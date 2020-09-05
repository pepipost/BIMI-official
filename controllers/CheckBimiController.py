from flask_restful import Resource,request
import json
from models.CheckRecords import CheckRecords 
from models.CheckSvg import CheckSvg
class CheckBimiController(Resource):
    def post(self):
        content = request.json
        svg_check = {}
        # CS = CheckSvg("storage/svgs/svg-file.svg")
        # return CS.check_svg()
        CR = CheckRecords(content['domain'])
        data = CR.get_dns_details()
        CS = CheckSvg(data['bimi']['svg'])
        data['svg_validation'] = CS.check_svg()
        return data
        # return CS