# 🔎 SearchGrid — Distributed Search & Indexing Platform

SearchGrid is a beginner-friendly project that shows how a search system works behind the scenes.

Imagine an online shopping website. It may have thousands of products. When someone searches for **"wireless headphones"**, the website should quickly find useful products instead of checking every product one by one.

SearchGrid is a backend that helps make this possible. It stores information, prepares it for searching, finds matching results, and returns them through simple API endpoints.

The project is built with **Python, FastAPI, PostgreSQL, Elasticsearch, Kafka, Redis, and Docker**.

---

## 📌 1. What does SearchGrid do?

SearchGrid lets an application:

- Add documents, products, or articles.
- Update or delete stored information.
- Search for words inside titles, content, and tags.
- Sort and filter search results.
- Add many documents at once.
- Cache popular searches to make repeated requests faster.

You can think of it as the search backend of an online store, document library, or article website.

---

## 🧠 2. Understand the technologies in simple words

| Technology | What it does in SearchGrid |
|---|---|
| **Python** | The programming language used to build the backend. |
| **FastAPI** | Receives requests and sends responses through API endpoints. |
| **PostgreSQL** | Saves the original documents safely. |
| **Elasticsearch** | Finds matching documents quickly when someone searches. |
| **Kafka** | Carries messages about new, updated, or deleted documents. |
| **Redis** | Temporarily saves search results so repeated searches can be faster. |
| **Docker Compose** | Starts the API and all supporting services together. |
| **Pytest** | Runs automated tests to check parts of the application. |

### Why do we need both PostgreSQL and Elasticsearch?

They have different jobs:

- **PostgreSQL** is the main storage. It keeps the original document data.
- **Elasticsearch** creates a search-friendly copy of that data.

PostgreSQL is the source of truth. Elasticsearch is used to search that information efficiently.

### What is an inverted index?

An inverted index is a way of organizing words so a search engine can quickly find which documents contain them.

For example:

| Word | Documents containing that word |
|---|---|
| laptop | Document 1, Document 3 |
| wireless | Document 2, Document 3 |
| keyboard | Document 1 |

Instead of reading every document from beginning to end for each search, the search engine can look up the words in its index.

---

## 🏗️ 3. How does SearchGrid work?

Here is the basic journey when a new document is added:

```text
       User / Application
               |
               v
          FastAPI
               |
               v
          PostgreSQL
       (Save document)
               |
               v
       Outbox Event
      (Save the change)
               |
               v
       Indexing Worker
               |
               v
             Kafka
       (Event message)
               |
               v
        Elasticsearch
        (Search index)
```

When a user searches:

```text
       User Search
            |
            v
          FastAPI
            |
            v
       Redis Cache
        /       \
      Found    Not Found
        |          |
        v          v
     Return    Elasticsearch
     Result        |
                   v
               Save result
               in Redis
                   |
                   v
               Return result
```

**What is an outbox event?**

Whenever a document is added or changed, SearchGrid saves both the document and a small record describing that change in the same database transaction.

The background worker reads those records and processes them. This helps avoid losing indexing work when a service is temporarily unavailable.

**What is eventual consistency?**

The document is saved in PostgreSQL first. Elasticsearch receives the update shortly afterwards through the background worker. Therefore, a newly added document may take a short time to appear in search results.

---

## ✨ 4. Main features

### Document management
Create, view, update, and delete documents using API requests.

### Full-text search
Search for words in document titles, content, and tags.

### Search ranking
Search results use Elasticsearch relevance scoring. Title matches receive a higher field weight than content matches.

### Filters and sorting
Narrow results by document type or tags. Sort results by relevance, newest, or oldest.

### Search aggregations
Get counts grouped by document type and tags. These can help build filters and search dashboards.

### Bulk document creation
Submit multiple documents in a single API request.

### Redis caching
Save search responses temporarily. Repeated requests can reuse the cached response until it expires or is invalidated.

### Background indexing
Process document changes outside the main API request, using a worker and an outbox event pipeline.

---

## 💻 5. Project folder structure

```text
SearchGrid/
│
├── app/
│   ├── api/
│   │   └── routes.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── db/
│   │   ├── models.py
│   │   └── session.py
│   │
│   ├── schemas/
│   │   └── document.py
│   │
│   ├── services/
│   │   ├── cache.py
│   │   ├── documents.py
│   │   └── search.py
│   │
│   ├── workers/
│   │   └── indexer.py
│   │
│   └── main.py
│
├── scripts/
│   └── create_index.py
│
├── tests/
│   └── test_documents.py
│
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
└── README.md
```

### What do these folders contain?

- `api/` — API endpoints that receive user requests.
- `core/` — Application settings and configuration.
- `db/` — Database connection and table definitions.
- `schemas/` — Rules for validating incoming and outgoing data.
- `services/` — Main document, search, and cache logic.
- `workers/` — Background processing for indexing.
- `scripts/` — Helper scripts for Elasticsearch.
- `tests/` — Automated tests.

---

## ⚙️ 6. How to run SearchGrid on your computer

### Requirements

Install these before starting:

