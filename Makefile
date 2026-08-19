.PHONY: up down restart logs build clean reset help

# Подключение переменных окружения из файла .env
include .env

# Путь к docker-compose.yml
DOCKER_COMPOSE ?= $(DOCKER_COMPOSE_CMD) -f docker/docker-compose.yml --env-file .env

help: ## Показать список всех команд
	@echo "Доступные команды:"
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Запуск всех сервисов
	$(DOCKER_COMPOSE) up -d

down: ## Остановка всех сервисов
	$(DOCKER_COMPOSE) down

restart: ## Перезапуск сервисов
	$(MAKE) down && $(MAKE) up

logs: ## Просмотр логов
	$(DOCKER_COMPOSE) logs -f

build: ## Сборка образов без использования кэша
	$(DOCKER_COMPOSE) build --no-cache

clean: ## Остановка и удаление volumes
	$(DOCKER_COMPOSE) down -v

reset: ## Остановка, удаление тома Mongo и очистка ./data
	$(DOCKER_COMPOSE) down -v --remove-orphans --timeout 10
	-docker volume rm $(PROJECT_NAME)-mongo_data
	rm -rf data