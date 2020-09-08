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
        path = self.get_abs_path(directory)
        # regex = r"^"+str(path)+"*.svg$"
        # replaced = re.sub(regex,replace_string,error_str)
        # replaced = error_str.replace(str(path),replace_string)
        return error_str