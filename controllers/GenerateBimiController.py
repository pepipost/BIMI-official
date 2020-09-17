from flask_restful import Resource,request
import json
from models.CheckRecords import CheckRecords 
from models.CheckSvg import CheckSvg
from models.CheckVmc import CheckVmc
from models.GenerateBimi import GenerateBimi
from utils.Utils import Utils
from Config import Config
class GenerateBimiController(Resource):
    def __init__(self):
        self.Utils = Utils()
        self.svg_file_flag = False
        self.vmc_file_flag = False

    def post(self):
        content = request.form
        CR = CheckRecords(content['domain'])
        data = CR.get_dns_details()

        if content['svg_link']!="":
            svg_link = content['svg_link']
            CS = CheckSvg(svg_link)
        else:
            self.svg_file_flag = True
            svg_link = self.Utils.upload_request_file("svg_file", request, Config.STORAGE_SVG_DIR, self.svg_file_flag)
            CS = CheckSvg(svg_link,self.svg_file_flag)
        
        data['svg_validation'] = CS.check_svg()
            
        if content['vmc_link']!="":
            vmc_link = content['vmc_link']
            CV = CheckVmc(vmc_link)
        else:
            self.vmc_file_flag = True
            vmc_link = self.Utils.upload_request_file("vmc_file", request, Config.STORAGE_CERT_DIR, self.vmc_file_flag)
            CV = CheckVmc(vmc_link,self.vmc_file_flag)

        data['vmc_validation'] = CV.check_vmc()
        
        svg_generate_link = svg_link
        vmc_generate_link = vmc_link
        if self.svg_file_flag:
            svg_generate_link = self.Utils.svg_replace_file_link(content['domain'], svg_link)
        if self.vmc_file_flag:
            vmc_generate_link = self.Utils.vmc_replace_file_link(content['domain'], vmc_link)

        if (data['svg_validation']['status'] and data['dmarc']['status'] and data['mx']['status'] and data['spf']['status'] and data['vmc_validation']['status']):
            GB = GenerateBimi()
            data['bimi_generation'] = GB.generate_bimi(content['domain'], svg_generate_link, vmc_generate_link)
            data['bimi_generation']['svg_link'] = svg_generate_link
            data['bimi_generation']['vmc_link'] = vmc_generate_link
        else:
            data['bimi_generation'] = {"status":False, "record":"", "message":"Some errors was found in your bimi check","errors":["Please fix the errors shown below to successfully generate BIMI record."], "svg_link":svg_generate_link, "vmc_link": vmc_generate_link}
        
        return data

        