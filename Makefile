.PHONY: up down restart logs rebuild clean help

# Путь к docker-compose.yml
DOCKER_COMPOSE := docker compose -f docker/docker-compose.yml

help: ## Показать список всех команд
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Запуск всех сервисов
	$(DOCKER_COMPOSE) up -d

down: ## Остановка всех сервисов
	$(DOCKER_COMPOSE) down

restart: ## Перезапуск сервисов
	down up

logs: ## Просмотр логов
	$(DOCKER_COMPOSE) logs -f

build: ## Сборка образов без использования кэша
	$(DOCKER_COMPOSE) build --no-cache

clean: ## Остановка и удаление volumes
	$(DOCKER_COMPOSE) down -v