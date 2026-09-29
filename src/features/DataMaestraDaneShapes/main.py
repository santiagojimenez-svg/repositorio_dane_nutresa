'''Script para la definición e ingesta del FeatureGroup: INTERNA

Feature Group: Producto-Daily-Simple
'''

import subprocess
import sys
import os
import tempfile

REQUI = "/opt/ml/processing/input/requirements/requirements.txt"

try:
    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        "-r",
        REQUI])
except subprocess.CalledProcessError as error:
    print('requirements.txt file not found ', error.output)

import argparse
import time
import boto3
import geopandas as gpd
import sagemaker
from sagemaker.feature_store.feature_group import FeatureGroup

parser = argparse.ArgumentParser()
parser.add_argument('--region', type=str, default='us-east-1')
parser.add_argument('--feature-store-bucket', type=str)
parser.add_argument('--entidad', type=str)
parser.add_argument('--fuente', type=str, default='interna')
parser.add_argument('--periodicidad', type=str)
parser.add_argument('--record-identifier-name', type=str)
parser.add_argument('--record-event-time-name', type=str)
parser.add_argument('--complejidad', type=str)
parser.add_argument('--db-datalake', type=str)
parser.add_argument('--tb-daneshapes', type=str)
args, _ = parser.parse_known_args()

# Parámetros
region = args.region
feature_store_bucket = args.feature_store_bucket
entidad = args.entidad
fuente = args.fuente
periodicidad = args.periodicidad
record_identifier_name = args.record_identifier_name
record_event_time_name = args.record_event_time_name
complejidad = args.complejidad
feature_group_name = f'fg-{entidad}-{fuente}-{periodicidad}-{complejidad}'

# Conexiones
boto_session = boto3.session.Session(region_name=region)
sagemaker_session = sagemaker.Session(boto_session=boto_session,
                                      default_bucket=feature_store_bucket)

# --- RUTAS REALES (Ajustadas a tu S3) ---
SHAPES_BUCKET = "machine-learning-helados-featurestore-lab"
# Ruta de la carpeta donde están las particiones "manzanas_05001.parquet", etc.
DANE_PARQUET_PREFIX = "Dane/fuentes_externas_v5/raw/ml_fdex/shapes/"


def set_record_event_time(dataset, record_event_time_name_local):
    """Agrega la columna de tiempo al dataset si no existe"""
    if record_event_time_name_local not in dataset:
        dataset[record_event_time_name_local] = time.time()
    return dataset


def list_parquet_files(bucket, prefix):
    """Obtiene la lista de todos los archivos parquet particionados en la ruta"""
    s3_client = boto3.client('s3', region_name=region)
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
    
    keys = []
    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                # Aquí filtramos por archivos .parquet
                # Si todos se llaman "manzanas_XXXXX.parquet", esto los encontrará
                if obj['Key'].endswith('.parquet') and 'manzanas_' in obj['Key']:
                    keys.append(obj['Key'])
    return keys


def convert_to_wkt(geometry):
    """Conversion de geometrias a formato string WKT"""
    if hasattr(geometry, 'wkt'):
        return geometry.wkt
    return str(geometry)


def fix_columns_dtypes(geodataframe):
    """Arreglo de columnas a fin de ser guardadas como string en Feature Store"""
    if 'geometry' in geodataframe.columns:
        geodataframe['geometry'] = geodataframe['geometry'].apply(convert_to_wkt).astype(str)

    for col in geodataframe.columns:
        if col == 'geometry':
            continue
        if geodataframe.dtypes[col] == 'object':
            geodataframe[col] = geodataframe[col].astype(str)
        elif geodataframe.dtypes[col] == 'float64':
            geodataframe[col] = geodataframe[col].apply(lambda x: str(x)).astype(str)
        elif str(geodataframe.dtypes[col]) == 'geometry':
            geodataframe[col] = geodataframe[col].apply(convert_to_wkt).astype(str)
    return geodataframe


def process_and_ingest_partition(s3_client, key, feature_group):
    """Descarga, procesa e ingesta un archivo particionado específico"""
    file_name = os.path.basename(key)
    # --- CÓDIGO CORREGIDO MULTIPLATAFORMA ---
    temp_dir = tempfile.gettempdir()
    local_parquet_path = os.path.join(temp_dir, file_name)
    # ----------------------------------------
    
    print(f"Descargando {file_name} desde s3://{SHAPES_BUCKET}/{key} ...")
    s3_client.download_file(SHAPES_BUCKET, key, local_parquet_path)

    print(f"Leyendo GeoParquet de {file_name} con GeoPandas...")
    gdf = gpd.read_parquet(local_parquet_path)

    if gdf.crs is None:
        gdf.set_crs("EPSG:3116", inplace=True)
    elif gdf.crs != "EPSG:3116":
        gdf = gdf.to_crs("EPSG:3116")

    gdf = fix_columns_dtypes(gdf)
    gdf.columns = gdf.columns.str.lower()
    gdf = set_record_event_time(gdf, record_event_time_name)
    
    print(f"Ingestando {len(gdf)} registros de {file_name} al Feature Store...")
    feature_group.ingest(data_frame=gdf, max_workers=8, wait=True)
    
    if os.path.exists(local_parquet_path):
        os.remove(local_parquet_path)


def main():
    # 1. Definición del Feature Group
    sagemaker_feature_group = FeatureGroup(name=feature_group_name,
                                           sagemaker_session=sagemaker_session)
    try:
        sagemaker_feature_group.describe()
    except Exception as err:
        print(f"Ha ocurrido un error accediendo al Feature Group: {feature_group_name}")
        raise err

    # 2. Listar archivos particionados usando la RUTA REAL (DANE_PARQUET_PREFIX)
    print("Buscando particiones en S3...")
    parquet_keys = list_parquet_files(SHAPES_BUCKET, DANE_PARQUET_PREFIX)
    
    if not parquet_keys:
        print("No se encontraron archivos .parquet particionados en la ruta especificada.")
        return
    
    print(f"Se encontraron {len(parquet_keys)} archivos particionados para procesar.")
    
    # 3. Iterar sobre cada archivo e ingestar
    s3_client = boto3.client('s3', region_name=region)
    for index, key in enumerate(parquet_keys):
        print(f"--- Procesando archivo {index + 1} de {len(parquet_keys)} ---")
        process_and_ingest_partition(s3_client, key, sagemaker_feature_group)
        
    print("Ingesta completa exitosamente.")


if __name__ == '__main__':
    main()