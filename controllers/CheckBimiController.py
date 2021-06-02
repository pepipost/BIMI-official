from flask_restful import Resource,request
import json
from models.CheckRecords import CheckRecords 
from models.CheckSvg import CheckSvg
from models.CheckVmc import CheckVmc
class CheckBimiController(Resource):
    def post(self):
        content = request.json
        data = {"bimi":{},"dmarc":{},"mx":{},"spf":{},"svg_validation":{},"vmc_validation":{}}
        if "domain" not in content or (content['domain'].strip() == "" or content['domain'].strip() is None) :
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
            return data, 400

        user_agent = request.headers.get('User-Agent')
        
        CR = CheckRecords(content['domain'])
        
        data = CR.get_dns_details()

        CS = CheckSvg(data['bimi']['svg'],user_agent)
        print(data['bimi']['svg'])
        data['svg_validation'] = CS.check_svg()
        CV = CheckVmc(data['bimi']['vmc'],user_agent)
        data['vmc_validation'] = CV.check_vmc()
        return data