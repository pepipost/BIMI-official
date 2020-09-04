from flask_restful import Resource,request
import json
from models.CheckRecords import CheckRecords 
class CheckBimiRecords(Resource):
    def post(self):
        content = request.json
        domain = content['domain']
        CR = CheckRecords()
        data = CR.get_dns_details(domain)
        return data