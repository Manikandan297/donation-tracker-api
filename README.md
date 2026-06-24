# 💜 DonateFlow — Donation Management API

A full-stack Donation Management system built with **FastAPI** (Backend) and **Vanilla HTML/CSS/JS** (Frontend).

---

## 🚀 Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python 3.x |
| Database | SQLite + SQLAlchemy ORM |
| Validation | Pydantic v2 |
| Server | Uvicorn (ASGI) |
| Frontend | HTML5, CSS3, Vanilla JS |

---

## ✨ Features

- ✅ **Idempotent Transactions** — Same `request_id` submitted twice → `409 Conflict`
- ✅ **Input Validation** — Amount > 0, User ID > 0, non-blank Request ID
- ✅ **Dependency Injection** — `Depends(get_db)` for automatic session management
- ✅ **Pagination** — `page` & `page_size` query params on all list endpoints
- ✅ **CORS Enabled** — Frontend can connect without browser errors
- ✅ **Timestamps** — Every transaction records `created_at` automatically
- ✅ **SQL Aggregation** — Summary uses `func.sum()` / `func.count()` for performance
- ✅ **Beautiful Frontend** — Dark mode dashboard with live stats

---

## 📁 Project Structure

```
backend_assingment/
│
├── app1.py          # Main FastAPI application (7 endpoints)
├── database.py      # DB engine, session, get_db() dependency
├── models.py        # SQLAlchemy ORM model (Transaction)
├── schemas.py       # Pydantic request/response schemas
├── requirment.txt   # Python dependencies
├── index.html       # Frontend dashboard
└── .gitignore       # Git ignore rules
```

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/transaction` | Create a new transaction (idempotent) |
| `GET` | `/transactions` | List all transactions (paginated) |
| `GET` | `/transaction/{id}` | Get single transaction by ID |
| `GET` | `/transactions/user/{user_id}` | Get user's transactions (paginated) |
| `GET` | `/summary/{user_id}` | Get total amount & count for a user |
| `DELETE` | `/transaction/{id}` | Delete a transaction |
| `GET` | `/health` | Health check |

---

## ⚙️ Setup & Run

### 1. Install dependencies
```bash
pip install -r requirment.txt
```

### 2. Start the backend server
```bash
uvicorn app1:app --reload
```

### 3. Open the frontend
Double-click `index.html` or open in browser.

### 4. View API docs
```
http://127.0.0.1:8000/docs
```

---

## 📸 Frontend Pages

| Page | Description |
|---|---|
| 📊 Dashboard | Live stats — total donations, unique donors, avg, top donors |
| 📋 Transactions | All transactions with search, pagination & delete |
| 💸 New Donation | Submit donation form with auto-generated request ID |
| 👤 User Summary | View total donated amount per user |
| 🔍 Lookup | Find transaction by ID or view user's all transactions |

---

## 🛡️ Idempotency Example

```bash
# First request → 201 Created ✅
POST /transaction
{ "user_id": 1, "amount": 500, "request_id": "TXN-001" }

# Same request again → 409 Conflict ⚠️
POST /transaction
{ "user_id": 1, "amount": 500, "request_id": "TXN-001" }
```

---

## 👨‍💻 Author

Built as part of a Backend Development Internship Assignment.
