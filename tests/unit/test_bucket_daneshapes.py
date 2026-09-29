import sys
import os
import io
import pytest
import boto3
import pandas as pd
import geopandas as gpd
import shapely.geometry
from unittest.mock import MagicMock
from moto import mock_aws

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# --- Mock de SageMaker (Faltaba este bloque aquí) ---
sys.modules['sagemaker'] = MagicMock()
sys.modules['sagemaker.feature_store'] = MagicMock()
sys.modules['sagemaker.feature_store.feature_group'] = MagicMock()
# -----------------------------------------------------------------

# Importamos la nueva función en lugar de retrieve_daneshapes
from src.features.DataMaestraDaneShapes.main import process_and_ingest_partition

@pytest.fixture(scope='session', autouse=True)
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"

class Test_S3_Bucket():
    
    @mock_aws
    def test_s3_process_and_ingest(self):
        bucket_name = "machine-learning-helados-featurestore-lab"
        key_name = "Dane/fuentes_externas_v5/raw/ml_fdex/shapes/manzanas_05001.parquet"

        # 1. Crear el bucket en nuestro S3 falso
        s3_client = boto3.client("s3", region_name='us-east-1')
        s3_client.create_bucket(Bucket=bucket_name)

        # 2. Crear un GeoDataFrame mock y subirlo como Parquet al bucket falso
        gdf_mock = gpd.GeoDataFrame({
            'cod_dane_a': ['05001'],
            'geometry': [shapely.geometry.Point(-75.5, 6.2)]
        }, crs='EPSG:3116')

        buffer = io.BytesIO()
        gdf_mock.to_parquet(buffer)
        buffer.seek(0)

        s3_client.put_object(
            Bucket=bucket_name,
            Key=key_name,
            Body=buffer.getvalue()
        )

        # 3. Mockear el Feature Group de SageMaker
        mock_feature_group = MagicMock()

        # 4. Ejecutar la función real
        process_and_ingest_partition(s3_client, key_name, mock_feature_group)

        # 5. Validaciones (Asserts)
        mock_feature_group.ingest.assert_called_once()
        
        args, kwargs = mock_feature_group.ingest.call_args
        ingested_df = kwargs['data_frame']
        
        assert not ingested_df.empty
        assert 'cod_dane_a' in ingested_df.columns
        assert isinstance(ingested_df['geometry'].iloc[0], str)
        assert 'POINT (-75.5 6.2)' in ingested_df['geometry'].iloc[0]

if __name__ == "__main__":
    test = Test_S3_Bucket()
    test.test_s3_process_and_ingest()