# Proyecto #1 - Tópicos Especiales de Telemática

## Video

Espacio para el video

## Integrantes

- Diego Alexander Munera
- Moises A
- Andres Rua
- Alberto Diaz
- Holmer Ortega

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


