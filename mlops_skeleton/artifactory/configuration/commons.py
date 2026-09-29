'''Clase para crear funciones que son reutilizables como carga
de archivos a s3'''
import logging


class Commons():
    '''Funciones reutilizables dentro del repositorio'''

    def init_logger(self, file_name, log_level=None):
        '''Configuración de logging'''
        if not log_level:
            log_level = 'INFO'
        logging.basicConfig()
        logger = logging.getLogger(file_name)
        logger.setLevel(getattr(logging, log_level))
        return logger

    def load_body_content_s3(self, client, file, bucket, prefix):
        """ Load files into s3, Body has file content"""
        client.put_object(
            Body=file,
            Bucket=bucket,
            Key=prefix
        )

    def load_scripts_s3(self, client, file, bucket, prefix):
        """ Load files into s3, Filename has file path"""
        client.upload_file(
            Filename=file,
            Bucket=bucket,
            Key=prefix
        )

    def delete_fg(self, sm_client, fg_name):
        '''Eliminar un feature group existente'''
        sm_client.delete_feature_group(
            FeatureGroupName=fg_name
        )
