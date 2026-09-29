'''Construcción de pipeline de FeaturesGroup'''
import json
import logging
import boto3
from aws_cdk import (aws_sagemaker as sm,
                     core as cdk)
from mlops_skeleton.artifactory.configuration.resource_config import Configuration
from mlops_skeleton.artifactory.configuration.commons import Commons
from mlops_skeleton.artifactory.configuration.constants import ArtifactoryConstants

class CreateFeaturePipeline(cdk.Construct):
    '''Definición de parametros necesarios para la creación del pipeline'''
    def __init__(self,
                 scope: cdk.Construct,
                 identifier: str,
                 construct_id: str,
                 logger: logging.Logger,
                 config: Configuration,
                 s3_client: boto3.client,
                 constants:ArtifactoryConstants,
                 **kwargs):
        super().__init__(scope, identifier, **kwargs)
        self.log = logger or logging.getLogger(__name__)
        self.constants = constants
        self.local_constants = self.constants.features_dictionary.get(construct_id)
        self.conf = config
        self._pipeline_arn = None
        self._pipeline_name = None
        common = Commons()
        pipeline_definition_path = (
            f'{self.constants.pipeline_def_path}/{self.local_constants.get("fuente")}'\
            f'/definition_{self.constants.env}.json')
        pipeline_s3_path = (
            f'{self.local_constants.get("entidad")}/artefactos/codigo/pipelines'\
            f'/{self.local_constants.get("fuente")}/pipeline.json')
        feature = self.local_constants.get("fuente")
        features_src_path = f'{self.constants.feature_src_path}/{feature}'
        features_s3_path = (
            f'{self.local_constants.get("entidad")}/artefactos/codigo/features'\
            f'/{self.local_constants.get("fuente")}')
        script_files = ['main.py', 'requirements.txt']

        # Load py scripts to s3
        for file in script_files:
            common.load_scripts_s3(
                client=s3_client,
                file=f'{features_src_path}/{file}',
                bucket=self.conf.feature_store_bucket,
                prefix=f'{features_s3_path}/{file}')

        # Pipeline definition
        try:
            with open(pipeline_definition_path, "rb") as file:
                self.log.info("Load pipeline definition")
                pipeline_def = json.dumps((json.load(file))) % {
                    "models_bucket": self.conf.models_bucket,
                    "aws_region": self.constants.aws_region,
                    "feature_store_bucket": self.conf.feature_store_bucket,
                    "process_rol_arn": self.conf.process_rol_arn,
                    "entidad": self.local_constants.get("entidad"),
                    "fuente": self.local_constants.get("fuente"),
                    "periodicidad": self.local_constants.get("periodicidad"),
                    "complejidad": self.local_constants.get("complejidad"),
                    "record_identifier_name": self.local_constants.get("record_id"),
                    "monitoring_bucket": self.conf.monitoring_bucket,
                    "account_env": self.conf.account_env,
                    "p_env": self.constants.p_env}

                common.load_body_content_s3(
                    client=s3_client,
                    file=pipeline_def,
                    bucket=self.conf.feature_store_bucket,
                    prefix=pipeline_s3_path)

                self.pipeline_feature_template = (
                    self.create_pipeline(pipeline_s3_path,
                                         identifier,
                                         self.local_constants.get("fuente")))

                cdk.Tags.of(self.pipeline_feature_template).add("a-nombre-recurso",
                                                                "sagemaker-pipelines")
                cdk.Tags.of(self.pipeline_feature_template).add("a-rol-servicio",
                                                                "operaciones")
        except Exception as error:
            self.log.error(error)
            raise error

    def create_pipeline(self, pipeline_s3_path, identifier, fuente):
        '''Definición de creación de pipeline con CDK'''
        self.log.info(f"Creating pipeline {identifier}")
        pipeline_feature_template = sm.CfnPipeline(
            scope=self,
            id=f'pipeline-{fuente}',
            pipeline_definition={
                "PipelineDefinitionS3Location": {
                    "Bucket": self.conf.feature_store_bucket,
                    "Key": pipeline_s3_path,
                    }},
            pipeline_name=identifier,
            role_arn=self.conf.process_rol_arn,
            pipeline_description=f'Feature pipeline for {fuente}')

        return pipeline_feature_template

    @property
    def pipeline_arn(self):
        '''Construcción del arn del pipeline'''
        self._pipeline_arn = f'arn:aws:sagemaker:{self.constants.aws_region}: '\
        f'{self.constants.aws_account_id}:pipeline/'\
        f'{self.pipeline_feature_template.pipeline_name}'
        return self._pipeline_arn

    @property
    def pipeline_name(self):
        '''Encontrar el nombre del pipeline'''
        self._pipeline_name = self.pipeline_feature_template.pipeline_name
        return self._pipeline_name
