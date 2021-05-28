from flask_restful import Resource,request
import json
from models.CheckRecords import CheckRecords 
from models.CheckSvg import CheckSvg
from models.CheckVmc import CheckVmc
from models.GenerateBimi import GenerateBimi
from utils.Utils import Utils
from Config import Config
import tldextract
class GenerateBimiController(Resource):
    def __init__(self):
        self.Utils = Utils()
        self.svg_file_flag = False
        self.vmc_file_flag = False

    def post(self):
        content = request.form
        data = {"bimi":{},"dmarc":{},"mx":{},"spf":{},"svg_validation":{},"vmc_validation":{},"bimi_generation":{}}
        if "domain" not in content or content['domain'].strip() == "" :
            data['bimi']['record'] = None
            data['bimi']['status'] = False
            data['dmarc']['record'] = None
            data['dmarc']['status'] = False
            data['mx']['record'] = []
            data['mx']['status'] = False
            data['spf']['record'] = None
            data['spf']['status'] = False
            data['svg_validation']['svg_link'] = None
            data['svg_validation']['status'] = False
            data['vmc_validation']['recorvmc_linkd'] = None
            data['vmc_validation']['status'] = False
            data['bimi_generation']['status'] = False
            data['bimi_generation']['errors'] = ["Something went wrong"]
            data['bimi_generation']['record'] = None
            return data, 400

        user_agent = request.headers.get('User-Agent')

        # Check if the current domain has a bimi record set (In case of sub domains)
        CR = CheckRecords(content['domain'])
        bimi_data = CR.get_bimi()

        # print(bimi_data, "\n")

        # Try to extract parent domain in case the no record found was due to subdomain search
        maindomain = tldextract.extract(content['domain'], include_psl_private_domains=True).registered_domain
        if bimi_data['record'] == "" and maindomain != content['domain']:
            CR = CheckRecords(maindomain)
            data = CR.get_dns_details()
        else:
            data = CR.get_dns_details(bimi=bimi_data)

        if content['svg_link']!="":
            svg_link = content['svg_link']
            CS = CheckSvg(svg_link,user_agent)
        else:
            self.svg_file_flag = True
            svg_link = self.Utils.upload_request_file("svg_file", request, Config.STORAGE_SVG_DIR, self.svg_file_flag)
            if svg_link == "":
                return data, 400
            CS = CheckSvg(svg_link,user_agent,self.svg_file_flag)
        
        data['svg_validation'] = CS.check_svg()
            
        if content['vmc_link']!="":
            vmc_link = content['vmc_link']
            CV = CheckVmc(vmc_link,user_agent)
        else:
            self.vmc_file_flag = True
            vmc_link = self.Utils.upload_request_file("vmc_file", request, Config.STORAGE_CERT_DIR, self.vmc_file_flag)
            CV = CheckVmc(vmc_link,user_agent,self.vmc_file_flag)

        data['vmc_validation'] = CV.check_vmc()
        
        svg_generate_link = svg_link
        vmc_generate_link = vmc_link
        if self.svg_file_flag:
            svg_generate_link = self.Utils.svg_replace_file_link(content['domain'], svg_link)
        if self.vmc_file_flag:
            vmc_generate_link = self.Utils.vmc_replace_file_link(content['domain'], vmc_link)

        GB = GenerateBimi()
        data['bimi_generation'] = GB.generate_bimi(content['domain'], svg_generate_link, vmc_generate_link)
        data['bimi_generation']['svg_link'] = svg_generate_link
        data['bimi_generation']['vmc_link'] = vmc_generate_link

        if (data['svg_validation']['status'] and data['dmarc']['status'] and data['mx']['status'] and data['spf']['status'] and data['vmc_validation']['status']):
            data['bimi_generation']['status'] = True
        else:
            data['bimi_generation']['status'] = False
            data['bimi_generation']['errors'] = ["Your BIMI record is not compliant with the standard requirements. Please check the below report to understand what really went wrong."]
            # data['bimi_generation'] = {"status":False, "record":"", "message":"Some errors was found in your bimi check","errors":["Please fix the errors shown below to successfully generate BIMI record."], "svg_link":svg_generate_link, "vmc_link": vmc_generate_link}
        
        return data

        