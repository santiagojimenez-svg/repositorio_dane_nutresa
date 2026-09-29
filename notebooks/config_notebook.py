'''Definición de variables utiles para el uso de notebooks'''
import os
import sys
currDir = os.path.dirname(os.path.realpath("__file__"))
rootDir = os.path.abspath(os.path.join(currDir, '..'))
sys.path.insert(1, rootDir + '/src')

print('Directorio "src" adicionado para cargar modulos')

import sagemaker

print('Librerías boto3 y sagemaker importadas')


sagemaker_session = sagemaker.Session()
sagemaker_role = 'arn:aws:iam::544644514035:role/ause1-rol-ml-sagemaker-crud-processes'
sagemaker_region = 'us-east-1'

# S3 bucket for saving code and model artifacts.
# Feel free to specify a different bucket and prefix
sagemaker_bucket = 'machine-learning-serviciosnutresa-modelos-lab'
feature_store_bucket='machine-learning-serviciosnutresa-featurestore-lab'

print('Variables de sagemaker listas para ser usadas:')
print('\t* sagemaker_session')
print('\t* sagemaker_role:', sagemaker_role)
print('\t* sagemaker_bucket:', sagemaker_bucket)
print('\t* feature_store_bucket:', feature_store_bucket)
