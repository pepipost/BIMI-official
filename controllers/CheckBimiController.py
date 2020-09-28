from flask_restful import Resource,request
import json
from models.CheckRecords import CheckRecords 
from models.CheckSvg import CheckSvg
from models.CheckVmc import CheckVmc
class CheckBimiController(Resource):
    def post(self):
        content = request.json
        user_agent = request.headers.get('User-Agent')
        CR = CheckRecords(content['domain'])
        data = CR.get_dns_details()
        CS = CheckSvg(data['bimi']['svg'],user_agent)
        data['svg_validation'] = CS.check_svg()
        CV = CheckVmc(data['bimi']['vmc'],user_agent)
        data['vmc_validation'] = CV.check_vmc()
        return data