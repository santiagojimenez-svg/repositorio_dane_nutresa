import os
import boto3
from mlops_skeleton.artifactory.configuration.base_config import BaseConfig
from mlops_skeleton.artifactory.configuration.commons import Commons


class Configuration(BaseConfig):
    """En esta clase se definen parametros globales a utilizar en la solución
    de CDK, estos parámetros pueden ser consumidos desde SSM"""

    def __init__(self, log_level=None, ssm_interface=None):
        """
        Complementary Data lab Configuration config stores the Data lab
        specific parameters
        :param log_level: level the class logger should log at
        :param ssm_interface: ssm interface, normally boto, to read parameters
        from parameter store
        """
        commons = Commons()
        self.log_level = log_level or os.getenv('LOG_LEVEL', 'INFO')
        self._logger = commons.init_logger(__name__, self.log_level)
        self._ssm = ssm_interface or boto3.client('ssm',
                                                  region_name='us-east-1')
        super().__init__(self.log_level, self._ssm)
        self._fetch_from_ssm()

    def _fetch_from_ssm(self):
        self._models_bucket = None
        self._monitoring_bucket = None
        self._lambda_rol_arn = None
        self._training_hyperparameters = None
        self._f1_score_threshold = None
        self._model_database = None
        self._features_store_db = None
        self._process_rol_arn = None
        self._feature_store_bucket = None
        self._kms_s3_key_arn = None
        self._account_name = None
        self._account_env = None

    @property
    def models_bucket(self):
        '''Obtiene el bucket de modelos desde SSM'''
        if not self._models_bucket:
            self._logger.info("Getting Sagemaker Bucket from SSM")
            self._models_bucket = self._get_ssm_param(
                '/ml/s3/foundation/models_bucket_name')
        else:
            self._logger.info("Bucket from model")
        return self._models_bucket

    @property
    def monitoring_bucket(self):
        '''Obtiene el bucket de monitoring desde SSM'''
        if not self._monitoring_bucket:
            self._logger.info("Getting Sagemaker Bucket from SSM")
            self._monitoring_bucket = self._get_ssm_param(
                '/ml/s3/foundation/monitoring_bucket_name')
        else:
            self._logger.info("Bucket from monitoring")
        return self._monitoring_bucket

    @property
    def feature_store_bucket(self):
        '''Obtiene el bucket de features desde SSM'''
        if not self._feature_store_bucket:
            self._logger.info("Getting Feature store Bucket from SSM")
            self._feature_store_bucket = self._get_ssm_param(
                '/ml/s3/foundation/feature_store_bucket_name')
        else:
            self._logger.info("Bucket from feature store")
        return self._feature_store_bucket

    @property
    def lambda_rol_arn(self):
        '''Obtiene el rol para ejecutar lambdas desde SSM'''
        if not self._lambda_rol_arn:
            self._logger.info("Getting Lambda execution Role ARN")
            self._lambda_rol_arn = self._get_ssm_param(
                '/ml/iam/foundation/lambda_role_arn')
        else:
            self._logger.info("Lambda Role ARN")
        return self._lambda_rol_arn

    @property
    def process_rol_arn(self):
        '''Obtiene el rol de ejecutar procesos de Sagemaker
         desde SSM'''
        if not self._process_rol_arn:
            self._logger.info("Getting Process Rol ARN")
            self._process_rol_arn = self._get_ssm_param(
                '/ml/iam/foundation/sagemaker_role_arn')
        else:
            self._logger.info("Process Rol ARN")
        return self._process_rol_arn

    @property
    def training_hyperparameters(self):
        '''Obtiene hiperparametros desde SSM'''
        if not self._training_hyperparameters:
            self._logger.info("Getting Training hyperparameter")
            self._training_hyperparameters = self._get_ssm_param(
                '/ml/misc/mundos/hyperparameter')
        else:
            self._logger.info("Training MaxDepth")
        return self._training_hyperparameters

    @property
    def f1_score_threshold(self):
        '''Obtiene el umbral de aceptación de modelos desde SSM'''
        if not self._f1_score_threshold:
            self._logger.info("Getting F1 threshold")
            self._f1_score_threshold = self._get_ssm_param(
                '/ml/misc/mundos/f1threshold')
        else:
            self._logger.info("F1 threshold")
        return self._f1_score_threshold

    @property
    def model_database(self):
        '''Obtiene el nombre de la bd desde SSM'''
        if not self._model_database:
            self._logger.info("Getting Model Database name")
            self._model_database = self._get_ssm_param(
                '/ml/glue/foundation/models_database_name')
        else:
            self._logger.info("Model Database name")
        return self._model_database

    @property
    def features_store_db(self):
        '''Obtiene el nombre de la bd de features desde SSM'''
        if not self._features_store_db:
            self._logger.info("Getting Feature Store Database name")
            self._features_store_db = 'sagemaker_featurestore'
        else:
            self._logger.info("Feature Store Database name")
        return self._features_store_db

    @property
    def account_name(self):
        '''Obtiene el alias de la cuenta desde SSM'''
        if not self._account_name:
            self._logger.info("Getting account alias")
            self._account_name = self._get_ssm_param(
                '/ml/misc/foundation/account_name')
        else:
            self._logger.info("Alias de la cuenta")
        return self._account_name

    @property
    def account_env(self):
        '''Obtiene el nombre del ambiente desde SSM'''
        if not self._account_env:
            self._logger.info("Getting account environment name")
            self._account_env = self._get_ssm_param(
                '/ml/misc/foundation/env_name')
        else:
            self._logger.info("Account environment")
        return self._account_env

    @property
    def kms_s3_key_arn(self):
        '''Obtiene el ID de la llave de KMS desde SSM'''
        if not self._kms_s3_key_arn:
            self._logger.info("Getting KMS ID")
            self._get_ssm_param(
               '/ml/kms/foundation/s3_kms_arn')
        else:
            self._logger.info("ID de la llave de KMS")
        return self._kms_s3_key_arn
