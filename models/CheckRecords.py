from flask_restful import Resource,request
import json
import subprocess
import dns.resolver
from pprint import pprint
from lxml import etree
import xml.etree.cElementTree as et
# from io import StringIO
# import dkim
from certvalidator import CertificateValidator, errors

class CheckRecords(Resource):
    RNG_SCHEMA_FILE = "svg_schema/relaxng.rng.xml"
    # CHECK SVG TAG
    def is_svg_extension(self, file):
        if file.endswith('.svg') or file.endswith('.SVG'):
            return True
        else:
            return False

    def is_svg_xml(self, filename):
        tag = None
        with open(filename, "r") as f:
            try:
                for event, el in et.iterparse(f, ('start',)):
                    tag = el.tag
                    break
            except et.ParseError:
                pass
        return tag == '{http://www.w3.org/2000/svg}svg'

    def check_svg(self, file_svg):
        if self.is_svg_extension(file_svg):
            if self.is_svg_xml(file_svg):
                return "Valid SVG"
                # if self.is_svg_schema(file_svg):
                #     return "Valid SVG file"
                # else:
                #     return "Invalid SVG Schema"
            else:
                return "Invalid SVG"
        else:
            return "Not an SVG extension"

    def chec_svg_schema(self, file_svg):
        with open(self.RNG_SCHEMA_FILE) as f:
            relaxng_doc = etree.parse(f)
        
        relaxng = etree.RelaxNG(relaxng_doc)

        with open(file_svg) as valid:
            doc = etree.parse(valid)
        return relaxng.validate(doc)

        """f = StringIO('''\
                        <element name="a" xmlns="http://relaxng.org/ns/structure/1.0">
                        <zeroOrMore>
                            <element name="b">
                            <text />
                            </element>
                        </zeroOrMore>
                        </element>
                    ''')
        relaxng_doc = etree.parse(f)
        relaxng = etree.RelaxNG(relaxng_doc)

        with open(file_svg) as svg:
            doc = etree.parse(svg)
        relaxng.validate(doc)"""

    def validate_bimi(self, record):
        if 'v=BIMI1' not in record:
            return {"valid": False, "response": {"errors": ["No BIMI record found"], "warnings": []}}
        return {"valid": True, "response": {"errors": [], "warnings":[]}}

    def certificate_validator(self, certificate_vmc):
        # CERTIFICATE VALIDATOR
        with open(certificate_vmc, 'rb') as f:
            end_entity_cert = f.read()
        try:
            validator = CertificateValidator(end_entity_cert)
            return validator.validate_usage(set(['digital_signature']))
        except (errors.PathValidationError):
            print("Cannot verify certificate. Issue: %s",errors.PathValidationError)

    def get_dns_details(self, domain):
        # BIMI CHECK
        bimiRecord = {"status": "", "record": "","errors":[], "warnings":[] ,"svg":""}
        try:
            dkim_data = dns.resolver.query('default._bimi.'+domain, 'TXT')
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
            print("Error in executing DNS Resolver. Error: ", e)
            bimiRecord['status'] = False
            bimiRecord['errors'] = ["No dkim record found for bimi"]
       
        # Check sfp dmarc mx
        try:
            result = subprocess.run(['checkdmarc', domain], stdout=subprocess.PIPE)
            complied_dict = json.loads(result.stdout)
            # return complied_dict
        except Exception as e:
            print("error in executing checkdmarc. Error: ",e)

        # MX CHECK
        mxRecord = {"status": "", "records": [],"warnings":[], "errors":[]}
        if  len(complied_dict['mx']['hosts']) == 0:
            mxRecord['status'] = False
            mxRecord['errors'] = [(complied_dict['mx']['error'] if 'error' in complied_dict['mx'] else None)]
            mxRecord['warnings'] = (complied_dict['mx']['warnings'] if 'warnings' in complied_dict['mx'] else [])
        else:
            for host in complied_dict['mx']['hosts']: 
                mxRecord['records'].append(host['hostname'])
                mxRecord['status'] = True
                mxRecord['errors'] = [(complied_dict['mx']['error'] if 'error' in complied_dict['mx'] else None)]
                if host['hostname']=="" or host['hostname']==None:
                    mxRecord['status'] = False
                    mxRecord['errors'] = ["No Mx Rerod Found"]
                mxRecord['warnings'] = (complied_dict['mx']['warnings'] if 'warnings' in complied_dict['mx'] else [])
                

        # SPF CHECK
        spfRecord = {"status": "", "record": "","warnings":[], "errors":""}
        if  complied_dict['spf']['record'] in (None, ''):
            spfRecord['status'] = False
            spfRecord['errors'] = [(complied_dict['spf']['error'] if 'error' in complied_dict['spf'] else None)]
            spfRecord['warnings'] = (complied_dict['spf']['warnings'] if 'warnings' in complied_dict['spf'] else [])
            
        else:
            spfRecord['status'] = complied_dict['spf']['valid']
            spfRecord['errors'] = [(complied_dict['spf']['error'] if 'error' in complied_dict['spf'] else None)]
            spfRecord['warnings'] = (complied_dict['spf']['warnings'] if 'warnings' in complied_dict['spf'] else [])
            spfRecord['record'] = complied_dict['spf']['record']

        # # DKIM CHECK
        # dkimrecord = {"status": "", "record": "","message":""}
        # try:
        #     dkim_data = dns.resolver.query('default._domainkey.'+domain, 'TXT')
        #     for i in dkim_data.response.answer:
        #         print(i.to_text())
        #         for j in i.items:
        #             # print(j.to_text())
        #             dkimrecord['record'] = j.to_text()
        # except Exception as e:
        #     print("error in executing dns resolver for dmarc record. Error: ",e)

        # DMARC CHECK
        dmarcRecord = {"status": "", "record": "","message":[],"errors":[]}
        if complied_dict['dmarc']['record'] in (None, ''):
            dmarcRecord['status'] = False
            dmarcRecord['errors'] = [(complied_dict['dmarc']['error'] if 'error' in complied_dict['dmarc'] else None)]
            dmarcRecord['warnings'] = (complied_dict['dmarc']['warnings'] if 'warnings' in complied_dict['dmarc'] else [])
        elif complied_dict['dmarc']['record'].find("p=none") != -1:
            dmarcRecord['status'] = False
            dmarcRecord['errors'] = ["dmarc policy should be set to p=quarantine or p=reject for BIMI to work"]
            dmarcRecord['warnings'] = (complied_dict['dmarc']['warnings'] if 'warnings' in complied_dict['dmarc'] else [])
            dmarcRecord['record'] = complied_dict['dmarc']['record']
        else:
            dmarcRecord['status'] = complied_dict['dmarc']['valid']
            dmarcRecord['errors'] = [(complied_dict['dmarc']['error'] if 'error' in complied_dict['dmarc'] else None)]
            dmarcRecord['warnings'] = (complied_dict['dmarc']['warnings'] if 'warnings' in complied_dict['dmarc'] else [])
            dmarcRecord['record'] = complied_dict['dmarc']['record']

        response = {"mx":mxRecord, "spf":spfRecord, "dmarc":dmarcRecord, "bimi": bimiRecord}
        return response
