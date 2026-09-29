'''Construcción de constantes'''
import os
import logging
from aws_cdk import core

def set_p_env(env_name, aws_account_env):
    """ Set p_env based on env_name and aws_account_env"""
    if env_name!='prod':
        if aws_account_env=='calidad':
            return 'test'
        return 'dev'
    return 'prod'

def set_db_name(env_name, aws_account_env):
    """Trae el nombre de la base de datos de machine 
       learning según el ambiente"""
    if aws_account_env != "hel001":
        return f"db_machine_learning_nutresa_{env_name}"
    return 'db_machine_learning_helados_lab'

class ArtifactoryConstants:
    '''Definición de constantes'''
    def __init__(self,
                 logger,
                 config) -> None:
        self.log = logger or logging.getLogger(__name__)
        self.log.info('Loading CDK context variables ...')
        self.aws_region = core.Aws.REGION
        self.aws_account_id = core.Aws.ACCOUNT_ID
        self.aws_account_name = config.account_name
        self.aws_account_env = config.account_env
        self.env = 'prod' if self.aws_account_env=='produccion' else 'dev'
        self.p_env = set_p_env(self.env, self.aws_account_env)
        self.log.info('Region: %s', self.aws_region)
        self.log.info('Account ID: %s', self.aws_account_id)
        self.log.info("env: %s", self.env)
        self.log.info("p_env: %s", self.p_env)
        self.base_path = os.getcwd()
        self.triggers_events_path = f"{self.base_path}/mlops_skeleton/trigger"
        self.lambda_src_path = f"{self.base_path}/src/lambdas"
        self.feature_group_def_path = f"{self.base_path}/mlops_skeleton/feature_group"
        self.ssm_path = f"{self.base_path}/mlops_skeleton/ssm"
        self.pipeline_def_path = f"{self.base_path}/mlops_skeleton/sagemaker_pipelines"
        self.feature_src_path = f"{self.base_path}/src/features"
        self.datalake_db = set_db_name(self.p_env, self.aws_account_env)

        self.features_dictionary = (
            {'mlops-features-daneshapes':
              {'record_id': 'cod_dane_a',
               'entidad': 'Dane',
               'fuente': 'DataMaestraDaneShapes',
               'periodicidad': 'monthly',
               'complejidad': 'simple',
               'feature_group_mode': 'offline',
               'datalake_db': f"db_nutresa_datalake_stage_{self.p_env}",
               'info_table': 'ml_epv_tb_data_maestra_daneshapes'}})
