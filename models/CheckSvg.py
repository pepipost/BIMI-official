from lxml import etree
import xml.etree.cElementTree as et
import subprocess
from utils.Utils import Utils
import urllib.request
import os
import uuid
from Config import Config
class CheckSvg:
    def __init__(self, svg_file):
        self.RNG_SCHEMA_FILE = Config.RNG_SCHEMA_FILE
        self.STORAGE_SVG_DIR = Config.STORAGE_SVG_DIR
        self.errors = []
        self.svg_file = svg_file
        self.Utils = Utils()
        self.svg_response = {"status": False, "errors":[]}

    # Donwnload SVG
    def download_svg_path(self, url):
        print('Beginning file download with urllib2')
        self.check_dir_folder()
        file_name_hash = str(uuid.uuid4())
        with urllib.request.urlopen(url) as response, open(self.STORAGE_SVG_DIR+file_name_hash+".svg", 'wb') as out_file:
            data = response.read() # a `bytes` object
            out_file.write(data)
        return self.STORAGE_SVG_DIR+file_name_hash+".svg"

    # Check if storage directory exist
    def check_dir_folder(self):
        try:
            if not os.path.exists(self.STORAGE_SVG_DIR):
                os.makedirs(self.STORAGE_SVG_DIR)
        except OSError as e:
            if e.errno != errno.EXIST:
                raise

    # CHECK SVG TAG (EXCLUDED)
    def is_svg_extension(self):
        if self.svg_file.endswith('.svg') or self.svg_file.endswith('.SVG'):
            return True
        else:
            return False

    # Check if xml file has an SVG tag
    def is_svg_xml(self):
        tag = None
        with open(self.svg_file, "r") as f:
            try:
                for event, el in et.iterparse(f, ('start',)):
                    tag = el.tag
                    break
            except et.ParseError:
                pass
        return tag == '{http://www.w3.org/2000/svg}svg'

    # SVG check function
    def check_svg(self):
        if self.svg_file != "":
            self.svg_file = self.download_svg_path(self.svg_file)
            if self.is_svg_xml():
                self.chec_svg_schema()
                if len(self.svg_response['errors']) > 0:
                    self.svg_response['status'] = False
                else:
                    self.svg_response['status'] = True
            else:
                self.svg_response['errors'].append({"short_error":"Invalid SVG","error_details":"The SVG image in your BIMI record has no SVG tag"})
        else:
            self.svg_response['errors'].append({"short_error":"No SVG Image Found","error_details":"We have found a blank/empty SVG file Or no SVG link in you BIMI record. Please check your BIMI record for this."})

        return self.svg_response
    
    # SVG check according to SVG Relax Ng, rng file schema 
    def chec_svg_schema(self):
        try:
            result = subprocess.run(['pyjing',"-c", self.RNG_SCHEMA_FILE,self.svg_file], stdout=subprocess.PIPE)
            # print(result.stdout)
            error_string = result.stdout.decode()
            if error_string:
                if error_string.find("error:"):
                    err = error_string.split("error:")
                    # print(error_string)
                    for i in range(1, len(err)-1):
                        clear_error_string = self.Utils.clear_response_single_string(err[i])
                        error_str = self.Utils.replace_abs_path(self.STORAGE_SVG_DIR,clear_error_string,", at Line ")
                        self.svg_response['errors'].append({"short_error":error_str,"error_details":clear_error_string})
                    self.svg_response['status'] = False
            else:
                self.svg_response['status'] = True
        except Exception as e:
            print("error in executing pyjing schema check. Error: ",e)