1. **Python 3.12 or later in the 3.12 series** (the Docker image uses Python 3.12).
2. **Docker Desktop**.
3. **Git**.
4. **Visual Studio Code** (recommended).

You do not need to install PostgreSQL, Elasticsearch, Kafka, or Redis separately. Docker Compose starts them for you.

### Step 1 — Download the project

Open PowerShell or the VS Code terminal:

```powershell
git clone https://github.com/Kushagrarai09/SearchGrid.git
```

Go into the project folder:

```powershell
cd SearchGrid
```

### Step 2 — Create the environment file

Run:

```powershell
Copy-Item .env.example .env
```

The `.env` file contains the settings used by the application and its services.

For this local learning setup, the example values are ready to use. Do not use these sample passwords or unsecured settings for a public production deployment.

### Step 3 — Start Docker Desktop

Open Docker Desktop and make sure it is running.

### Step 4 — Start all services

Run:

```powershell
docker compose up --build
```

Docker Compose builds the application image and starts:

- FastAPI application
- PostgreSQL database
- Elasticsearch search engine
- Kafka message broker
- Redis cache
- Background indexing worker

The first startup may take a little longer because Docker needs to download the images.

### Step 5 — Open the API documentation

Once the API has started, open:

**http://localhost:8000/docs**

This page lets you explore and test the API directly from your browser.

### Step 6 — Check service health

Open:

**http://localhost:8000/health**

The response shows whether PostgreSQL, Redis, and Elasticsearch are reachable by the API.

### Stop the application

In the terminal, press `Ctrl + C`, then run:

```powershell
docker compose down
```

To stop the services and also delete their saved Docker volumes (this deletes local database and search data), run:

```powershell
docker compose down -v
```

---

## 🚀 7. Try the API

You can test these endpoints in Swagger at **http://localhost:8000/docs**.

### A. Add a document

Endpoint:

`POST /api/v1/documents`

Example JSON:

```json
{
  "title": "Learning Distributed Systems",
  "content": "Distributed systems use multiple computers to work together. Kafka helps services communicate through events.",
  "kind": "article",
  "tags": ["backend", "distributed-systems"],
  "metadata": {
    "author": "Kushagra"
  }
}
```

The API saves the document in PostgreSQL and creates an indexing event for the background worker.

### B. Search for a document

Endpoint:

`GET /api/v1/search`

Example:

```text
http://localhost:8000/api/v1/search?q=Kafka
```

Search for a particular type:

```text
http://localhost:8000/api/v1/search?q=Kafka&kind=article
```

### C. Add multiple documents

Endpoint:

`POST /api/v1/documents/bulk`

Example JSON:

```json
{
  "documents": [
    {
      "title": "Redis Basics",
      "content": "Redis is an in-memory data store.",
      "kind": "article",
      "tags": ["redis", "backend"]
    },
    {
      "title": "Elasticsearch Basics",
      "content": "Elasticsearch is used for full-text search.",
      "kind": "document",
      "tags": ["search", "backend"]
    }
  ]
}
```

### D. Other available endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/documents` | Create a document |
| GET | `/api/v1/documents/{id}` | Get a document |
| PUT | `/api/v1/documents/{id}` | Update a document |
| DELETE | `/api/v1/documents/{id}` | Delete a document |
| POST | `/api/v1/documents/bulk` | Create multiple documents |
| GET | `/api/v1/search` | Search documents |
| GET | `/health` | Check service health |

---

## 🧪 8. Run the tests

Create a virtual environment and install the dependencies if you want to run tests directly on your computer:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
```

If PowerShell blocks activation, you can run the test command through the environment's Python executable without activating it:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

The current tests cover basic request-schema validation. They do not replace full integration tests with live PostgreSQL, Kafka, Elasticsearch, and Redis services.

---

## 🎯 9. What you can learn from this project

By exploring SearchGrid, you can practise:

1. Building REST APIs with Python and FastAPI.
2. Saving data with PostgreSQL and SQLAlchemy.
3. Understanding inverted indexes and full-text search.
4. Creating Elasticsearch indexes and search queries.
5. Understanding search relevance and ranking.
6. Sending and processing events with Kafka.
7. Using background workers and the transactional outbox pattern.
8. Caching responses with Redis.
9. Running multiple backend services with Docker Compose.
10. Testing application code with Pytest.

---

## 🔧 10. Future improvements

SearchGrid is a learning-focused MVP. The following improvements would make it more suitable for larger and real-world workloads:

- Add user authentication, roles, and API keys.
- Add Alembic database migrations.
- Use Elasticsearch bulk indexing for more efficient large imports.
- Add Kafka dead-letter queues and event replay tools.
- Add worker concurrency controls and safer event claiming.
- Add Elasticsearch index aliases and a reindexing process.
- Add monitoring, logs, metrics, and distributed tracing.
- Add integration tests and performance/load tests.
- Configure TLS, secure credentials, backups, and production deployment settings.

---

## 👨‍💻 Author

**Kushagra Rai**

GitHub: [@Kushagrarai09](https://github.com/Kushagrarai09)

---

## ⭐ Support

If you find this project useful for learning backend development, distributed systems, or search-engine architecture, consider giving the repository a star.

**SearchGrid — Make information easy to find.**
