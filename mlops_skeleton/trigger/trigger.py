import json
import logging
from aws_cdk import aws_lambda
from aws_cdk import core as cdk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_events as events
from mlops_skeleton.artifactory.configuration.constants import ArtifactoryConstants
from mlops_skeleton.artifactory.configuration.resource_config import Configuration

class GenerateTrigger(cdk.Construct):
    '''Definir función lambda con sus disparador'''
    # Cuáles son las variables que necesita mi construct
    def __init__(self,
                 scope: cdk.Construct,
                 identifier: str,
                 feature_pipeline_name: str,
                 construct_id: str,
                 logger: logging.Logger,
                 config: Configuration,
                 constants:ArtifactoryConstants,
                 **kwargs):
        super().__init__(scope, identifier, **kwargs)
        self.log = logger or logging.getLogger(__name__)
        self.local_constants = constants.features_dictionary.get(construct_id)
        self.conf = config

        self.log.info(f'Create lambda for feature '\
                      f'orchestration: {self.local_constants.get("fuente")}')
        self.log.info(f'Triggers event path: {constants.triggers_events_path}')
        lambda_definition = (
            f'{constants.triggers_events_path}/{self.local_constants.get("fuente")}'\
            f'/lambda/definition_{constants.env}.json')

        try:
            # Loading and parsing "definition" for Lambda function file.
            with open(lambda_definition, "rb") as file:
                self.log.info(f"Loading Lambda function definition: {lambda_definition}")
                lambda_id = f'features-initialize-{self.local_constants.get("fuente")}'
                lambda_data = json.load(file)
                lambda_handler_name = "ause1-ml-lmd-" + lambda_id
                lambda_general_path = f'{constants.lambda_src_path}'
                tb_daneshapes = ("" if self.local_constants.get("info_table") is None
                                    else self.local_constants.get("info_table"))
                tipo_modelo = ("" if self.local_constants.get("tipo_modelo") is None
                                    else self.local_constants.get("tipo_modelo"))
                environment_variables = {'DATALAKE_DATABASE': self.local_constants.get("datalake_db"),
                                         'TB_DANESHAPES': tb_daneshapes,
                                         'FEATURE_PIPELINE_NAME': feature_pipeline_name,
                                         'TIPO_MODELO' : tipo_modelo}
                lambda_template = self.create_lambda_function(
                    lambda_function_handler_name=lambda_handler_name,
                    script_location=f'{lambda_general_path}/{self.local_constants.get("fuente")}',
                    data=lambda_data,
                    environment_variables=environment_variables)
                    
                cdk.Tags.of(lambda_template).add("a-nombre-recurso",
                                                 "lambda")
                cdk.Tags.of(lambda_template).add("a-rol-servicio",
                                                 "operaciones")
        except Exception as error:
            self.log.error(error)
            raise error

        self.log.info(f'Create trigger for feature orchestration: {self.local_constants.get("fuente")}')
        event_definition = (
            f'{constants.triggers_events_path}/{self.local_constants.get("fuente")}'\
            f'/cloudwatch/definition_{constants.env}.json')
        try:
            with open(event_definition, "rb") as file:
                self.log.info(f"Loading CloudWatch scheduled event definition: {event_definition}")
                event_id = f'features-{self.local_constants.get("fuente")}-mth'
                event_data = json.load(file)
                event_name = "ause1-ml-ev-" + event_id
                lambda_target_arn = lambda_template.function_arn
                self.log.info(f"Lambda function name: {lambda_handler_name}")
                self.create_scheduled_event(
                    event_name=event_name,
                    target_arn=lambda_target_arn,
                    target_name=lambda_handler_name,
                    data=event_data)
        except Exception as error:
            self.log.error(error)
            raise error

    def create_lambda_function(self,
                               lambda_function_handler_name,
                               script_location,
                               data,
                               environment_variables) -> aws_lambda.CfnFunction:
        """Funcion que toma como argumento el json y crea la funcion lambda."""
        property_python_version = data['property_python_version']
        memory_size = data['memory_size']
        timeout = data['timeout']
        lambda_template = aws_lambda.Function(
            self,
            id=lambda_function_handler_name,
            runtime=aws_lambda.Runtime(str(property_python_version)),
            code=aws_lambda.Code.asset(script_location),
            handler='main.lambda_handler',
            function_name=lambda_function_handler_name,
            memory_size=memory_size,
            role=iam.Role.from_role_arn(
                self,
                id=f'{lambda_function_handler_name}_role',
                role_arn=self.conf.lambda_rol_arn,
            ),
            environment=environment_variables,
            timeout=cdk.Duration.seconds(timeout),
            description='Feature lambda initialization'
        )
        return lambda_template

    def create_scheduled_event(self,
                               event_name,
                               target_arn,
                               target_name,
                               data) -> events.CfnRule:
        '''Función para crear el evento a partir de CDK'''
        schedule_expression = data["schedule_expression"]
        state = data["state"]
        description = data.get("description", "No description")
        lambda_permission_id = event_name + "permission"

        events_target_property = events.CfnRule.TargetProperty(
            id=target_name+'_property',
            arn=target_arn)

        event_template = events.CfnRule(
            self,
            id=event_name,
            name=event_name,
            description=description,
            schedule_expression=schedule_expression,
            state=state,
            targets=[events_target_property])

        aws_lambda.CfnPermission(
            self,
            id=lambda_permission_id,
            action="lambda:InvokeFunction",
            function_name=target_name,
            principal="events.amazonaws.com",
            source_arn=event_template.attr_arn)

        return event_template
