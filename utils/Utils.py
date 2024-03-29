from pathlib import Path
import re
import Constants
from Config import Config
from werkzeug.utils import secure_filename
import os
from flask import request
class Utils:
    def record_str_to_dict(self, record_str):
        d = {}
        list_data = record_str.split(";")
        for i in list_data:
            if '=' in i:
                s = i.split("=")
                d[(s[0].strip()).lower()] = s[1]
        return d

    def clear_response_single_string(self, response_str):
        response_str = response_str.replace("\r", "")
        response_str = response_str.replace("\n", "")
        return response_str

    def detect_spf_macros(self, spf_record):
        MACRO_REGEX = r"(%{)(.*)(})"
        return re.search(MACRO_REGEX, spf_record)

    def get_abs_path(self, directory):
        return str(Path(directory).parent.absolute())

    def replace_abs_path(self,path,input_string,replace_string):
        try:
            path = self.get_abs_path(path).replace("\\", "\\\\")
            PATH_REGEX = "("+path+".*?\.svg:)"
            output_string = re.sub(PATH_REGEX,input_string,replace_string)
            return output_string
        except Exception as e:
            print("Exception in replace_abs_path for SVG. Error in - ",self.__class__.__name__,". \n Error: ",e)
        
    def strip_svg_plugin_errors(self,directory,error_str,replace_string):
        try:
            path = self.get_abs_path(directory)
            # replaced = error_str
            # for key,value in Constants.svg_regex.items():
            #     replaced = re.sub(value,replace_string,replaced)
            error_str = error_str.split(";")[0].split("error:")[1] + ", At line number: " +(re.search(Constants.svg_error_line,error_str)).group(0)
            return error_str
        except Exception as e:
            print("Exception in strip_svg_plugin_errors for SVG. Error in - ",self.__class__.__name__,". \n Error: ",e)
    
    def allowed_file(self,filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

    def upload_request_file(self, parameter, request, destination_path, return_path = False):
        try:
            if parameter not in request.files:
                return ""
            file = request.files[parameter]
            if file.filename == '':
                return ""
            if file and self.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                self.check_dir_folder(destination_path)
                file.save(os.path.join(destination_path, filename))
                if return_path:
                    return destination_path+filename
                return True 
        except Exception as e:
            print("Exception in upload_file for SVG. Error in - ",self.__class__.__name__,". \n Error: ",e)

    # Check if storage directory exist
    def check_dir_folder(self,path):
            try:
                if not os.path.exists(path):
                    os.makedirs(path)
            except OSError as e:
                if e.errno != errno.EXIST:
                    raise
    
    def svg_replace_file_link(self, domain, svg_path_string):
        try:
            if svg_path_string != None and svg_path_string != "":
                return svg_path_string.replace(Config.STORAGE_SVG_DIR,"https://"+domain+"/public-path-to-svgfile/")
            else:
                return ""
        except Exception as e:
            print("Exception in svg_replace_file_link for SVG. Error in - ",self.__class__.__name__,". \n Error: ",e)
    
    def vmc_replace_file_link(self, domain, vmc_path_string):
        try:
            if vmc_path_string != None and vmc_path_string != "":
                return vmc_path_string.replace(Config.STORAGE_CERT_DIR,"https://"+domain+"/public-path-to-pemfile/")
            else:
                return ""
        except Exception as e:
            print("Exception in vmc_replace_file_link for VMC. Error in - ",self.__class__.__name__,". \n Error: ",e)
