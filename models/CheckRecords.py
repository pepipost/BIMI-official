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
            return {"valid": False, "response": "An invalid BIMI is set"}
        return {"valid": True, "response": "A valid BIMI record is set"}

    def certificate_validator(self, certificate_vmc):
        # CERTIFICATE VALIDATOR
        with open(certificate_vmc, 'rb') as f:
            end_entity_cert = f.read()
        try:
            validator = CertificateValidator(end_entity_cert)
            validator.validate_usage(set(['digital_signature']))
        except (errors.PathValidationError):
            print("Cannot verify certificate. Issue: %s",errors.PathValidationError)

    def get_dns_details(self, domain):
        # BIMI CHECK
        bimiRecord = {"status": "", "record": "","message":"","svg":""}
        try:
            dkim_data = dns.resolver.query('default._bimi.'+domain, 'TXT')
            for i in dkim_data.response.answer:
                print(i.to_text())
                for j in i.items:
                    print(j.to_text())
                    bimiRecord['record'] = j.to_text()

            if bimiRecord['record'] in (None, ''):
                bimiRecord['status'] = False
                bimiRecord['message'] = "No dkim record found for bimi"
            else:
                bimi_validity = self.validate_bimi(bimiRecord['record'])
                if bimi_validity['valid']:
                    bimiRecord['status'] = True
                    bimiRecord['message'] = bimi_validity['response']
                else:
                    bimiRecord['status'] = False
                    bimiRecord['message'] = bimi_validity['response']
                bimiRecord['svg'] = bimiRecord['record'].split('l=')[1]

        except Exception as e:
            print("error in executing DNS Resolver. Error: ", e)


        # Check sfp dmarc mx
        try:
            result = subprocess.run(['checkdmarc', domain], stdout=subprocess.PIPE)
            complied_dict = json.loads(result.stdout)
        except Exception as e:
            print("error in executing checkdmarc")


        # MX CHECK
        mxRecord = {"status": "", "records": [],"message":""}
        if  len(complied_dict['mx']['hosts']) == 0:
            mxRecord['status'] = False
            mxRecord['message'] = (complied_dict['mx']['warnings'] if 'warnings' in complied_dict['mx'] else "")
        else:
            for host in complied_dict['mx']['hosts']: 
                mxRecord['records'].append(host['hostname'])
                mxRecord['status'] = True
                mxRecord['message'] = complied_dict['mx']['warnings']

        # SPF CHECK
        spfRecord = {"status": "", "record": "","message":""}
        if  complied_dict['spf']['record'] in (None, ''):
            spfRecord['status'] = False
            spfRecord['message'] = complied_dict['spf']['error']
        else:
            spfRecord['status'] = complied_dict['spf']['valid']
            spfRecord['message'] = complied_dict['spf']['warnings'] if complied_dict['spf']['warnings'] else ""
            spfRecord['record'] = complied_dict['spf']['record']

        # DMARC CHECK
        dmarcRecord = {"status": "", "record": "","message":""}
        if complied_dict['dmarc']['record'] in (None, ''):
            dmarcRecord['status'] = False
            dmarcRecord['message'] = complied_dict['dmarc']['error']
        else:
            dmarcRecord['status'] = complied_dict['dmarc']['valid']
            dmarcRecord['message'] = complied_dict['dmarc']['warnings'] if complied_dict['spf']['warnings'] else ""
            dmarcRecord['record'] = complied_dict['dmarc']['record'] 

        response = {"mx":mxRecord, "spf":spfRecord, "dmarc":dmarcRecord, "bimi": bimiRecord}
        return response
