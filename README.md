# Proyecto #1 - Tópicos Especiales de Telemática

## Video

(https://youtu.be/BeJv_tnxkK0?si=cuIZi1YkV-3_yDq1)

## Integrantes

- Diego Alexander Munera
- Moises David Arrieta Hernandez
- Alberto Andres Diaz Mejia
- Andres Felipe Rua Ortega
- Holmer Ortega Gomez
  
## Descripción del Proyecto
Este proyecto implementa un sistema de archivos distribuidos por bloques, diseñado para permitir el acceso concurrente a archivos distribuidos en múltiples nodos. Inspirado en sistemas como Google File System (GFS) y Hadoop Distributed File System (HDFS), nuestro sistema se enfoca en proporcionar un DFS minimalista con características de escritura y lectura a nivel de bloque y transparencia en el acceso a archivos tanto locales como remotos.

### Problema
Los sistemas de archivos tradicionales enfrentan limitaciones en cuanto a escalabilidad y fiabilidad cuando se manejan grandes volúmenes de datos distribuidos geográficamente. Este proyecto busca superar estas limitaciones mediante la distribución de archivos en bloques a través de varios nodos, mejorando así la disponibilidad y el rendimiento.

### Solución
Nuestro DFS permite:
- **Distribución de Bloques**: Los archivos se dividen en bloques que se distribuyen en diferentes nodos, optimizando el acceso y la redundancia.
- **Transparencia**: Integración con el sistema de gestión de archivos del sistema operativo, permitiendo a los usuarios acceder a archivos remotos como si fueran locales.
- **Escalabilidad y Tolerancia a Fallos**: Replicación de bloques en múltiples nodos para garantizar la disponibilidad y la integridad de los datos.

## Arquitectura del Sistema
![TTelematica](https://github.com/user-attachments/assets/1fce5d28-ae82-4ff5-a801-de97db5e0f13)

El sistema está compuesto por los siguientes componentes:
- **Cliente**: Interfaz CLI/API que permite a los usuarios interactuar con el sistema de archivos.
- **NameNode**: Gestiona el espacio de nombres del sistema de archivos y regula el acceso a los archivos.
- **DataNode**: Almacena los datos efectivos y maneja las operaciones de lectura y escritura a nivel de bloque.

## Tecnologías Utilizadas
- **Python**: Lenguaje principal para la implementación del servidor y cliente.
- **gRPC**: Utilizado para la comunicación entre los diferentes componentes del sistema.
- **Docker**: Para contenerizar y desplegar fácilmente los componentes del sistema.

## Instalación y Configuración
### Requisitos Previos
Asegurarse de tener Python y Docker instalados en tu sistema.

sudo apt update sudo apt install python3 python3-pip docker docker-compose
clonar el repositorio
### Ejecución del Sistema
Utilizar Docker para construir y ejecutar el sistema:
docker-compose up --build
## Uso del Sistema
Para interactuar con el sistema de archivos, puedes utilizar la interfaz CLI o hacer llamadas a la API. Ejemplos de comandos:
- **listar archivos:** dfs_cli ls
- **Subir archivo:** dfs_cli put mi_archivo.txt
- **Descargar archivo** dfs_cli get mi_archivo.txt 

# Conectarse a las instancias si la llave esta en el mismo directorio (ojo no subir la llave a github)
 
- Namenode: ssh -i "nodes.pem" ubuntu@ec2-34-203-26-116.compute-1.amazonaws.com
- Datanode1: ssh -i "nodes.pem" ubuntu@ec2-34.205.35.127.compute-1.amazonaws.com
- Datanode2: ssh -i "nodes.pem" ubuntu@ec2-18-213-115-89.compute-1.amazonaws.com
- Datanode3: ssh -i "nodes.pem" ubuntu@ec2-3-236-192-52.compute-1.amazonaws.com

# Conectarse a las intancias si la llave esta en ~/.ssh

- Namenode: ssh -i ~/.ssh/nodes.pem ubuntu@ec2-34-203-26-116.compute-1.amazonaws.com
- Datanode1: ssh -i ~/.ssh/nodes.pem ubuntu@ec2-34.205.35.127.compute-1.amazonaws.com
- Datanode2: ssh -i ~/.ssh/nodes.pem ubuntu@ec2-18-211-99-187.compute-1.amazonaws.com
- Datanode3: ssh -i ~/.ssh/nodes.pem ubuntu@ec2-44-221-145-22.compute-1.amazonaws.com

# Identificadores de los datanodes:

- Datanode1: ip35127dt01c0
- Datanode2: ip99187dt02c0
- Datanode3: ip14522dt01c1

# Montar e inicializar los contenedores
sudo docker compose -f docker-compose.namenode.yml up
sudo docker compose -f docker-compose.datanode.yml up

# Para cargar un archivo en un datanode

python main.py create -out resources/mid_files -in resources/big_files -f nombredelarchivo

Para que el comando funcione asi deben estar parados en la ruta del cliente: Proyecto1-DFS/client

# Para abrir un archivo que hay en los datanode

python main.py open -out resources/downloaded_files -f nombredelarchivo

# Para listar los archivos que hay en el momento

python main.py ls

Para que el comando funcione asi deben estar parados en la ruta del cliente: Proyecto1-DFS/client

# Para agregar datos a un archivo que ya existe

python main.py append -out resources/splitted_files -in resources/big_files -f nombredelarchivo2 -fdfs nombredelarchivo1

# Si hay problemas con los contenedores

## Detener el contenedor en ejecución
docker-compose -f docker-compose.datanode.yml down

## Reconstruir la imagen y reiniciar el contenedor
docker-compose -f docker-compose.datanode.yml up --build -d

## Si solo necesita reiniciar el contenedor sin reconstruir
docker-compose -f docker-compose.datanode.yml restart

## Si necesita forzar la reconstrucción de la imagen desde cero
docker-compose -f docker-compose.datanode.yml build --no-cache
docker-compose -f docker-compose.datanode.yml up -d

## Para eliminar todas las imágenes no utilizadas
docker image prune -a

## Para eliminar todos los contenedores detenidos, redes no utilizadas, imágenes colgantes y caché de construcción
docker system prune


