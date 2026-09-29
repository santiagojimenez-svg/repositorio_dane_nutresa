"""Orquestación de creación de recursos a desplegar en el stack"""
import logging
import boto3
from aws_cdk import core as cdk
from mlops_skeleton.feature_group.feature_group import CreateFeatureGroup
from mlops_skeleton.sagemaker_pipelines.pipelines import CreateFeaturePipeline
from mlops_skeleton.artifactory.configuration.resource_config import Configuration
from mlops_skeleton.artifactory.configuration.constants import ArtifactoryConstants
from mlops_skeleton.alerts.alerts import GenerateFeaturesAlerts
from mlops_skeleton.trigger.trigger import GenerateTrigger
from mlops_skeleton.ssm.ssm import ParameterStore

class MlopsFeaturesStack(cdk.Stack):
    '''Orquestación de creación de recursos a desplegar en el stack'''

    def __init__(self,
                 scope: cdk.Construct,
                 construct_id: str,
                 config: Configuration,
                 logger: logging.Logger,
                 s3_client:boto3.client,
                 constants:ArtifactoryConstants,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.local_constants = constants.features_dictionary.get(construct_id)

        ParameterStore(scope = self,
                       identifier = 'ssm_columns_definition',
                       construct_id = construct_id,
                       logger = logger,
                       constants = constants)

        CreateFeatureGroup(scope = self,
                           id = f'fg_{self.local_constants.get("entidad")}_'\
                                f'{self.local_constants.get("fuente")}',
                           construct_id = construct_id,
                           logger = logger,
                           config = config,
                           constants = constants)

        daneshapes_pipeline = (
            CreateFeaturePipeline(scope = self,
                                  identifier = f'ml-helados-features-'\
                                               f'{self.local_constants.get("fuente")}',
                                  construct_id = construct_id,
                                  logger = logger,
                                  config = config,
                                  s3_client = s3_client,
                                  constants = constants))

        GenerateTrigger(scope = self,
                        identifier = f'trigger_{self.local_constants.get("entidad")}_'\
                                     f'{self.local_constants.get("fuente")}',
                        feature_pipeline_name = daneshapes_pipeline.pipeline_name,
                        construct_id = construct_id,
                        logger = logger,
                        config = config,
                        constants = constants)

        notifications_email = scope.node.try_get_context('notifications_email')
        GenerateFeaturesAlerts(scope = self,
                               identifier = 'features-alerts',
                               daneshapes_features_arn = daneshapes_pipeline.pipeline_arn,
                               construct_id = construct_id,
                               logger = logger,
                               notifications_email = notifications_email,
                               constants = constants)
