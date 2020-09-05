from asn1crypto import pem
from certvalidator import CertificateValidator, errors
class CheckCert():
    def certificate_validator(self, certificate_vmc):
        #Certificate validator (DER or PEM-encoded X.509 certificate)
        #patch by @snipperbytes (vikram sahu)
        end_entity_cert = None
        intermediates = []
        with open(certificate_vmc, 'rb') as f:
            print(f)
            for type_name, headers, der_bytes in pem.unarmor(f.read(), multiple=True):
                if end_entity_cert is None:
                    end_entity_cert = der_bytes
                else:
                    intermediates.append(der_bytes)
                validator = CertificateValidator(end_entity_cert, intermediates)
                print(intermediates)
    
    
    """# CERTIFICATE VALIDATOR
        with open(certificate_vmc, 'rb') as f:
            end_entity_cert = f.read()
        try:
            validator = CertificateValidator(end_entity_cert)
            return validator.validate_usage(set(['digital_signature']))
        except (errors.PathValidationError):
            print("Cannot verify certificate. Issue: %s",errors.PathValidationError)"""