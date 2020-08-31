from flask_restful import Resource,request
import json
import subprocess

class getDnsRecords(Resource):
    def post(self):
        # content = request.json
        # a = json.loads(content)
        # return content['test']
        content = request.json
        content['domain']
        result = subprocess.run(['checkdmarc', content['domain']], stdout=subprocess.PIPE)
        complied_json = json.loads(result.stdout)

        # return result
        return json.dumps({"message":"success","data":complied_json.replace('\"','"')})