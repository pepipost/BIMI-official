from flask import Flask,redirect,url_for,request, render_template
from flask_restful import Api,Resource
from flask_cors import CORS
from controllers.GetList import GetList
from controllers.CheckBimiController import CheckBimiController
from controllers.GenerateBimiController import GenerateBimiController
from Config import Config
from utils.Log import logger
import json

application = Flask(__name__, static_folder = Config.STATIC_FOLDER, template_folder = Config.TEMPLATE_FOLDER)
api = Api(application)
cors = CORS(application, origins=Config.CORS_WHITELIST)

@application.route('/')
def index():
    return render_template(Config.HOME_PAGE, **{"title":"BIMI Generator"})

api.add_resource(CheckBimiController, '/check-bimi')
api.add_resource(GenerateBimiController, '/generate-bimi')

if __name__ == '__main__':
    application.debug = DEBUG=Config.DEBUG
    host=Config.APP_HOST if Config.APP_HOST else '127.0.0.1'
    port=Config.APP_PORT if (Config.APP_PORT and type(Config.APP_PORT) == int) else 5000
    application.config['TEMPLATES_AUTO_RELOAD'] = True
    application.jinja_env.globals.update(DEBUG=Config.DEBUG)
    application.run(
        host=(host),
        port=(port)
    )
