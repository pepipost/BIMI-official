from pathlib import Path
import re
class Utils:
    def clear_response_single_string(self, response_str):
        response_str = response_str.replace("\r", "")
        response_str = response_str.replace("\n", "")
        return response_str

    def get_abs_path(self, directory):
        return Path(directory).parent.absolute()

    def replace_abs_path(self,directory,error_str,replace_string):
        try:
            path = self.get_abs_path(directory)
            REGEX_ATTRIBUTES = r"(; expected attribute.*?\.svg:)"
            REGEX_ELEMENTS = r"(; expected the element.*?\.svg:|; expected element.*?\.svg:)"
            replaced = error_str
            replaced = re.sub(REGEX_ATTRIBUTES,replace_string,replaced)
            replaced = re.sub(REGEX_ELEMENTS,replace_string,replaced)

            return replaced

        except Exception as e:
            print("Exception in path replace for SVG error in - ",self.__class__.__name__,". \n Error: ",e)