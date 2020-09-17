from Config import Config
import urllib.request
import subprocess
import sys,os
from asn1crypto import pem
from certvalidator import CertificateValidator
from utils.Utils import Utils
import base64
class CheckVmc():
    def __init__(self, vmc_file, is_file=False):
        self.STORAGE_CERT_DIR = Config.STORAGE_CERT_DIR
        self.vmc_file = vmc_file
        self.Utils = Utils()
        self.vmc_response = {"status": False, "errors":[], "vmc_link":vmc_file}
        self.is_file = is_file

    def check_vmc(self):
        self.check_vmc_schema()

    def check_vmc_schema(self):
        try:
            end_entity_cert = None
            intermediates = []
            with open('static/storage/certificates/acvmc.pem', 'rb') as f:
                for type_name, headers, der_bytes in pem.unarmor(f.read(), multiple=True):
                    if end_entity_cert is None:
                        end_entity_cert = der_bytes
                    else:
                        intermediates.append(der_bytes)

            validator = CertificateValidator(end_entity_cert, intermediates)
            result = validator.validate_usage(set(['digital_signature']))
            print(base64.b64decode(str(result)))
            print(json.loads(result))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(str(e))

    # Check VMC extension
    def is_vmc_extension(self):
        if self.vmc_file.endswith('.pem') or self.vmc_file.endswith('.PEM'):
            return True
        else:
            return False