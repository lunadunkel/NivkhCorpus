### Запуск

###### линукс/мак
1. зайти в репозиторий в терминале
2. активировать венв или создать
	создать: python -m venv venv
	активировать: source venv/bin/activate
3. установить requirements.txt (если еще нет): pip install -r requirements.txt
4. запустить сервер: uvicorn backend.main:app --reload

### винда
- то же все самое, но для активации сл команда: venv\Scripts\activate