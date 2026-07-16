# 🚑 Nazartepa 103 — AI-Powered Emergency Medical Dispatch Platform

Tez tibbiy yordam (103) xizmatini raqamlashtirishga qaratilgan platforma.
Fuqaro murojaatini qabul qiladi, **AI yordamida og'irlik darajasini baholaydi**,
eng yaqin brigadani topadi va butun jarayonni **real vaqt rejimida** boshqaradi.

> Arxitektura: **modul-monolit** (Domain-Driven Design). Kelajakda modullar
> alohida microservice'ga ajratilishi mumkin. Batafsil: [`docs/architecture.md`](docs/architecture.md).

## ✨ Imkoniyatlar (bosqichma-bosqich)

- ✅ **Auth + RBAC** — JWT (access/refresh rotation + revocation), 6 rol
- ⬜ **Emergency Call** — murojaat qabul qilish, status oqimi, audit log
- ⬜ **AI Triage** — matndan RED/YELLOW/GREEN priority (rule-based / Ollama / API)
- ⬜ **Dispatch** — eng yaqin brigada, ETA, WebSocket jonli xarita
- ⬜ **Frontend** — Next.js operator dashboard (Leaflet xarita)
- ⬜ **Telegram bot** — aiogram 3 + Mini App

## 🧱 Texnologiyalar

| Qatlam | Texnologiya |
|--------|-------------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2 (async), Alembic, Pydantic v2 |
| DB / Cache | PostgreSQL 16, Redis 7 |
| Frontend | Next.js 14, TypeScript, Tailwind, shadcn/ui, Leaflet |
| Bot | aiogram 3 |
| DevOps | Docker, docker-compose, GitHub Actions, ruff, mypy, pytest |

## 🚀 Ishga tushirish

### Variant A — Docker (tavsiya etiladi)

Butun tizim (Postgres + Redis + Backend) bir buyruq bilan ko'tariladi.
Python'ni lokal o'rnatish shart emas.

```bash
cp .env.example .env         # Windows: copy .env.example .env
docker compose up -d --build
```

- API: <http://localhost:8000>
- Sog'liq: <http://localhost:8000/health>
- Swagger: <http://localhost:8000/docs>

Migratsiyalar konteyner ishga tushganda avtomatik qo'llanadi (`alembic upgrade head`).

### Variant B — Lokal (Docker'siz)

Python 3.12+ va ishlab turgan PostgreSQL + Redis kerak.

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -e ".[dev]"
cp ../.env.example .env       # DATABASE_URL, REDIS_URL ni lokalga moslang
alembic upgrade head
python -m app.scripts.seed    # birinchi super-admin yaratadi
uvicorn app.main:app --reload
```

## 🧪 Testlar

```bash
cd backend
pytest
ruff check .
mypy app
```

## 📁 Struktura

```
Nazartepa103PRO/
├── docker-compose.yml
├── backend/
│   └── app/
│       ├── core/        # config, db, security, deps, logging
│       ├── shared/      # base model, exceptions, pagination
│       └── modules/     # auth, users, emergency, ai_triage, ambulance, dispatch, realtime
├── bot/                 # aiogram 3 (keyingi bosqich)
├── frontend/            # Next.js (keyingi bosqich)
└── docs/
```

## 🗺️ Roadmap

Milestone'lar reja faylida. Hozirgi holat: **M0 (poydevor) + M1 (auth/RBAC)** tayyor.

---

📚 Universitet AI yo'nalishi loyihasi · Portfolio & CV uchun full-stack + AI + DevOps namoyishi.
