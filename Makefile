# Make file para DFS en AWS

include .env
export $(shell sed 's/=.*//' .env)

.PHONY: proto-all run-namenode run-datanode deploy-namenode deploy-datanode

# Generacion de archivos proto
proto-all:
	@python -m grpc_tools.protoc -I ./protos --python_out=./protos --pyi_out=./protos --grpc_python_out=./protos ./protos/file.proto

# Ejecucion local (para desarrollo y pruebas)
run-namenode:
	@python namenode/main.py

run-datanode:
	@python datanode/main.py

# Despliegue en AWS
deploy-namenode:
	@echo "Desplegando NameNode en AWS EC2..."
	@scp -i ~/.ssh/nodes.pem -r ./namenode/* ubuntu@$(NAMENODE_IP):/home/ubuntu/namenode/
	@scp -i ~/.ssh/nodes.pem -r ./protos/* ubuntu@$(NAMENODE_IP):/home/ubuntu/protos/
	@scp -i ~/.ssh/nodes.pem ./namenode/.env ubuntu@$(NAMENODE_IP):/home/ubuntu/namenode/.env
	@ssh -i ~/.ssh/nodes.pem ubuntu@$(NAMENODE_IP) "\
        if ! command -v pip &> /dev/null; then \
            curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py; \
        fi && \
        export PYTHONPATH=/home/ubuntu/protos:/home/ubuntu/namenode && \
        cd /home/ubuntu/namenode && python3 -m pip install -r requirements.txt && python3 main.py"


deploy-datanode:
	@echo "Desplegando DataNode en AWS EC2..."
	@scp -i ~/.ssh/nodes.pem -r ./datanode/* ubuntu@$(DATANODE_IP):/home/ubuntu/datanode/
	@scp -i ~/.ssh/nodes.pem -r ./protos/* ubuntu@$(DATANODE_IP):/home/ubuntu/protos/
	@scp -i ~/.ssh/nodes.pem ./datanode/.env ubuntu@$(DATANODE_IP):/home/ubuntu/datanode/.env
	@ssh -i ~/.ssh/nodes.pem ubuntu@$(DATANODE_IP) "\
        if ! command -v pip &> /dev/null; then \
            curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py; \
        fi && \
        export PYTHONPATH=/home/ubuntu/protos:/home/ubuntu/datanode && \
        cd /home/ubuntu/datanode && python3 -m pip install -r requirements.txt && python3 main.py"

# Comando docker (puede ser util para despliegue local o en un entorno de contenedores en AWS)

# Construcción de imágenes Docker
build-namenode:
	@docker build -t namenode-image ./namenode

build-datanode:
	@docker build -t datanode-image ./datanode

run-docker-namenode:
	@docker run \
	--name namenode \
	--env-file namenode/.env \
	--expose 8000 \
	-p 8000:8000 \
	-v $(pwd)/namenode:/app \
	--network proyecto-1 \
	your_preferred_image_name \
	python main.py

run-docker-datanode:
	@docker run \
    --name datanode \
    --env-file datanode/.env \
    --expose 8001 \
    -p 8001:8001 \
    -v $(pwd)/datanode:/app \
    --network proyecto-1 \
    datanode-image \
    python main.py


# Esto se ejecuta con: make proto-all && make deploy-namenode && make deploy-datanode