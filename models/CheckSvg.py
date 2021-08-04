from lxml import etree
import xml.etree.cElementTree as et
import subprocess
from utils.Utils import Utils
import requests
from requests import HTTPError
import sys,os
import uuid
from Config import Config
from utils.Utils import Utils

class CheckSvg:
    def __init__(self, svg_file, user_agent, is_file=False):
        self.RNG_SCHEMA_FILE = Config.RNG_SCHEMA_FILE
        self.STORAGE_SVG_DIR = Config.STORAGE_SVG_DIR
        self.svg_file = svg_file
        self.Utils = Utils()
        self.svg_response = {"status": False, "errors":[], "svg_link":svg_file}
        self.is_file = is_file
        self.user_agent = user_agent

    # Donwnload SVG
    def download_svg_path(self, url):
        print('Beginning SVG file download with requests')
        try:
            self.Utils.check_dir_folder(self.STORAGE_SVG_DIR)
            file_name_hash = str(uuid.uuid4())

            session = requests.Session()
            session.max_redirects = 3
            response = session.get(url, headers={'User-Agent': self.user_agent})
            if response:
                with open(self.STORAGE_SVG_DIR+file_name_hash+".svg", 'wb+') as out_file:
                    out_file.write(response.content)
                print("Generated file: "+self.STORAGE_SVG_DIR+file_name_hash+".svg")
                return self.STORAGE_SVG_DIR+file_name_hash+".svg"
            else:
                response.raise_for_status()
                return False
        
        except HTTPError as http_err:
            self.svg_response['errors'].append({"short_error":"Http Error","error_details":"An error occurred while fetching the BIMI SVG Image. "+str(http_err)+"."})
            print(f'HTTP error : {http_err}, occurred while fetching image');
            return False

        except requests.exceptions.TooManyRedirects as red_err:
            self.svg_response['errors'].append({"short_error":"Too many redirects","error_details":"The svg URL redirected too many times, please remove the redirections, or atleast reduce them to 3 or less."})
            print(f'HTTP error : More than 3 redirects while fetching the svg image');
            return False

        except Exception as e:
            print(e)
            self.svg_response["errors"].append({"short_error":"Something went wrong while downloading the SVG Image","error_details":"Either you have a really bad SVG link or Your SVG cannot be downloaded for processing."})
            return False
            
    # CHECK SVG Extension
    def is_svg_extension(self):
        print('Checking Svg extension')
        if self.is_file:
            if self.svg_file != None:
                return True
            else:
                print(self.svg_file, "Upload SVG Image has an Invalid Extension")
                return False
        else:
            if self.svg_file.endswith('.svg') or self.svg_file.endswith('.SVG'):
                return True
            else:
                return False

    # Check if xml file has an SVG tag
    def is_svg_xml(self):
        print('Checking If this is an XML file')
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
            if self.is_svg_extension():
                if not self.is_file:
                    self.svg_file = self.download_svg_path(self.svg_file)
                    if not self.svg_file:
                        self.svg_response['status'] = False
                        return self.svg_response
                if self.svg_file:
                    if self.is_svg_xml():
                        self.check_svg_schema()
                        if len(self.svg_response['errors']) > 0:
                            self.svg_response['status'] = False
                        else:
                            self.svg_response['status'] = True
                    else:
                        self.svg_response['errors'].append({"short_error":"Invalid SVG","error_details":"The SVG image in your BIMI record has no SVG tag"})
                else:
                    self.svg_response['errors'].append({"short_error":"File extraction error","error_details":"There was an issue with downloading the SVG. Either the SVG image file doesn't exist or the link is unreachable / blocked."})
            else:
                self.svg_response['errors'].append({"short_error":"Extension Error","error_details":"Invalid File extension"})
        else:
            self.svg_response['errors'].append({"short_error":"No SVG Image Found","error_details":"We have found a blank/empty SVG file Or no SVG link in you BIMI record. Please check your BIMI record for this."})

        return self.svg_response
    
    # SVG check according to Relax Ng, rng file schema 
    def check_svg_schema(self):
        try:
            result = subprocess.run(['pyjing',"-c", self.RNG_SCHEMA_FILE,self.svg_file], stdout=subprocess.PIPE)
            # print(result.stdout)
            error_string = result.stdout.decode()
            if error_string:
                if error_string.find("error:")!=-1:
                    err = error_string.split("\n")
                    for i in range(len(err)):
                        # print(err[i])
                        if err[i]:
                            clear_error_string = self.Utils.clear_response_single_string(err[i].split('.svg:')[1])
                            error_str = self.Utils.strip_svg_plugin_errors(self.STORAGE_SVG_DIR,clear_error_string,", Check Line ")
                            self.svg_response['errors'].append({"short_error":error_str,"error_details":clear_error_string})
                    self.svg_response['status'] = False
            else:
                self.svg_response['status'] = True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(str(e))
