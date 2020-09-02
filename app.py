from flask import Flask,redirect,url_for,request, render_template
from flask_restful import Api,Resource
from controllers.GetList import GetList
from controllers.CheckBimi import CheckBimi
from Config import Config
from utils.Log import logger
import json

#app = Flask(__name__,static_folder = "./templates/cli-build/static", template_folder = "./templates/cli-build")

app = Flask(__name__, static_folder = Config.STATIC_FOLDER, template_folder = Config.TEMPLATE_FOLDER)
api = Api(app)

@app.route('/')
def index():
    return render_template(Config.HOME_PAGE, **{"title":"BIMI Generator","data":"test"})

api.add_resource(GetList, '/all-list')
api.add_resource(CheckBimi, '/check-bimi')

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