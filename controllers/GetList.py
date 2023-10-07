from flask_restful import Resource
from models.DbLog import DbLog
import json

#for debugging
from pprint import pprint

class GetList(Resource):
    def post(self):
        # content = request.json
        # a = json.loads(content)
        # return content['test']
        dblog = DbLog()
        return json.dumps({"message":"success","data":dblog.createLog()})