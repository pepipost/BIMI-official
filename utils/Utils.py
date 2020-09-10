from pathlib import Path
import re
import Constants
class Utils:
    def clear_response_single_string(self, response_str):
        response_str = response_str.replace("\r", "")
        response_str = response_str.replace("\n", "")
        return response_str

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
            replaced = error_str
            for key,value in Constants.svg_regex.items():
                replaced = re.sub(value,replace_string,replaced)
            return replaced
        except Exception as e:
            print("Exception in strip_svg_plugin_errors for SVG. Error in - ",self.__class__.__name__,". \n Error: ",e)