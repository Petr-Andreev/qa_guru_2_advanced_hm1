# qa_guru_v1
Python autotesting advanced

### Объяснение структуры `README.md`

1. **Предварительные условия:** 
   - Убедитесь, что у вас установлено следующее:
   - Python 3.12 или выше;
   - `pip` for package management;
   - `uvicorn` for running the FastAPI server;
   - `pytest` for running tests;
   - `pytest-xdist` for parallel test execution;

Вы можете установить необходимые пакеты, запустив:

```bash
pip install fastapi uvicorn pytest pytest-xdist requests
```

2. **Как запустить сервер FastAPI:**
   - Инструкция по запуску FastAPI сервера с использованием `uvicorn`.
```bash
uvicorn app.main:app --reload 
```
   - Также есть возможность использовать SWAGGER:
   - В поисковую строку браузера нужно прописать: http://127.0.0.1:8000/docs

3. **Как запускать тесты:**
   - Параллельный запуск API тестов на окружениях PROD и TEST, прописать в консоли:
```bash
pytest
```