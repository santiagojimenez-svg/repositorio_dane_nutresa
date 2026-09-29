import json
import logging
from aws_cdk import (aws_ssm as ssm,
                     core as cdk)
from mlops_skeleton.artifactory.configuration.constants import ArtifactoryConstants

class ParameterStore(cdk.Construct):
    '''Definición de parametros para construir los ssm'''
    def __init__(self,
                 scope: cdk.Construct,
                 identifier: str,
                 construct_id: str,
                 logger: logging.Logger,
                 constants:ArtifactoryConstants,
                 **kwargs):
        super().__init__(scope, identifier, **kwargs)
        self.log = logger or logging.getLogger(__name__)
        self.local_constants = constants.features_dictionary.get(construct_id)
        self.log.info("Creating SSM parameters")
        definition = (
            f'{constants.ssm_path}/columns_definition/'\
            f'{self.local_constants.get("fuente")}/definition_{constants.env}.json')
        try:
            with open(definition, "rb") as file:
                self.log.info(f"Loading {definition} parameter store definition")
                parameter_name = (
                    f'/ml/misc/features_{self.local_constants.get("entidad")}'\
                    f'/{self.local_constants.get("fuente")}/columns_definition')
                parameter_store_data = json.load(file)
                ssm_parameter_template = self.create_ssm_parameter(
                    parameter_name,
                    parameter_store_data)
                cdk.Tags.of(ssm_parameter_template).add(
                    "a-nombre-recurso",
                    'parameter-store')
                cdk.Tags.of(ssm_parameter_template).add(
                    "a-rol-servicio",
                    "operaciones")
        except Exception as error:
            self.log.error(error)
            raise TypeError(error)

    def create_ssm_parameter(self, parameter_store_name, parameter_store_data):
        '''Creación de SSM parameter store desde CDK'''
        ssm_parameter_template = ssm.StringParameter(
            scope=self,
            id=parameter_store_name,
            string_value=parameter_store_data['value'],
            description=parameter_store_data['description'],
            parameter_name=parameter_store_name
        )

        return ssm_parameter_template