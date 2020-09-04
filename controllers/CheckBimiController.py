from flask_restful import Resource,request
import json
from models.CheckRecords import CheckRecords 
class CheckBimiController(Resource):
    def post(self):
        content = request.json
        CR = CheckRecords(content['domain'])
        data = CR.get_dns_details()
        return data