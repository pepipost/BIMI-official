from flask_restful import Resource,request
import json
from models.CheckRecords import CheckRecords 
from models.CheckSvg import CheckSvg
from models.CheckVmc import CheckVmc
class CheckBimiController(Resource):
    def post(self):
        # CV = CheckVmc("static/storage/certificates/bob.crt",True)
        # CV.validate_vmc()
        # return
        content = request.json
        CR = CheckRecords(content['domain'])
        data = CR.get_dns_details()
        CS = CheckSvg(data['bimi']['svg'])
        data['svg_validation'] = CS.check_svg()
        CV = CheckVmc(data['bimi']['vmc'])
        data['vmc_validation'] = CV.check_vmc()
        return data