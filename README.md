# SmartMarket

A smart grocery store management system — a PySide6 desktop app connected to a FastAPI backend with an Azure SQL Server database.

---

## What It Does

SmartMarket gives store managers a full toolkit to run their inventory from a desktop interface:

- **Login** — Google OAuth authentication via Firebase
- **Inventory** — View, add, edit and delete products with cloud image uploads (Cloudinary)
- **Pricing** — Manage product prices and costs
- **Promotions** — Toggle promotions and set discount percentages per product
- **Reports** — Charts and statistics on sales, profit, and inventory value
- **AI Chat** — Natural language assistant powered by HuggingFace models:
  - Ask questions about your inventory in plain text (Text-to-SQL)
  - Analyze product notes for sentiment
  - Write or update records via natural language

---

## Architecture

```
┌─────────────────────┐        HTTP        ┌──────────────────────────┐
│   Client (PySide6)  │ ────────────────►  │   Server (FastAPI)       │
│                     │                    │                          │
│  Login              │                    │  /query  – read routes   │
│  Inventory          │                    │  /command – write routes │
│  Pricing            │                    │  /chat   – AI routes     │
│  Reports            │                    └──────────┬───────────────┘
│  Chat               │                               │ pyodbc
└─────────────────────┘                    ┌──────────▼───────────────┐
                                           │   Azure SQL Server       │
                                           │                          │
                                           │  dbo.readProduct  (CQRS) │
                                           │  dbo.Events       (CQRS) │
                                           └──────────────────────────┘
```

The backend follows a **CQRS** pattern — reads go to a denormalized `readProduct` table, while writes are recorded as events in the `Events` table and projected onto `readProduct`.

---

## Project Structure

```
SmartMarket/
├── start.sh                  # One-command startup (Mac/Linux)
├── start.bat                 # One-command startup (Windows)
├── docker-compose.yml        # Docker setup for the server
│
├── client/                   # Desktop app (PySide6)
│   ├── main.py
│   ├── requirements.txt
│   ├── .env                  # (not in git — see .env.example)
│   ├── loginWindow/          # Google OAuth login screen
│   ├── inventory/            # Product management screen
│   ├── pricing/              # Pricing management screen
│   ├── reports/              # Charts and statistics
│   ├── Chat/                 # AI assistant screen
│   └── mainDashboard/        # Main navigation
│
└── server/                   # API server (FastAPI)
    ├── app.py
    ├── requirements.txt
    ├── Dockerfile
    ├── .env                  # (not in git — see .env.example)
    ├── create_tables.sql     # DB schema
    ├── seed_data.py          # Seed script for test data
    ├── common/               # DB connection
    ├── readFrom/             # Query (read) routes
    ├── writeTo/              # Command (write) routes
    └── chat/                 # AI chat routes
```

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — for running with Docker
- Python 3.10+ — for running without Docker
- An **Azure SQL Server** database with the tables from `server/create_tables.sql`
- A [HuggingFace](https://huggingface.co) account and API token
- A [Cloudinary](https://cloudinary.com) account
- A [Firebase](https://firebase.google.com) project with Google OAuth enabled

---

## Quickest Option — Client Only (Server is Live)

The server is already deployed at **https://smartmarket-1.onrender.com** — you don't need to run it yourself.

Just set up the client with that URL:

1. Create `client/.env` (see `client/.env.example`) and set:
```env
URL=https://smartmarket-1.onrender.com
```

2. Run the client:
```bash
cd client
python -m venv venv

# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install -r requirements.txt
python main.py
```

That's it — no Docker, no server setup needed.

---

## Running with Docker (Self-hosted)

### 1. Fill in environment files

Create `server/.env` (see `server/.env.example`) and `client/.env` (see `client/.env.example`).

### 2. Run

**Mac / Linux:**
```bash
./start.sh
```

**Windows:**
```bat
start.bat
```

`start.sh` / `start.bat` will:
1. Build and start the server in Docker
2. Create a Python virtual environment for the client (if one doesn't exist)
3. Install client dependencies
4. Launch the desktop app

---

## Running Without Docker

### Server

```bash
cd server
python -m venv venv

# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install -r requirements.txt
uvicorn app:app --reload
```

Server runs on `http://localhost:8000` — API docs at `http://localhost:8000/docs`.

> **Note (Mac/Linux):** You must have the Microsoft ODBC Driver installed:
> - macOS: `brew install msodbcsql18`
> - Linux: [Microsoft docs](https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server)

### Client

```bash
cd client
python -m venv venv

# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install -r requirements.txt
python main.py
```

### Order of startup

1. Start the **server** first
2. Start the **client**
3. Log in with a Google account

---

## API Overview

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/query/products` | List all products |
| GET | `/query/products/{id}` | Get a single product |
| GET | `/query/products/{id}/events` | Full event history for a product |
| GET | `/query/products_profit` | Profit per product |
| GET | `/query/products_category_value` | Inventory value by category |
| GET | `/query/products_total_profit_per_month` | Monthly profit totals |
| GET | `/query/products/distinct/brands` | All distinct brands |
| GET | `/query/products/distinct/categories` | All distinct categories |
| POST | `/command/product/create` | Create a new product |
| PUT | `/command/product/{id}/update` | Update product fields |
| DELETE | `/command/product/{id}/delete` | Delete a product |
| POST | `/command/product/{id}/purchase` | Record a stock purchase |
| POST | `/command/product/{id}/sale` | Record a sale |
| POST | `/command/product/{id}/change_price` | Change price or cost |
| POST | `/command/product/{id}/set_promotion` | Set/remove a promotion |
| POST | `/command/product/{id}/add_note` | Add a note to a product |
| POST | `/chat/analyze_note` | Sentiment analysis on a note |
| POST | `/chat/ask` | Natural language query / action |

Full interactive docs: `http://localhost:8000/docs`

---

## Database Setup

Run `server/create_tables.sql` on your Azure SQL database before first use.

To populate test data (≈150 products, 2000+ events):
```bash
cd server
source venv/bin/activate   # or venv\Scripts\activate on Windows
python seed_data.py
```

---

## Environment Variables

See `server/.env.example` and `client/.env.example` for the full list of required variables.
