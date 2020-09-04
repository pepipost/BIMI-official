from certvalidator import CertificateValidator, errors
class CheckCert():
    def certificate_validator(self, certificate_vmc):
    # CERTIFICATE VALIDATOR
    with open(certificate_vmc, 'rb') as f:
        end_entity_cert = f.read()
    try:
        validator = CertificateValidator(end_entity_cert)
        return validator.validate_usage(set(['digital_signature']))
    except (errors.PathValidationError):
        print("Cannot verify certificate. Issue: %s",errors.PathValidationError)