# Resumen de Arquitectura: Pipeline de Datos Geográficos (DANE)

## Objetivo del Proyecto
Este proyecto funciona como una **fábrica automatizada de datos en AWS**. Su propósito principal no es el entrenamiento de modelos de Machine Learning, sino la **preparación y disponibilización de información geográfica del DANE** (específicamente manzanas y municipios de Colombia). 

El objetivo final es que cualquier modelo analítico de Nutresa (por ejemplo, predicciones de ventas por zona) pueda consultar esta información de manera rápida, estandarizada y sin reprocesos.

---

## Flujo de Trabajo y Arquitectura

El flujo automatizado se compone de 4 piezas clave, ilustradas en el siguiente esquema:

```text
 ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌────────────────────────┐
 │   1. EL RELOJ   │  ==>  │  2. EL BOTÓN    │  ==>  │  3. LA MÁQUINA  │  ==>  │ 4. LA BIBLIOTECA       │
 │   EventBridge   │       │     Lambda      │       │    SageMaker    │       │     Feature Store      │
 │  (Cada mes)     │       │ (src/lambdas/)  │       │ (src/features/) │       │ (S3 Data Lake)         │
 └─────────────────┘       └─────────────────┘       └─────────────────┘       └────────────────────────┘
```

### 1. El Reloj (Amazon EventBridge)
Actúa como el cronómetro en la nube del proyecto. Está configurado para activarse automáticamente con una periodicidad **mensual**, garantizando que los datos se actualicen de forma regular sin intervención manual.

### 2. El Botón de Encendido (AWS Lambda)
Ubicado en `src/lambdas/`. Cuando EventBridge se activa, hace un llamado a esta función Lambda. 
* **Función:** Actúa como un disparador (trigger). No realiza cálculos pesados; simplemente inicia el proceso en SageMaker pasándole las variables de entorno necesarias (ej. conexiones a bases de datos).

### 3. La Máquina de Procesamiento (Amazon SageMaker)
Ubicado en `src/features/DataMaestraDaneShapes/main.py`. Es el motor principal donde ocurre la transformación de los datos. SageMaker levanta una instancia temporal con capacidad de memoria suficiente para ejecutar el script de procesamiento:
* **Extracción:** Descarga el consolidado de manzanas (`MGN_URB_MANZANA_CLEAN.parquet`) desde el Data Lake en Amazon S3.
* **Transformación Espacial:** Asegura que toda la cartografía utilice el sistema de coordenadas oficial de Colombia (EPSG:3116).
* **Traducción de Geometrías:** Convierte los polígonos geográficos a un formato de texto estándar y procesable (ej. `POLYGON ((...))`).
* **Estandarización:** Limpia y formatea los datos para su consumo.

### 4. La Biblioteca (SageMaker Feature Store)
Una vez procesados los datos, el script los almacena en el **Feature Store**. Este es un catálogo de datos centralizado y organizado. 
* **Beneficio:** Cuando un científico de datos de Nutresa necesita consultar información geográfica para un cliente o modelo, simplemente la extrae del Feature Store de forma inmediata, evitando volver a procesar archivos espaciales pesados.

---

## Infraestructura como Código (IaC)

### ¿Qué hacen `app.py` y `mlops_skeleton`?
Estos archivos son los **planos de construcción** del proyecto utilizando **AWS CDK** (Cloud Development Kit). 

En lugar de crear la infraestructura manualmente a través de la consola web de AWS, este código en Python automatiza el despliegue. Al ejecutarlo, AWS despliega de forma automática y estandarizada todos los recursos necesarios: las funciones Lambda, el pipeline de SageMaker, los roles de seguridad (IAM) y las alarmas de monitoreo.

### Actualizacion
Se actualiza el src el el feature por un nuevo codigo con las rutas nuestras de la v5 asi mismo su test queda en vilo la pregunta de que hacer con todo lo realacionado con el SSM.