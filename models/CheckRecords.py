import json
# import subprocess
# import dns.resolver
import checkdmarc
import re
from utils.Utils import Utils

class CheckRecords:
	def __init__(self,domain):
		self.domain = domain
		self.Utils = Utils()

	def getDnsTXT(self):
		# Check SPF DMARC MX from TXT record
		try:
			# result = subprocess.run(['checkdmarc', self.domain], stdout=subprocess.PIPE)
			# complied_dict = json.loads(result)
			result = checkdmarc.check_domains([self.domain],False,None,None,True,False,None,2.0,0.0)
			return result
		except Exception as e:
			print("error in executing checkdmarc. Error: ",e)

	def get_mx(self,mx):
		# MX CHECK
		mxRecord = {"status": "", "records": [],"warnings":[], "errors":[]}
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
	
	def get_spf(self, spf):
		# SPF CHECK
		spfRecord = {"status": "", "record": "","warnings":[], "errors":[]}
		if  spf['record'] in (None, ''):
			spfRecord['status'] = False
		else:
			spfRecord['status'] = spf['valid']
			spfRecord['record'] = spf['record']
		spfRecord['errors'] += [spf['error']] if 'error' in spf else []
		spfRecord['warnings'] += spf['warnings'] if 'warnings' in spf else [] 
		return spfRecord

	def get_dmarc(self, dmarc):
		# DMARC CHECK
		subdomainPolicy = None
		policy = None
		pct = 100
		dmarcRecord = {"status": "", "record": "","warnings":[],"errors":[]}
		if dmarc['record'] in (None, ''):
			dmarcRecord['status'] = False
		else:
			dmarcRecord['status'] = dmarc['valid']
			dmarc['record_a'] = self.Utils.record_str_to_dict(dmarc['record'])
			print(dmarc['record_a'])
			# Set Policy
			if "p" in dmarc["record_a"]:
				policy = dmarc["record_a"]["p"]
				print("policy",policy)
			# Set SubdomainPolicy
			if "sp" in dmarc["record_a"]:
				subdomainPolicy = dmarc["record_a"]["sp"]
				print("sub policy",subdomainPolicy)
			# Set mail percentage
			if "pct" in dmarc["record_a"]:
				pct = int(dmarc["record_a"]["pct"].strip())
				print("pct",pct)    
			# BIMI strict policy checks
			if policy == "quarantine":
				if pct != 100:
					dmarcRecord['status'] = False
					dmarcRecord['errors'] = ["dmarc policy when set to p=quarantine, it is recommended to set pct=100 for BIMI to work"]
			elif policy == "reject":
				if pct == 0:
					dmarcRecord['status'] = False
					dmarcRecord['errors'] = ["dmarc policy when set to p=reject, it is recommended to set pct should be atleast > 0 for BIMI to work"]
			else:
				dmarcRecord['status'] = False
				dmarcRecord['errors'] = ["dmarc policy should be set to p=quarantine or p=reject for BIMI to work"]

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

	def get_bimi(self):
		# BIMI CHECK
		bimiRecord = {"status": "", "record": "","errors":[], "warnings":[] ,"svg":"","vmc":""}
		try:
			bimi_data = checkdmarc.query_bimi_record(self.domain, selector='default', nameservers=None, timeout=4.0)
			bimiRecord['record'] = bimi_data['record']
			bimiRecord['status'] = True
			records = self.Utils.record_str_to_dict(bimiRecord['record'])
			if (records['v'] == 'BIMI1'):
				if 'l' in records:
					bimiRecord['svg'] = records['l']
				if 'a' in records:
					bimiRecord['vmc'] = records['a']

				if (not bimiRecord['svg']):
					bimiRecord['errors'].append("BIMI record should have a mandatory l= record containing your brand svg logo url")
					bimiRecord['status'] = False
				elif (not bimiRecord['svg'].lower().split('?')[0].endswith('.svg')):
					bimiRecord['errors'].append("BIMI logo should be strictly a SVG file")
					bimiRecord['svg'] = ""
					bimiRecord['status'] = False

				if (bimiRecord['vmc']!=""):
					if (not bimiRecord['vmc'].lower().split('?')[0].endswith('.pem')):
						bimiRecord['errors'].append("BIMI certificate should be strictly a PEM file")
						bimiRecord['vmc'] = ""
						bimiRecord['status'] = False

			else:
				bimiRecord['errors'].append("BIMI record should have a strict bimi version identifier v=BIMI1 at the beginning of the record")
				bimiRecord['status'] = False
				bimiRecord['svg'] = ""
				bimiRecord['vmc'] = ""
				bimiRecord['errors'].append("BIMI has an invalid format: Correct format : v=BIMI1; l=https://"+self.domain+"/svg-file-path/logo-image.svg; a=https://"+self.domain+"/pem-certificate-path/file.pem. \n Pem certificate being optional currently.")
			bimiRecord['errors'] += [bimi_data['error']] if 'error' in bimi_data else []
			bimiRecord['warnings'] += bimi_data['warnings'] if 'warnings' in bimi_data else []
		except Exception as e:
			print("Error in executing DNS Resolver for BIMI DKIM Check. Error: ", e)
			bimiRecord['status'] = False
			bimiRecord['svg'] = ""
			bimiRecord['vmc'] = ""
			bimiRecord['errors'].append("Error with bimi dns check. "+str(e))
		return bimiRecord

	def get_dns_details(self, bimi=None):
		dnsRecords = self.getDnsTXT()
		# return dnsRecords
		mxRecord = self.get_mx(dnsRecords['mx'])
		spfRecord = self.get_spf(dnsRecords['spf'])
		dmarcRecord = self.get_dmarc(dnsRecords['dmarc'])
		if bimi == None:
			bimiRecord = self.get_bimi()
		else:
			bimiRecord = bimi
		response = {"mx":mxRecord, "spf":spfRecord, "dmarc":dmarcRecord, "bimi": bimiRecord}
		return response


