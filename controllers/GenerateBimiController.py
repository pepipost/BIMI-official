from flask_restful import Resource,request
import json
from models.CheckRecords import CheckRecords 
from models.CheckSvg import CheckSvg
from models.GenerateBimi import GenerateBimi
class GenerateBimiController(Resource):
    def post(self):
        content = request.json
        CR = CheckRecords(content['domain'])
        data = CR.get_dns_details()

        if content['svg_link']!="":
            svg_link = content['svg_link']
            CS = CheckSvg(content['svg_link'])
        data['svg_validation'] = CS.check_svg()
        
        if content['vmc_link']:
            vmc_link = content['vmc_link']
        else:
            vmc_link = ""
            
        if (data['svg_validation']['status'] and data['dmarc']['status'] and data['mx']['status'] and data['spf']['status']):
            GB = GenerateBimi()
            data['bimi_generation'] = GB.generate_bimi(content['domain'], svg_link, vmc_link)
        else:
            data['bimi_generation'] = {"status":False, "record":"", "errors":"Some errors was found in your bimi check","message":"Please fix the errors shown below to successfully generate BIMI record."}
        return data