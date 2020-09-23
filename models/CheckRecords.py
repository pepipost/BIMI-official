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
            if dmarc['tags']['p']['value'] == "none":
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
                if re.search(regex_cert, bimiRecord['record']):
                    bimiRecord['svg'] = (bimiRecord['record'].split('l=')[1]).split('.svg')[0]+'.svg'
                    bimiRecord['vmc'] = (bimiRecord['record'].split('a=')[1]).split('.pem')[0]+'.pem'
                    bimiRecord['status'] = True
                elif re.search(regex_without_cert, bimiRecord['record']):
                    bimiRecord['svg'] = (bimiRecord['record'].split('l=')[1]).split('.svg')[0]+'.svg'
                    bimiRecord['vmc'] = ""
                    bimiRecord['status'] = True
                    
                    if bimiRecord['record'].find("a=") !=-1:
                        pem_string = bimiRecord['record'].split("a=")[1]
                        pem_string = pem_string.replace(" ","")
                        if pem_string.find(";") != -1:
                            pem_string = pem_string.split(';')[0]
                            print(pem_string)
                            if len(pem_string) > 0:
                                bimiRecord['errors'].append("BIMI record has an invalid a= record format. The linked file must be .pem file or empty record a=;")
                                bimiRecord['status'] = False
                        else:
                            if len(pem_string) > 0:
                                bimiRecord['errors'].append("BIMI record has an invalid a= record format. The linked file must be .pem file or empty record a=;")
                                bimiRecord['status'] = False
                else:
                    bimiRecord['status'] = False
                    bimiRecord['svg'] = ""
                    bimiRecord['vmc'] = ""
                    bimiRecord['errors'].append("BIMI has an invalid format: Correct format : v=BIMI1; l=https://"+self.domain+"/svg-file-path/logo-image.svg; a=https://"+self.domain+"/pem-certificate-path/file.pem. \n Pem certificate being optional currently")
        except Exception as e:
            print("Error in executing DNS Resolver for BIMI DKIM Check. Error: ", e)
            bimiRecord['status'] = False
            bimiRecord['svg'] = ""
            bimiRecord['vmc'] = ""
            bimiRecord['errors'].append("Error with bimi dns check."+str(e))
        return bimiRecord

    def get_dns_details(self):
        dnsRecords = self.getDnsTXT()
        # return dnsRecords
        mxRecord = self.get_mx(dnsRecords['mx'])
        spfRecord = self.get_spf(dnsRecords['spf'])
        dmarcRecord = self.get_dmarc(dnsRecords['dmarc'])
        bimiRecord = self.get_bimi()
        response = {"mx":mxRecord, "spf":spfRecord, "dmarc":dmarcRecord, "bimi": bimiRecord}
        return response


