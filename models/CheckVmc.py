from Config import Config
import requests
from asn1crypto import pem
from certvalidator import CertificateValidator, errors
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from requests import HTTPError
import uuid
from utils.Utils import Utils
from datetime import datetime
import gzip
import base64

class CheckVmc:
    def __init__(self, vmc_file, user_agent, svg_link='', is_file=False):
        self.STORAGE_CERT_DIR = Config.STORAGE_CERT_DIR
        self.vmc_file = vmc_file
        self.Utils = Utils()
        self.vmc_response = {"status": False, "errors":[], "vmc_link":vmc_file}
        self.is_file = is_file
        self.user_agent = user_agent
        self.parsed_vmc = None
        self.svg_link = svg_link
        self.pem_file_path = None

    def download_pem_path(self, url):
        try:
            print('Beginning VMC file download certificate')
            self.Utils.check_dir_folder(self.STORAGE_CERT_DIR)
            file_name_hash = str(uuid.uuid4())

            session = requests.Session()
            session.max_redirects = 3
            response = session.get(url, headers={'User-Agent': self.user_agent})
            if response:
                self.pem_file_path = self.STORAGE_CERT_DIR+file_name_hash+".pem"
                with open(self.STORAGE_CERT_DIR+file_name_hash+".pem", 'wb+') as out_file:
                    out_file.write(response.content)
                return self.STORAGE_CERT_DIR+file_name_hash+".pem"
            else:
                response.raise_for_status()
                return False
        except HTTPError as http_err:
            self.vmc_response['errors'].append("An error occurred while fetching the Certificate from the provided Url. "+str(http_err)+".")
            print(f'HTTP error : {http_err} occurred while fetching the Certificate')
            return False
        except requests.exceptions.TooManyRedirects as red_err:
            self.vmc_response['errors'].append("The cetificate URL redirected too many times, please remove the redirections, or atleast reduce them to 3 or less.")
            print(f'HTTP error : {red_err}. More than 3 redirects while fetching the svg image')
            return False
        except Exception as e:
            print(e)
            return False

    def validate_vmc(self):
        try:
            end_entity_cert = None
            intermediates = []
            with open(self.vmc_file, 'rb') as f:
                readfile = f.read()
                # Create parsed data for expiry and embedded svg check
                self.parsed_vmc = self.parse_vmc_cert(readfile)
                for type_name, headers, der_bytes in pem.unarmor(readfile, multiple=True):
                    if end_entity_cert is None:
                        end_entity_cert = der_bytes
                    else:
                        intermediates.append(der_bytes)

            validator = CertificateValidator(end_entity_cert, intermediates)
            validated = validator.validate_usage(
                set(['digital_signature'])
                # ,extended_key_usage=set(["server_auth", "client_auth"])
                )
            if validated:
                print("Certificate Validated")

        except errors.PathValidationError as PathValidationError:
            self.vmc_response["errors"].append("Warning: "+str(PathValidationError))
            print(PathValidationError)
        except errors.RevokedError as RevokedError:
            self.vmc_response["errors"].append("Warning: Certificate Revoked.\n"+str(RevokedError))
            print(RevokedError)
        except errors.InvalidCertificateError as InvalidCertificateError:
            self.vmc_response["errors"].append("Warning: Certificate Is Invalid.\n"+str(InvalidCertificateError))
            print(InvalidCertificateError)
        except errors.PathBuildingError as PathBuildingError:
            # self.vmc_response["errors"].append("Warning: Cannot Build Path.\n"+str(PathBuildingError))
            print(PathBuildingError)
        except Exception as e:
            self.vmc_response["errors"].append("Warning: Validation Exception.\n"+str(e))
            print(e)


    # Extract SVG image from VMC cert file
    def get_svg_from_cert(self):
        cert_svg = None
        for i in self.parsed_vmc.extensions:
            if hasattr(i.value,'value') and 'svg' in str(i.value.value):
                data = (base64.b64decode(str(i.value.value).split("data:image/svg+xml;base64,")[1]))
                svg = (gzip.decompress(data).decode())
                cert_svg = svg.strip()
                cert_svg = "".join(svg.split())
        return cert_svg

    # naive comapsion SVG in PEM with BIMI SVG
    def compare_pem_svg(self):
        cert_svg = self.get_svg_from_cert()
        if cert_svg:
            with open(self.svg_link,encoding='utf-8') as svg_file:
                # Remove indentation / tabs / newline
                svg = "".join((svg_file.read()).split())
                if svg.lower() == cert_svg.lower():
                    pass
                else:
                    self.vmc_response["errors"].append("The SVG image provided in the BIMI record doesn't match the SVG image provided in the pem file. Please make sure that they are the same.\n")
        else:
            self.vmc_response["errors"].append("There's no embedded SVG Logotype Image as defined in svg logotype RFC 3709. \n")


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

    # Parse VMC certificate
    def parse_vmc_cert(self, pem_data):
        return x509.load_pem_x509_certificate(pem_data, default_backend())

    # Check certificate expiry
    def cert_validity(self):
        current_date_time = datetime.utcnow()
        print(current_date_time)
        print(self.parsed_vmc.not_valid_before)
        print(self.parsed_vmc.not_valid_after)
        if self.parsed_vmc.not_valid_before > current_date_time:
            print("VMC certificate not yet active")
            self.vmc_response["errors"].append("The VMC certificate used is not yet active, and being used prior to the active date: "+self.parsed_vmc.not_valid_before.strftime("%m/%d/%Y, %H:%M:%S"))
            return False
        elif self.parsed_vmc.not_valid_after < current_date_time:
            print("VMC certificate expired")
            self.vmc_response["errors"].append("The VMC certificate used is expired by date: "+self.parsed_vmc.not_valid_after.strftime("%m/%d/%Y, %H:%M:%S"))
            return False
        return True

    # Check VMC certificate
    def check_vmc(self):
        if self.vmc_file != "":
            if not self.is_file:
                self.vmc_file = self.download_pem_path(self.vmc_file)
                if not self.vmc_file:
                    self.vmc_response['status'] = False
                    return self.vmc_response
            else:
                self.pem_file_path = self.vmc_file

            if self.is_vmc_extension():
                # Read stored file and validate with certvalidator
                self.validate_vmc()
                # Check certificate expiry
                self.cert_validity()
                # Compare SVG in BIMI and SVG in PEM cert
                self.compare_pem_svg()
                if len(self.vmc_response['errors']) > 0:
                    self.vmc_response['status'] = False
                else:
                    self.vmc_response['status'] = True
        else:
            # Currently vmc certificate is optional
            self.vmc_response['status'] = "Option"
        return self.vmc_response
