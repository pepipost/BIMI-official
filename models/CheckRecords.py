import json
# import subprocess
# import dns.resolver
import checkdmarc
import re
from utils.Utils import Utils
from collections import OrderedDict
import tldextract

class CheckRecords:
	def __init__(self,domain):
		self.approved_nameservers = None
		self.approved_mx_hostnames = None
		self.skip_tls = True
		self.include_dmarc_tag_descriptions = False
		self.nameservers = None
		self.timeout = 2.0
		self.parked = False
		# self.wait=0.0
		self.Utils = Utils()
		self.domain_results = {}
		self.domain = domain.rstrip(".\r\n").strip().lower()
		self.base_domain  = checkdmarc.get_base_domain(self.domain)
		# self.mxRecord = {"status": "", "records": [],"warnings":[], "errors":[]}
		# self.spfRecord = {"status": "", "records": [],"warnings":[], "errors":[]}
		# self.dmarcRecord = {"status": "", "record": "","warnings":[],"errors":[]}
		# self.bimiRecord = {"status": "", "record": "","errors":[], "warnings":[] ,"svg":"","vmc":""}

	def fetchNs(self):
		result = {}
		try:
			result = checkdmarc.get_nameservers(
			self.domain,
			approved_nameservers=self.approved_nameservers,
			nameservers=self.nameservers,
			timeout=self.timeout)
		except checkdmarc.DNSException as error:
			result = OrderedDict([("hostnames", []),
				("error", error.__str__())])
		return result

	def fetchMx(self):
		result = {}
		try:
			result = checkdmarc.get_mx_hosts(
				self.domain,
				skip_tls=self.skip_tls,
				approved_hostnames=self.approved_mx_hostnames,
				nameservers=self.nameservers,
				timeout=self.timeout)

		except checkdmarc.DNSException as error:
			result = OrderedDict([("hosts", []),
				("error", error.__str__())])
		return result

	def fetchSpf(self):
		result = OrderedDict([("record", ''), ("valid", True), ("dns_lookups", None)])
		try:
			spf_query = checkdmarc.query_spf_record(
				self.domain,
				nameservers=self.nameservers,
				timeout=self.timeout)
			result["record"] = spf_query["record"]
			result["warnings"] = spf_query["warnings"]
			parsed_spf = checkdmarc.parse_spf_record(result["record"],
				self.domain,
				parked=self.parked,
				nameservers=self.nameservers,
				timeout=self.timeout)

			result["dns_lookups"] = parsed_spf["dns_lookups"]

			result["parsed"] = parsed_spf["parsed"]
			result["warnings"] += parsed_spf["warnings"]
		except checkdmarc.SPFError as error:
			# Incase of exception records are blank, so fetching it again
			"""
			if not result["record"]:
				records = []
				records = self.queryRecords()
				for record in records:
					if record.startswith("v=spf1"):
						result["record"]+=record+'\n'
			"""
			result["error"] = str(error)
			del result["dns_lookups"]
			result["valid"] = False
			if hasattr(error, "data") and error.data:
				for key in error.data:
					result[key] = error.data[key]
		return result

	def queryRecords(self):
		try:
			return checkdmarc._query_dns(self.domain, "TXT")
		except Exception as e:
			return ''
			
	def fetchDmarc(self):
		result = OrderedDict([("record", None),
			("valid", True),
			("location", None)])
		try:
			dmarc_query = checkdmarc.query_dmarc_record(self.domain,
				nameservers=self.nameservers,
				timeout=self.timeout)
			result["record"] = dmarc_query["record"]
			result["location"] = dmarc_query["location"]
			parsed_dmarc_record = checkdmarc.parse_dmarc_record(
				dmarc_query["record"],
				dmarc_query["location"],
				parked=self.parked,
				include_tag_descriptions=self.include_dmarc_tag_descriptions,
				nameservers=self.nameservers,
				timeout=self.timeout)
			result["warnings"] = dmarc_query["warnings"]

			result["tags"] = parsed_dmarc_record["tags"]
			result["warnings"] += parsed_dmarc_record[
			"warnings"]
		except checkdmarc.DMARCError as error:
			result["error"] = str(error)
			result["valid"] = False
			if hasattr(error, "data") and error.data:
				for key in error.data:
					result[key] = error.data[key]
		return result

	def get_mx(self, mx, chk=None):
		# MX CHECK
		mxRecord = {"status": "", "records": [], "warnings":[], "errors":[], "domain":self.domain, "precheck":chk}
		if  len(mx['hosts']) == 0:
			mxRecord['status'] = False
		else:
			for host in mx['hosts']:
				mxRecord['records'].append(host['hostname'])
				mxRecord['status'] = True
				if host['hostname']=="" or host['hostname']==None:
					mxRecord['status'] = False
					mxRecord['errors'] = ["No Mx Rerod Found"]
					mxRecord['records'] = []
		mxRecord['errors'] += [mx['error']] if 'error' in mx else []
		mxRecord['warnings'] += mx['warnings'] if 'warnings' in mx else []
		return mxRecord
	
	def get_spf(self, spf, chk=None):
		# SPF CHECK
		spfRecord = {"status": "", "records": [], "warnings":[], "errors":[], "domain":self.domain, "precheck":chk, "note": False}
		if  spf['record'] in (None, ''):
			spfRecord['status'] = False
		else:
			spfRecord['status'] = spf['valid']
			spfRecord['record'] = spf['record']
			if self.Utils.detect_spf_macros(spf_record = spf['record']):
				spfRecord['note'] = "The SPF checks might not be completely reliable since there are some dynamic records in your SPF record."
		spfRecord['errors'] += [spf['error']] if 'error' in spf else []
		spfRecord['warnings'] += spf['warnings'] if 'warnings' in spf else []
		return spfRecord

	def get_dmarc(self, dmarc, chk=None, setrecord=True):
		# DMARC CHECK
		dmarcRecord = {"status": "", "record": "","warnings":[], "errors":[], "domain":self.domain, "precheck":chk}
		subdomainPolicy = None
		policy = None
		pct = 100
		if dmarc['record'] in (None, ''):
			if chk != None:
				dmarcRecord['errors'] += ["DMARC policy needs to be set for your root domain for BIMI to work."]
			dmarcRecord['status'] = False
		else:
			dmarcRecord['status'] = dmarc['valid']
			dmarc['record_a'] = self.Utils.record_str_to_dict(dmarc['record'])
			# Set Policy
			if "p" in dmarc["record_a"]:
				policy = dmarc["record_a"]["p"]
			# Set SubdomainPolicy
			if "sp" in dmarc["record_a"]:
				subdomainPolicy = dmarc["record_a"]["sp"]
			# Set mail percentage
			if "pct" in dmarc["record_a"]:
				pct = int(dmarc["record_a"]["pct"].strip())

			# BIMI strict policy checks
			if policy == "quarantine":
				if pct != 100:
					dmarcRecord['status'] = False
					dmarcRecord['errors'] += ["dmarc policy when set to p=quarantine, it is recommended to set pct=100 for BIMI to work"]
			elif policy == "reject":
				if pct == 0:
					dmarcRecord['status'] = False
					dmarcRecord['errors'] += ["dmarc policy when set to p=reject, it is recommended to set pct should be atleast > 0 for BIMI to work"]
			else:
				dmarcRecord['status'] = False
				dmarcRecord['errors'] += ["dmarc policy should be set to p=quarantine or p=reject for BIMI to work"]

			if subdomainPolicy and subdomainPolicy == "none":
				dmarcRecord['status'] = False
				dmarcRecord['errors'] += ["dmarc sub domain policy sp should be set to either reject or quarantine for BIMI to work"]

		if setrecord==True:
			dmarcRecord['record'] = dmarc['record']

		dmarcRecord['errors'] += [dmarc['error']] if 'error' in dmarc else []
		dmarcRecord['warnings'] += dmarc['warnings'] if 'warnings' in dmarc else []
		return dmarcRecord

	# EXCLUDED
	# DKIM CHECK
	"""    
	def get_dkim(self):
			dkimrecord = {"status": "", "record": "","warnings":""}
			try:
				dkim_data = dns.resolver.query('default._domainkey.'+self.domain, 'TXT')
				for i in dkim_data.response.answer:
					print(i.to_text())
					for j in i.items:
						# print(j.to_text())
						dkimrecord['record'] = j.to_text()
			except Exception as e:
				print("error in executing dns resolver for dmarc record. Error: ",e)
	"""

	def get_bimi(self, setrecord=True, chk=None):
		# BIMI CHECK
		bimiRecord = {"status": "", "record": "", "errors":[], "warnings":[], "svg":"", "vmc":"", "domain":self.domain, "precheck":chk}
		# regex_cert = r"v=BIMI1;(| )l=((.*):\/\/.*);(| )a=((.*):\/\/(.*.pem))"
		regex_cert = r"v=bimi1;(?=.*(l=((.*):\/\/(.*.svg)))\b)(?=.*(a=((.*):\/\/(.*.pem)))\b).*(;$| |$)"
		# regex_without_cert = r"v=BIMI1;\s+(| )l=((.*):\/\/.*)(;| |)"
		regex_without_cert = r"v=bimi1;(|\s+)l=((.*):\/\/(.*.svg))(;| |).*"
		try:
			bimi_data = checkdmarc.query_bimi_record(self.domain, selector='default', nameservers=None, timeout=4.0)
			if setrecord == True:
				bimiRecord['record'] = bimi_data['record']
			bimiRecord['status'] = True
			if bimi_data['record'] in (None, ''):
				bimiRecord['status'] = False
				bimiRecord['errors'].append("BIMI Record not found. BIMI record should be set for BIMI to work in the following format : v=BIMI1; l=https://"+self.domain+"/svg-file-path/logo-image.svg; a=https://"+self.domain+"/vmc-certificate-path/file.pem. \n Vmc certificate currently being optional.")
			else:
				if (re.search(regex_cert, bimiRecord['record'].lower()) or re.search(regex_without_cert, bimiRecord['record'].lower())):
					records = self.Utils.record_str_to_dict(bimi_data['record'])
					if 'l' in records:
						bimiRecord['svg'] = records['l']
					if 'a' in records:
						bimiRecord['vmc'] = records['a']

					if (not bimiRecord['svg']):
						bimiRecord['errors'].append("BIMI record should have a mandatory l= record containing your brand svg logo url")
						bimiRecord['status'] = False
					elif (not bimiRecord['svg'].lower().split('?')[0].endswith('.svg')):
						bimiRecord['errors'].append("BIMI logo should be strictly a SVG file, check your bimi record's \"l=\" parameter.")
						bimiRecord['svg'] = ""
						bimiRecord['status'] = False

					if (bimiRecord['vmc']!=""):
						if (not bimiRecord['vmc'].lower().split('?')[0].endswith('.pem')):
							bimiRecord['errors'].append("BIMI vmc certificate should be strictly a PEM file, check your bimi record's \"a=\" parameter.")
							bimiRecord['vmc'] = ""
							bimiRecord['status'] = False
				else:
					bimiRecord['errors'].append("BIMI has an invalid format: Correct format : v=BIMI1; l=https://"+self.domain+"/svg-file-path/logo-image.svg; a=https://"+self.domain+"/vmc-certificate-path/file.pem. \n Vmc certificate currently being optional.")
					bimiRecord['status'] = False
					bimiRecord['svg'] = ""
					bimiRecord['vmc'] = ""
			# Suppression of bimi error in case of bimi pass in main domain
			if chk!=None and bimiRecord['status'] == True:
				chk.pop('warnings', None)
				chk.pop('errors', None)

			bimiRecord['errors'] += [bimi_data['error']] if 'error' in bimi_data else []
			bimiRecord['warnings'] += bimi_data['warnings'] if 'warnings' in bimi_data else []
		except Exception as e:
			print("Error in executing DNS Resolver for BIMI DKIM Check. Error: ", e)
			bimiRecord['status'] = False
			bimiRecord['svg'] = ""
			bimiRecord['vmc'] = ""
			bimiRecord['errors'].append("Error with bimi dns check. "+str(e))
		return bimiRecord

	# def get_dns_details(self, bimi=None):
	# 	dnsRecords = self.getDnsTXT()
	# 	# return dnsRecords
	# 	mxRecord = self.get_mx(dnsRecords['mx'])
	# 	spfRecord = self.get_spf(dnsRecords['spf'])
	# 	dmarcRecord = self.get_dmarc(dnsRecords['dmarc'])
	# 	if bimi == None:
	# 		bimiRecord = self.get_bimi()
	# 	else:
	# 		bimiRecord = bimi
	# 	response = {"mx":mxRecord, "spf":spfRecord, "dmarc":dmarcRecord, "bimi": bimiRecord}
	# 	return response


	def get_dns_details(self, bimi=None):
		# return dnsRecords
		mxRecord = self.get_mx(self.fetchMx())
		spfRecord = self.get_spf(self.fetchSpf())
		dmarcRecord = self.get_dmarc(self.fetchDmarc())
		bimiRecord = self.get_bimi()
		# Check for main domain if provided domain is a subdomain
		maindomain = tldextract.extract(self.domain, include_psl_private_domains=True).registered_domain
		if maindomain != self.domain:
			prevDomain = self.domain
			self.domain = maindomain
			if bimiRecord['status']:
				dmarcRecord = self.get_dmarc(self.fetchDmarc(),chk={'domain':prevDomain,'status':dmarcRecord['status']})
			else:
				# mxRecord = self.get_mx(self.fetchMx(),chk={prevDomain:mxRecord['status']})
				# spfRecord = self.get_spf(self.fetchSpf(),chk={prevDomain:spfRecord['status']})
				dmarcRecord = self.get_dmarc(self.fetchDmarc(),chk={'domain':prevDomain,'status':dmarcRecord['status']})
				bimiRecord = self.get_bimi(chk={'domain':prevDomain,'status':bimiRecord['status'],'warnings':bimiRecord['warnings'],'errors':bimiRecord['errors']})
		response = {"mx":mxRecord, "spf":spfRecord, "dmarc":dmarcRecord, "bimi": bimiRecord}
		return response

