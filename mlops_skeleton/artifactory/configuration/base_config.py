from botocore.exceptions import ClientError
from mlops_skeleton.artifactory.configuration.commons import Commons


class BaseConfig:
    """Define la forma de consultar los parámetros almacenados en SSM"""
    def __init__(self, log_level, ssm_interface):
        commons = Commons()
        self.log_level = log_level
        self._logger = commons.init_logger(__name__, log_level)
        self._ssm = ssm_interface

    def _fetch_from_ssm(self):
        raise NotImplementedError()

    def _get_ssm_param(self, key):
        try:
            self._logger.info('Obtaining SSM Parameter: {}'.format(key))
            return self._ssm.get_parameter(Name=key)['Parameter']['Value']
        except ClientError as error:
            if error.response['Error']['Code'] == 'ThrottlingException':
                self._logger.error("SSM RATE LIMIT REACHED")
            else:
                self._logger.error("Unexpected error: %s" % error)
            raise
