'''Lambda de inicialización para la ejecución del pipeline
que crea e ingesta datos al FeatureGroup'''
import os
import boto3

DATALAKE_DATABASE = os.environ['DATALAKE_DATABASE']
TB_DANESHAPES = os.environ['TB_DANESHAPES']
FEATURE_PIPELINE_NAME = os.environ['FEATURE_PIPELINE_NAME']
sm_client = boto3.client('sagemaker')


def lambda_handler(event, context):
    '''Definición de lambda que inicia el Sagemaker Pipeline'''
    response = sm_client.start_pipeline_execution(
        PipelineName=FEATURE_PIPELINE_NAME,
        PipelineParameters=[

            {
                'Name': 'ProcessingDBDatalake',
                'Value': DATALAKE_DATABASE
            },
            {
                'Name': 'ProcessingTBDaneshapes',
                'Value': TB_DANESHAPES
            }
        ],
        PipelineExecutionDescription='Ingesta de datos con SageMaker Pipeline'
        f'{FEATURE_PIPELINE_NAME}',
    )
    return response
