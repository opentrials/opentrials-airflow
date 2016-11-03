.PHONY: build start stop

all: build start

build:
	docker build --rm -t okibot/opentrials-airflow .

start: stop
	ansible-playbook ansible/deploy_local.yml -e '@ansible/envs/dev.yml'

stop:
ifneq ($(strip $(shell docker ps -q)),)
	docker stop $(shell docker ps -q)
endif
