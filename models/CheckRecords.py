from flask_restful import Resource,request
import json
import subprocess
import dns.resolver
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
            # dmarc_list = dmarc['record'].split(";")
            # for dmarc_string in dmarc_list:
            #     subrecord = dmarc_string.split("=")
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
        try:
            dkim_data = dns.resolver.query('default._bimi.'+self.domain, 'TXT')
            for i in dkim_data.response.answer:
                for j in i.items:
                    print(j.to_text())
                    bimiRecord['record'] = j.to_text()
            if bimiRecord['record'] in (None, ''):
                bimiRecord['status'] = False
                bimiRecord['errors'] = ["No dkim record found for bimi"]
            else:
                bimi_validity = self.validate_bimi(bimiRecord['record'])
                if bimi_validity['valid']:
                    bimiRecord['status'] = True
                    bimiRecord['warnings'] = bimi_validity['response']['warnings']
                else:
                    bimiRecord['status'] = False
                    bimiRecord['errors'] = bimi_validity['response']['errors']
                bimiRecord['svg'] = (bimiRecord['record'].split('l=')[1]).split('.svg')[0]+'.svg'
        except Exception as e:
            print("Error in executing DNS Resolver for BIMI DKIM Check. Error: ", e)
            bimiRecord['status'] = False
            bimiRecord['errors'] = ["No dkim record found for bimi"]
        return bimiRecord

    def validate_bimi(self, record):
        if 'v=BIMI1' not in record:
            return {"valid": False, "response": {"errors": ["No BIMI record found"], "warnings": []}}
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
