from Config import Config
from urllib.request import Request, urlopen
import sys,os
from asn1crypto import pem
from certvalidator import CertificateValidator, errors
from utils.Utils import Utils
import uuid
class CheckVmc:
    def __init__(self, vmc_file, user_agent, is_file=False):
        self.STORAGE_CERT_DIR = Config.STORAGE_CERT_DIR
        self.vmc_file = vmc_file
        self.Utils = Utils()
        self.vmc_response = {"status": False, "errors":[], "vmc_link":vmc_file}
        self.is_file = is_file
        self.user_agent = user_agent

    def download_pem_path(self, url):
        print('Beginning VMC file download certificate with urllib')
        self.Utils.check_dir_folder(self.STORAGE_CERT_DIR)
        file_name_hash = str(uuid.uuid4())
        req = Request(url, headers={'User-Agent': self.user_agent})
        with urlopen(req) as response, open(self.STORAGE_CERT_DIR+file_name_hash+".pem", 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        return self.STORAGE_CERT_DIR+file_name_hash+".pem"

    def validate_vmc(self):
        try:
            end_entity_cert = None
            intermediates = []
            with open(self.vmc_file, 'rb') as f:
                for type_name, headers, der_bytes in pem.unarmor(f.read(), multiple=True):
                    if end_entity_cert is None:
                        end_entity_cert = der_bytes
                    else:
                        intermediates.append(der_bytes)
            validator = CertificateValidator(end_entity_cert, intermediates)
            validated = validator.validate_usage(set(['digital_signature']))
            # print(intermediates)
        except errors.PathValidationError as PathValidationError:
            self.vmc_response["errors"].append("Warning: "+str(PathValidationError))
            print(PathValidationError)
        except errors.RevokedError as RevokedError:
            self.vmc_response["errors"].append("Warning: Certificate Revoked.\n"+str(RevokedError))
            print(RevokedError)
        except errors.InvalidCertificateError as InvalidCertificateError:
            self.vmc_response["errors"].append("Warning: Certificate Is Invalid.\n"+str(InvalidCertificateError))
            print(InvalidCertificateError)
        # except errors.PathBuildingError as PathBuildingError:
        #     self.vmc_response["errors"].append("Warning: Cannot Build Path.\n"+str(PathBuildingError))
        #     print(PathBuildingError)
        except Exception as e:
            if "Unable to build a validation path" in str(e):
                pass
            else:
                self.vmc_response["errors"].append("Warning: Validation Exception.\n"+str(e))
                print(e)


    # Check VMC extension
    def is_vmc_extension(self):
        if self.is_file:
            if self.vmc_file != None:
                return True
            else:
                print(self.vmc_file, "Uploaded Vmc certificates has an Invalid Extension")
                return False
        else:
            if self.vmc_file.endswith('.pem') or self.vmc_file.endswith('.PEM'):
                return True
            else:
                self.vmc_response["errors"].append("Invalid file extension used. Only .pem files allowed")
                return False

    # Check vmc certificate
    def check_vmc(self):
        if self.vmc_file != "":
            if not self.is_file:
                self.vmc_file = self.download_pem_path(self.vmc_file)
            if self.is_vmc_extension():
                self.validate_vmc()
                if len(self.vmc_response['errors']) > 0:
                    self.vmc_response['status'] = False
                else:
                    self.vmc_response['status'] = True
        else:
            # Currently vmc certificate is optional
             self.vmc_response['status'] = "Option"
        return self.vmc_response
