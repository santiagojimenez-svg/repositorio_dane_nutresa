'''Clase para crear un feature group a partir de CDK'''
import json
import logging
from aws_cdk import aws_sagemaker as sm
from aws_cdk import core as cdk
from mlops_skeleton.artifactory.configuration.constants import ArtifactoryConstants
from mlops_skeleton.artifactory.configuration.resource_config import Configuration

class CreateFeatureGroup(cdk.Construct):
    '''Definir variables necesarias para crear el feature group'''

    def __init__(self,
                 scope: cdk.Construct,
                 id: str,
                 construct_id: str,
                 logger: logging.Logger,
                 config: Configuration,
                 constants:ArtifactoryConstants,
                 **kwargs):
        super().__init__(scope, id, **kwargs)
        self.log = logger or logging.getLogger(__name__)
        self.local_constants = constants.features_dictionary.get(construct_id)
        self.conf = config
        record_id = 'cod_dane_a'
        feature_group_path = (
            f'{constants.feature_group_def_path}/'\
            f'{self.local_constants.get("fuente")}/definition_{constants.env}.json')
        fg_name = (
            f'fg-{self.local_constants.get("entidad")}-'\
            f'{self.local_constants.get("fuente")}-{self.local_constants.get("periodicidad")}-'\
            f'{self.local_constants.get("complejidad")}')

        try:
            with open(feature_group_path, "rb") as file:
                self.log.info(f'Load feature group definition '\
                              f'for {self.local_constants.get("fuente")}')
                fg_def = json.load(file)
                fg_template = (
                    self.create_feature_group(id,
                                              fg_name,
                                              fg_def,
                                              self.local_constants.get("record_id"),
                                              self.local_constants.get("feature_group_mode")))
                cdk.Tags.of(fg_template).add("a-nombre-recurso",
                                             "sagemaker-feature-group")
                cdk.Tags.of(fg_template).add("a-rol-servicio",
                                             "almacenamiento")
        except Exception as error:
            self.log.error(error)
            raise error

    def create_feature_group(self,
                             identifier,
                             fg_name,
                             feature_group_definition,
                             record_id,
                             mode):
        '''Crear feature group a partir de CDK'''
        fg_def = []
        for feature, type in feature_group_definition.items():
            fg_definition_property = (
                sm.CfnFeatureGroup.FeatureDefinitionProperty(feature_name=feature,
                                                             feature_type=type))
            fg_def.append(fg_definition_property)

        if mode == 'offline':
            fg_template = sm.CfnFeatureGroup(
                scope=self,
                id=identifier,
                event_time_feature_name='EventTime',
                feature_definitions=fg_def,
                feature_group_name=fg_name,
                description=(
                    f'FeatureGroup de {self.local_constants.get("entidad")} para '
                    f'{self.local_constants.get("fuente")} '
                    f'con complejidad {self.local_constants.get("complejidad")}, '
                    f'de carga {self.local_constants.get("periodicidad")}'),
                record_identifier_feature_name=record_id,
                offline_store_config={
                    "DisableGlueTableCreation": False,
                    "S3StorageConfig": {
                        "S3Uri": f"s3://{self.conf.feature_store_bucket}/"
                        f'{self.local_constants.get("entidad")}/data/{fg_name}',
                        "KmsKeyId": self.conf.kms_s3_key_arn}
                },
                role_arn=self.conf.process_rol_arn
            )
        elif mode == 'online':
            fg_template = sm.CfnFeatureGroup(
                scope=self,
                id=identifier,
                event_time_feature_name='EventTime',
                feature_definitions=fg_def,
                feature_group_name=fg_name,
                description=(
                    f'FeatureGroup de {self.local_constants.get("entidad")} para '
                    f'{self.local_constants.get("fuente")} '
                    f'con complejidad {self.local_constants.get("complejidad")}, '
                    f'de carga {self.local_constants.get("periodicidad")}'),
                record_identifier_feature_name=record_id,
                offline_store_config={
                    "DisableGlueTableCreation": False,
                    "S3StorageConfig": {
                        "S3Uri": f"s3://{self.conf.feature_store_bucket}/"
                        f'{self.local_constants.get("entidad")}/data/{fg_name}',
                        "KmsKeyId": self.conf.kms_s3_key_arn}
                },
                online_store_config={
                   "EnableOnlineStore": True
                },
                role_arn=self.conf.process_rol_arn
            )
        return fg_template
