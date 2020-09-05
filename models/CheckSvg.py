from lxml import etree
import xml.etree.cElementTree as et
import subprocess
from utils.Utils import Utils
import urllib.request
import os
import uuid
# from pprint import pprint
# from io import StringIO1
class CheckSvg:
    def __init__(self, svg_file):
        self.RNG_SCHEMA_FILE = "svg_schema/svg_12_ps.rnc"
        self.STORAGE_SVG_DIR = "storage/svgs/"
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
                self.svg_response['errors'].append("Invalid SVG")
        else:
            self.svg_response['errors'].append("No SVG Image Found")
        return self.svg_response

    def chec_svg_schema(self):
        try:
            command = "pyjing -c "+self.RNG_SCHEMA_FILE+" "+self.svg_file
            result = subprocess.run(['pyjing',"-c", self.RNG_SCHEMA_FILE,self.svg_file], stdout=subprocess.PIPE)
            # print(result.stdout)
            error_string = result.stdout.decode()
            if error_string.find('and'):
                error_responses = error_string.split('and')
                for error_response in error_responses:
                    if error_response.find("error:"):
                        err = error_response.split("error:")
                        clear_error_string = self.Utils.clear_response_single_string(err[1])
                        self.errors.append(clear_error_string)
            return self.errors
        except Exception as e:
            print("error in executing pyjing schema check. Error: ",e)

    def chec_svg_schema_min(self, file_svg):
        with open(self.RNG_SCHEMA_FILE) as f:
            relaxng_doc = etree.parse(f)
        relaxng = etree.RelaxNG(relaxng_doc)

        with open(file_svg) as valid:
            doc = etree.parse(valid)
        return relaxng.validate(doc)

        """with open(self.RNG_SCHEMA_FILE) as f:
            relaxng_doc = etree.parse(f)
        
        relaxng = etree.RelaxNG(relaxng_doc)

        with open(file_svg) as valid:
            doc = etree.parse(valid)
        return relaxng.validate(doc)"""

        """f = StringIO('''\
                        <element name="a" xmlns="http://relaxng.org/ns/structure/1.0">
                        <zeroOrMore>
                            <element name="b">
                            <text />
                            </element>
                        </zeroOrMore>
                        </element>
                    ''')
        relaxng_doc = etree.parse(f)
        relaxng = etree.RelaxNG(relaxng_doc)

        with open(file_svg) as svg:
            doc = etree.parse(svg)
        relaxng.validate(doc)"""