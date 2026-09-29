'''Inicio de la lógica'''
import json
import ast
import boto3
from aws_cdk import core
from mlops_skeleton.artifactory.configuration.resource_config import Configuration
from mlops_skeleton.artifactory.configuration.commons import Commons
from mlops_skeleton.feature_stack import MlopsFeaturesStack
from mlops_skeleton.artifactory.configuration.constants import ArtifactoryConstants

app = core.App()
logger = Commons().init_logger(__name__, "INFO")
config = Configuration()
constants = ArtifactoryConstants(logger=logger,
                                 config=config)
s3_client = boto3.client('s3', region_name='us-east-1')

# Se incluyen tags a nivel de stack
TAGS_DEFINITION_PATH = 'src/tags/tags.json'
logger.info('Tags path: %s', TAGS_DEFINITION_PATH)

# Comentario extra
logger.info(f'Opening {TAGS_DEFINITION_PATH}')
with open(TAGS_DEFINITION_PATH, "rb") as file:
    tags = json.dumps((json.load(file))) % {
        "account_name": config.account_name,
        "aws_account_env": config.account_env
        }
    tags = ast.literal_eval(tags)

MlopsFeaturesStack(scope= app,
                   construct_id = "mlops-features-daneshapes",
                   config = config,
                   logger = logger,
                   s3_client = s3_client,
                   constants = constants)


logger.info('Adding tags')
for i in tags:
    core.Tags.of(app).add(i["Key"], i["Value"])

app.synth()
