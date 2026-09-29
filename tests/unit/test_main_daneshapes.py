import pytest
import os
import sys
import json
import pandas as pd
import geopandas as gpd
import boto3
from shapely.geometry import Point
import shapely.wkt
from pytest import fixture

# --- CORRECCIÓN DE MOTO AQUÍ ---
from moto import mock_aws 
# -------------------------------

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


# --- Mock de SageMaker ---
from unittest.mock import MagicMock
sys.modules['sagemaker'] = MagicMock()
sys.modules['sagemaker.feature_store'] = MagicMock()
sys.modules['sagemaker.feature_store.feature_group'] = MagicMock()
# -----------------------------------------------------------------


# Importamos SOLO las funciones que realmente existen y se usan en el main.py
from src.features.DataMaestraDaneShapes.main import (
    set_record_event_time,
    fix_columns_dtypes,
    convert_to_wkt,
    list_parquet_files
)


@pytest.fixture(scope='session', autouse=True)
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    
def t_set_record_event_time():
    test_data = pd.DataFrame({'columna1': [1,2,3,4]}) 
    final_data = set_record_event_time(test_data, 'EventTime')
    assert 'EventTime' in final_data
    
def t_convert_to_wkt():
    geo_file = open('tests/mocks/geometry.json')
    geo_content= json.load(geo_file)["data"]
    geometry = shapely.wkt.loads(geo_content)
    convert_to_wkt(geometry)
    return True

def t_fix_columns_dtypes():
    geo_file = open('tests/mocks/geodataframe.json')
    geo_content= json.load(geo_file)
    df = pd.DataFrame(geo_content)
    geometry = [Point(xy) for xy in zip(df.lon, df.lat)]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
    gdf = fix_columns_dtypes(gdf)
    return True

@mock_aws
def t_list_parquet_files():
    # 1. Configuramos un entorno de S3 simulado
    s3 = boto3.client('s3', region_name='us-east-1')
    bucket_name = "machine-learning-helados-featurestore-lab"
    s3.create_bucket(Bucket=bucket_name)
    
    # 2. Creamos archivos falsos en nuestro S3 simulado
    prefix = "Dane/fuentes_externas_v5/raw/ml_fdex/shapes/"
    
    # Archivos válidos (debería encontrarlos)
    s3.put_object(Bucket=bucket_name, Key=f"{prefix}manzanas_05001.parquet", Body=b"data")
    s3.put_object(Bucket=bucket_name, Key=f"{prefix}manzanas_11001.parquet", Body=b"data")
    
    # Archivos inválidos (NO debería encontrarlos porque no cumplen las reglas)
    s3.put_object(Bucket=bucket_name, Key=f"{prefix}municipios.parquet", Body=b"data") # No tiene 'manzanas_'
    s3.put_object(Bucket=bucket_name, Key=f"{prefix}manzanas_05001.csv", Body=b"data") # No es .parquet
    
    # 3. Llamamos a tu función
    keys = list_parquet_files(bucket_name, prefix)
    
    # 4. Validamos que solo traiga los 2 archivos correctos
    assert len(keys) == 2
    assert f"{prefix}manzanas_05001.parquet" in keys
    assert f"{prefix}manzanas_11001.parquet" in keys
       
        
class Test_DaneShapes_Feature():

    # Si en algún momento necesitas probar S3, simplemente pones @mock_aws encima de la función
    def test_main(self):
        
        # Probamos la adición del tiempo de evento
        t_set_record_event_time()
        
        # Probamos la conversión a WKT
        assert t_convert_to_wkt()
        
        # Probamos el casteo de columnas
        assert t_fix_columns_dtypes()
        
        # Agregamos la prueba de S3
        t_list_parquet_files()
    
if __name__ == "__main__":
    test = Test_DaneShapes_Feature()
    test.test_main()