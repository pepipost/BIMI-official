from flask_restful import Resource,request
import json
import subprocess
import dns.resolver
import re
# from pprint import pprint

class CheckRecords(Resource):
    def __init__(self,domain):
        self.domain = domain

    def getDnsTXT(self):
         # Check SPF DMARC MX from TXT record
        try:
            result = subprocess.run(['checkdmarc', self.domain], stdout=subprocess.PIPE)
            complied_dict = json.loads(result.stdout)
            return complied_dict
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
        dmarcRecord = {"status": "", "record": "","warnings":[],"errors":[]}
        if dmarc['record'] in (None, ''):
            dmarcRecord['status'] = False
        else:
            if dmarc['record'].find("p=none") != -1:
                dmarcRecord['status'] = False
                dmarcRecord['errors'] = ["dmarc policy should be set to p=quarantine or p=reject for BIMI to work"]
                dmarcRecord['record'] = dmarc['record']
            else:
                dmarcRecord['status'] = dmarc['valid']
                dmarcRecord['record'] = dmarc['record']
        dmarcRecord['errors'] += [dmarc['error']] if 'error' in dmarc else []
        dmarcRecord['warnings'] += dmarc['warnings'] if 'warnings' in dmarc else []
        return dmarcRecord

    # EXCLUDED
    def get_dkim(self):
        # DKIM CHECK
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

    def get_bimi(self):
        # BIMI CHECK
        bimiRecord = {"status": "", "record": "","errors":[], "warnings":[] ,"svg":""}
        regex_cert = r"v=BIMI1;(| )l=((.*):\/\/.*);(| )a=((.*):\/\/(.*.pem))"
        regex_without_cert = r"v=BIMI1;(| )l=((.*):\/\/.*)(;| |)"
        try:
            dkim_data = dns.resolver.query('default._bimi.'+self.domain, 'TXT')
            for i in dkim_data.response.answer:
                for j in i.items:
                    bimiRecord['record'] = j.to_text()
                bimi_str = bimiRecord['record']
                if re.search(regex_cert, bimi_str):
                    bimiRecord['svg'] = (bimiRecord['record'].split('l=')[1]).split('.svg')[0]+'.svg'
                    bimiRecord['status'] = True
                elif re.search(regex_without_cert, bimi_str):
                    bimiRecord['svg'] = (bimiRecord['record'].split('l=')[1]).split('.svg')[0]+'.svg'
                    bimiRecord['status'] = True
                else:
                    bimiRecord['status'] = False
                    bimiRecord['svg'] = ""
                    bimiRecord['errors'].append("BIMI has an invalid format: Correct format : v=BIMI1; l=https://amplify.valimail.com/bimi/time-warner/LysAFUdG-Hw-cnn_vmc.svg; a=https://amplify.valimail.com/bimi/time-warner/LysAFUdG-Hw-cnn_vmc.pem")
        except Exception as e:
            print("Error in executing DNS Resolver for BIMI DKIM Check. Error: ", e)
            bimiRecord['status'] = False
            bimiRecord['svg'] = ""
            bimiRecord['errors'].append("Error with bimi dns check."+str(e))

        return bimiRecord

    def validate_bimi(self, record):
        # dmarc_list = dmarc['record'].split(";")
            # for dmarc_string in dmarc_list:
            # subrecord = dmarc_string.split("=")
        if 'v=BIMI1' not in record:
            return {"valid": False, "response": {"errors": ["Invalid BIMI Record Found"], "warnings": []}}
        return {"valid": True, "response": {"errors": [], "warnings":[]}}

    def get_dns_details(self):
        dnsRecords = self.getDnsTXT()
        # return dnsRecords
        mxRecord = self.get_mx(dnsRecords['mx'])
        spfRecord = self.get_spf(dnsRecords['spf'])
        dmarcRecord = self.get_dmarc(dnsRecords['dmarc'])
        bimiRecord = self.get_bimi()
        response = {"mx":mxRecord, "spf":spfRecord, "dmarc":dmarcRecord, "bimi": bimiRecord}
        return response
