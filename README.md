# Document Search Service

Простой асинхронный сервис полнотекстового поиска документов.

Сервис получает текстовый поисковый запрос, выполняет поиск через Elasticsearch, возвращает до 20 подходящих документов с полными данными из PostgreSQL и поддерживает удаление документа одновременно из PostgreSQL и Elasticsearch.

## Стек

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0
- asyncpg
- Elasticsearch
- Pydantic
- pytest
- httpx

## Архитектура

PostgreSQL используется как основное хранилище документов.

В PostgreSQL хранятся:

- `id`
- `rubrics`
- `text`
- `created_date`

Elasticsearch используется как поисковый индекс.

В Elasticsearch хранятся:

- `id`
- `text`
- `created_date`

Общая схема поиска:

```text
HTTP request
    ↓
FastAPI
    ↓
Service layer
    ↓
Elasticsearch
    ↓
поиск по text
    ↓
сортировка по created_date
    ↓
limit 20
    ↓
получение document IDs
    ↓
PostgreSQL
    ↓
получение полных документов
    ↓
HTTP response
```

Таким образом Elasticsearch отвечает за полнотекстовый поиск, а PostgreSQL остаётся основным источником данных.

## Отличие от исходного задания

В исходном задании для Elasticsearch указана структура индекса:

```text
id
text
```

В реализации дополнительно добавлено поле:

```text
created_date
```

Это сделано намеренно для оптимизации поиска.

По условиям необходимо вернуть первые 20 найденных документов, отсортированных по дате создания.

Если хранить в Elasticsearch только `id` и `text`, Elasticsearch сможет найти подходящие документы, но не сможет отсортировать их по `created_date`.

В таком случае пришлось бы:

1. получить из Elasticsearch большое количество подходящих ID;
2. передать все эти ID в PostgreSQL;
3. выполнить сортировку в PostgreSQL;
4. только после этого ограничить результат до 20 документов.

В текущей реализации Elasticsearch сразу выполняет:

```text
search
→ sort by created_date
→ limit 20
```

После этого PostgreSQL получает максимум 20 ID и возвращает полные данные документов.

Поэтому структура Elasticsearch содержит одно дополнительное поле `created_date`.

PostgreSQL при этом остаётся основным хранилищем, а Elasticsearch используется только для поиска и предварительной сортировки результатов.

## API

### Поиск документов

```http
GET /documents/search?q=<text>
```

Пример:

```http
GET /documents/search?q=Москва
```

Алгоритм:

1. Elasticsearch выполняет полнотекстовый поиск по полю `text`.
2. Результаты сортируются по `created_date`.
3. Elasticsearch возвращает максимум 20 ID.
4. PostgreSQL возвращает полные данные найденных документов.
5. API возвращает список документов.

Если документы не найдены, возвращается пустой список:

```json
[]
```

### Удаление документа

```http
DELETE /documents/{document_id}
```

Пример:

```http
DELETE /documents/15
```

Документ удаляется из:

- Elasticsearch;
- PostgreSQL.

Если документа не существует, API возвращает `404`.

При успешном удалении возвращается `204 No Content`.

## Настройка проекта

### 1. Создать виртуальное окружение

Windows:

```bash
python -m venv venv
```

Активировать:

```bash
venv\Scripts\activate
```

Для Git Bash:

```bash
source venv/Scripts/activate
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 3. Создать `.env`

В корне приложения создать файл `.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/search_db
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_INDEX=documents
```

Заменить `password` на пароль пользователя PostgreSQL.

### 4. Создать PostgreSQL database

Необходимо создать базу данных:

```text
search_db
```

Например через PostgreSQL:

```sql
CREATE DATABASE search_db;
```

Либо через pgAdmin:

```text
Databases
→ Create
→ Database
→ search_db
```

### 5. Создать таблицы

Из директории приложения выполнить:

```bash
python init_db.py
```

Скрипт создаст необходимые таблицы на основе SQLAlchemy-моделей.

### 6. Запустить Elasticsearch

Для локального запуска можно использовать Docker:

```bash
docker run --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" elasticsearch:8.15.5
```

Проверить доступность Elasticsearch:

```bash
curl http://localhost:9200
```

Если Elasticsearch запущен корректно, будет возвращена информация о кластере.

Если контейнер уже создан, повторно его можно запустить командой:

```bash
docker start elasticsearch
```

### 7. Загрузить исходные данные

CSV-файл необходимо разместить в директории приложения.

При необходимости путь к файлу можно изменить в:

```python
CSV_PATH = "posts.csv"
```

После этого выполнить:

```bash
python load_csv.py
```

Скрипт:

1. читает CSV;
2. преобразует данные;
3. сохраняет документы в PostgreSQL;
4. получает созданный PostgreSQL `id`;
5. индексирует `id`, `text` и `created_date` в Elasticsearch.

Проверить количество документов в Elasticsearch можно командой:

```bash
curl http://localhost:9200/documents/_count
```

### 8. Запустить API

```bash
uvicorn main:app --reload
```

После запуска API доступно по адресу:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## OpenAPI

OpenAPI-схема проекта находится в файле:

```text
docs.json
```

При необходимости её можно сгенерировать заново:

```bash
python -c "import json; from main import app; open('docs.json', 'w', encoding='utf-8').write(json.dumps(app.openapi(), ensure_ascii=False, indent=2))"
```

## Тесты

В проекте присутствуют функциональные тесты API.

Для запуска сначала необходимо поднять приложение:

```bash
uvicorn main:app --reload
```

Затем в другом терминале выполнить:

```bash
pytest -v
```

Тесты проверяют:

- успешный поисковый запрос;
- ограничение количества результатов;
- валидацию пустого поискового запроса.

## Асинхронность

Работа с PostgreSQL выполняется асинхронно через:

```text
SQLAlchemy AsyncSession
asyncpg
```

Работа с Elasticsearch выполняется через:

```text
AsyncElasticsearch
```

HTTP-endpoint'ы FastAPI также реализованы как асинхронные функции.

## Структура проекта

```text
app/
├── api/
│   └── documents.py
│
├── db/
│   ├── models.py
│   ├── schemas.py
│   └── session.py
│
├── elastic/
│   └── client.py
│
├── services/
│   └── service.py
│
├── tests/
│   └── api_test.py
│
├── config.py
├── init_db.py
├── load_csv.py
├── main.py
├── docs.json
├── requirements.txt
├── README.md
└── .env
```

## Основные решения

### PostgreSQL

Используется как основное хранилище документов и содержит все поля документа.

### Elasticsearch

Используется для полнотекстового поиска.

Elasticsearch возвращает только ID подходящих документов, после чего полные данные получаются из PostgreSQL.

### Service layer

Бизнес-логика вынесена из API-роутеров в отдельный service layer.

API отвечает только за обработку HTTP-запросов, а service layer связывает Elasticsearch и PostgreSQL.

### Удаление

При удалении документа сервис удаляет его как из Elasticsearch, так и из PostgreSQL, чтобы данные в двух хранилищах оставались синхронизированными.