from flask_restful import Resource,request
import json
from models.CheckRecords import CheckRecords 
from models.CheckSvg import CheckSvg
class CheckBimiController(Resource):
    def post(self):
        # CS = CheckSvg("svg")
        # CS.check_path()
        # return

        content = request.json
        svg_check = {}
        CR = CheckRecords(content['domain'])
        data = CR.get_dns_details()
        CS = CheckSvg(data['bimi']['svg'])
        data['svg_validation'] = CS.check_svg()
        return data