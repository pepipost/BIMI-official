from flask import Flask,redirect,url_for,request, render_template
from flask_restful import Api,Resource
from controllers.HelloWorld import HelloWorld
from controllers.GetList import GetList
from controllers.dnsRecordCheck import getDnsRecords
from Config import Config
from utils.Log import logger
import json

#app = Flask(__name__,static_folder = "./templates/cli-build/static", template_folder = "./templates/cli-build")

app = Flask(__name__, static_folder = Config.STATIC_FOLDER, template_folder = Config.TEMPLATE_FOLDER)
api = Api(app)

@app.route('/')
def index():
    data = '''{"domain":{"status":"success","domain":"pepipost.com","type":"org","mx":[{"preference":5,"exchange":"mx1.pepipost.com","name":"pepipost.com"}],"org_domain":"pepipost.com","message":"Domain check OK"},"source":"bimigroup","website":{"icon":[{"url":"https:\/\/pepipost.com\/wp-content\/uploads\/2018\/10\/favi.png","width":64,"height":64}]},"bimi":{"results":[{"test":"mx","status":"ok","message":"Domain has valid MX records"},{"test":"svg_xml_header","status":"ok","message":"BIMI logo contains no embedded images"},{"test":"svg_url_secure","status":"ok","message":"BIMI url is secure, i.e.https"},{"test":"svg_url_mime","status":"ok","message":"SVG served with valid MIME-type"},{"test":"svg_url_protected","status":"ok","message":"SVG is using stable hosting"},{"test":"svg_aspect","status":"ok","message":"SVG has square dimensions"},{"test":"svg12_bimi_svg","status":"ok","message":"BIMI logo contains no embedded images"},{"test":"sgv_image","status":"ok","message":"SVG doesn\'t contain any rasterized data"},{"test":"svg_ref","status":"ok","message":"SVG contains no prohobited references"},{"test":"svg_colors","status":"ok","message":"SVG with proper color variance"},{"test":"svg_multimedia","status":"ok","message":"SVG contains no multimedia elements"},{"test":"svg_cdata","status":"ok","message":"SVG contains no Base64 encoded data"},{"test":"dmarc_policy_pct","status":"ok","message":"Sufficient DMARC policy for BIMI"},{"test":"dmarc_policy_org","status":"error","message":"Insufficient org-domain DMARC policy"}],"bimi_type":"org","record":"v=BIMI1; l=https:\/\/toolsapi.pepipost.com\/image\/logo.svg; a=;","svg_url":"https:\/\/toolsapi.pepipost.com\/image\/logo.svg","dmarc_status":"error","dmarc_message":"\'none\' is considered insufficient for BIMI display. Deploy at least \'quarantine\' policy to get BIMI support","finalResults":"error"},"dmarc":{"policy_org":"none","policy":"none","rua":["mailto:pepis@pepipost.com"],"ruf":[""],"pct":100,"pct_org":100},"spf":{"status":"success","message":"SPF is valid","record":"v=spf1 ip4:167.89.103.32\/32 ip4:167.89.104.34\/32 ip4:167.89.108.81\/32 ip4:167.89.11.179\/32 ip4:167.89.11.190\/32 ip4:167.89.110.191\/32 ip4:167.89.127.244\/32 ip4:167.89.29.164\/32 ip4:167.89.31.27\/32 ip4:167.89.33.104\/32 ip4:167.89.33.2\/32 ip4:167.89.33.214\/32 ip4:167.89.4.19\/32 ip4:167.89.69.3\/32 ip4:167.89.69.61\/32 ip4:167.89.72.118\/32 ip4:167.89.76.158\/32 ip4:167.89.76.163\/32 ip4:198.21.4.52\/32 ip4:167.89.100.196\/32 ip4:167.89.101.129\/32 ip4:167.89.102.14\/32 ip4:198.37.146.32\/28 ip4:192.237.158.78\/32 ip4:166.78.71.62\/32 ip4:192.237.158.71\/32 ip4:192.237.158.70\/32 ip4:192.237.158.76\/32 ip4:192.237.158.79\/32 ip4:184.173.153.197\/32 ip4:192.237.158.68\/32 ip4:192.237.158.69\/32 ip4:184.173.153.221\/32 ip4:184.173.153.197\/32 ~all"}}'''
    loaded_r = json.loads(data)
    return render_template(Config.HOME_PAGE, **{"title":"BIMI Generator","data":loaded_r})

api.add_resource(HelloWorld, '/hello')
api.add_resource(GetList, '/all-list')
api.add_resource(getDnsRecords, '/getDns')

if __name__ == '__main__':
    app.debug = True
    host=Config.APP_HOST if Config.APP_HOST else '127.0.0.1'
    port=Config.APP_PORT if Config.APP_PORT and Number.isInteger else 5000
    # logger.info("Connecting to Host: %s, Using Port: %d",host,port)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(
        host=(host),
        port=(port)
    )