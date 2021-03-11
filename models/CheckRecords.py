import json
# import subprocess
# import dns.resolver
import checkdmarc
import re
from pprint import pprint

class CheckRecords:
    def __init__(self,domain):
        self.domain = domain

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
        regex_pct = r"pct=(100|[1-9][0-9]|[1-9])"
        dmarcRecord = {"status": "", "record": "","warnings":[],"errors":[]}
        if dmarc['record'] in (None, ''):
            dmarcRecord['status'] = False
        else:
            dmarcRecord['status'] = dmarc['valid']
            searchpct = re.search(regex_pct, dmarc['record'])
            if dmarc['record'].find('p=quarantine')==-1 and dmarc['record'].find('p=reject')==-1:
                dmarcRecord['status'] = False
                dmarcRecord['errors'] = ["dmarc policy should be set to p=quarantine or p=reject for BIMI to work"]
            if searchpct and int(searchpct.group(0).split("=")[1]) != 100:
                dmarcRecord['status'] = False
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
        bimiRecord = {"status": "", "record": "","errors":[], "warnings":[] ,"svg":""}
        # regex_cert = r"v=BIMI1;(| )l=((.*):\/\/.*);(| )a=((.*):\/\/(.*.pem))"
        regex_cert = r"v=BIMI1;(?=.*(l=((.*):\/\/(.*.svg|.*.SVG)))\b)(?=.*(a=((.*):\/\/(.*.pem|.*.PEM)))\b).*(;$| |$)"
        # regex_without_cert = r"v=BIMI1;\s+(| )l=((.*):\/\/.*)(;| |)"
        regex_without_cert = r"v=BIMI1;(|\s+)l=((.*):\/\/(.*.svg|.*.SVG))(;| |).*"
        try:
            bimi_data = checkdmarc.query_bimi_record(self.domain, selector='default', nameservers=None, timeout=4.0)
            # print(bimi_data)
            bimiRecord['record'] = bimi_data['record']
            if re.search(regex_cert, bimiRecord['record']):
                print("Bimi Record is with pem certificate")
                bimiRecord['status'] = True
                if (".SVG" in bimiRecord['record']):
                    bimiRecord['svg'] = (bimiRecord['record'].split('l=')[1]).split('.SVG')[0]+'.SVG'
                elif (".svg" in bimiRecord['record']):
                    bimiRecord['svg'] = (bimiRecord['record'].split('l=')[1]).split('.svg')[0]+'.svg'
                else:
                    bimiRecord['status'] = False
                    bimiRecord['errors'].append("BIMI record doesn't have a .svg image")
                
                if (".PEM" in bimiRecord['record']):
                    bimiRecord['vmc'] = (bimiRecord['record'].split('a=')[1]).split('.PEM')[0]+'.PEM'
                elif (".pem" in bimiRecord['record']):
                    bimiRecord['vmc'] = (bimiRecord['record'].split('a=')[1]).split('.pem')[0]+'.pem'
                
                if(len(bimi_data['warnings'])) > 0:
                    bimi_data['warnings'] += bimi_data['warnings']
                    bimiRecord['status'] = False

            elif re.search(regex_without_cert, bimiRecord['record']):
                print("Bimi Record is without pem certificate")
                bimiRecord['status'] = True

                if ("SVG" in bimiRecord['record']):
                    bimiRecord['svg'] = (bimiRecord['record'].split('l=')[1]).split('.SVG')[0]+'.SVG'
                elif ("svg" in bimiRecord['record']):
                    bimiRecord['svg'] = (bimiRecord['record'].split('l=')[1]).split('.svg')[0]+'.svg'
                else:
                    bimiRecord['status'] = False
                    bimiRecord['errors'].append("BIMI record doesn't have a .svg image")

                bimiRecord['vmc'] = ""

                if(len(bimi_data['warnings'])) > 0:
                    bimiRecord['status'] = False

                if bimiRecord['record'].find("a=") !=-1:
                    pem_string = bimiRecord['record'].split("a=")[1]
                    pem_string = pem_string.replace(" ","")
                    pem_string = pem_string.replace("\"","")
                    if pem_string.find(";") != -1:
                        pem_string = pem_string.split(';')[0]
                        if len(pem_string) > 0:
                            bimiRecord['errors'].append("BIMI record has an invalid a= record format. The linked file must be .pem file or empty record a=;")
                            bimiRecord['status'] = False
                    else:
                        if len(pem_string) > 0:
                            bimiRecord['errors'].append("BIMI record has an invalid a= record format. The linked file must be .pem file or empty record a=;")
                            bimiRecord['status'] = False
                bimiRecord['errors'] += bimi_data['warnings']
            else:
                print("Bimi Record is Invalid")
                bimiRecord['status'] = False
                bimiRecord['svg'] = ""
                bimiRecord['vmc'] = ""
                bimiRecord['errors'].append("BIMI has an invalid format: Correct format : v=BIMI1; l=https://"+self.domain+"/svg-file-path/logo-image.svg; a=https://"+self.domain+"/pem-certificate-path/file.pem. \n Pem certificate being optional currently.")
                bimiRecord['errors'] += bimi_data['warnings']
        except Exception as e:
            print("Error in executing DNS Resolver for BIMI DKIM Check. Error: ", e)
            bimiRecord['status'] = False
            bimiRecord['svg'] = ""
            bimiRecord['vmc'] = ""
            bimiRecord['errors'].append("Error with bimi dns check. "+str(e))
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


