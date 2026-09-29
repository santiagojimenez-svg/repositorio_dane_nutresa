El shape que se encuentra en la carpeta "ShapeManzanas" se descarga de los datos abiertos del DANE mas exactamente del "Censo Nacional de Población y Vivienda - CNPV - 2018 | Datos Abiertos Colombia", el cual consistió en contar y caracterizar las personas residentes en Colombia, así como las viviendas y los hogares del territorio nacional.

MGN-Nivel Manzana integrado al CNPV2018 (Pagina donde se descarga):
El shape que se descarga es el que lleva por nombre "MGN-Nivel Manzana integrado al CNPV2018"

https://geoportal.dane.gov.co/servicios/descarga-y-metadatos/datos-geoestadisticos/?cod=4&fbclid=IwAR3qNQn8OOTU440yhXPo-27AmFjoE0Qo5KhCBxnvNStrBDmCPs1X8liCWd4

Por otro lado y aunque en este proceso no es relevante, tambien existe el shape del "Marco Geoestadistico Nacional (MGN)", el cual se descarga de la siguiente página:

https://geoportal.dane.gov.co/servicios/descarga-y-metadatos/descarga-mgn-marco-geoestadistico-nacional/

recordar que el que usa el proyecto es el de "Nivel Geográfico Municipio".

Importante:

ProcesamientoDeShapeDANE.ipynb:

Este script hace el procesamiento del shape completo de colombia y lo divide por códigos de municipio.

-) La lectura del shape es en promedio 26 minutos con 40 segundos. 
-) La carpeta "Manzana" guardará la estructura del procesamiento del shape "MGN-Nivel Manzana integrado al CNPV2018".
