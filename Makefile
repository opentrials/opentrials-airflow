.PHONY: build start stop

all: build start

build:
	docker build --rm -t opentrials/opentrials-airflow . -f Dockerfile

start: stop
	ansible-playbook ansible/deploy_local.yml -e '@ansible/envs/dev.yml'

stop:
	docker-compose -f ./ansible/files/docker-compose.yml -f ./ansible/files/docker-compose-local.yml stop
