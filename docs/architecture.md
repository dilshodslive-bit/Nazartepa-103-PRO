# Nazartepa 103 — Arxitektura

## Umumiy ko'rinish

Nazartepa 103 — AI asosidagi tez tibbiy yordam **dispatch** platformasi.
Loyiha **modul-monolit** sifatida qurilgan (Domain-Driven Design tamoyillari).
Har bir domen alohida, mustaqil paket. Kelajakda kerak bo'lsa, har qanday
modulni alohida microservice'ga ajratish oson.

## Nima uchun modul-monolit?

- Bitta repo, bitta deploy — rivojlantirish va debagging oson.
- Modullar orasidagi chegaralar aniq (har modulda o'z model/schema/service/router).
- Modullar bir-biriga to'g'ridan-to'g'ri emas, **service** qatlami orqali murojaat qiladi.
- Kerak bo'lganda modulni chiqarib olib, mustaqil xizmat qilish mumkin.

## Qatlamlar

```
router  →  HTTP kirish nuqtasi (FastAPI), so'rov/javob validatsiyasi (Pydantic)
service →  biznes-mantiq (domenlararo yagona kirish nuqtasi)
models  →  SQLAlchemy ORM (ma'lumotlar bazasi jadvallari)
schemas →  Pydantic v2 (I/O shakllari)
```

`core/` — butun ilova bo'ylab umumiy: konfiguratsiya, DB sessiya, xavfsizlik (JWT),
dependency'lar, logging.

`shared/` — modullar bo'ylab qayta ishlatiladigan: Base model, mixinlar
(timestamp, soft-delete), umumiy exceptionlar, pagination.

## Modullar (domenlar)

| Modul | Vazifa | Milestone |
|-------|--------|-----------|
| `auth` | Autentifikatsiya, JWT, RBAC rollar | 1 |
| `users` | Foydalanuvchilar (citizen/operator/dispatcher/doctor/admin) | 1 |
| `emergency` | Murojaat (EmergencyCall) qabul qilish va boshqarish | 2 |
| `ai_triage` | AI severity/priority baholash (provayder-agnostik) | 3 |
| `ambulance` | Brigadalar, GPS, status | 4 |
| `dispatch` | Brigada tayinlash, ETA hisoblash | 4 |
| `realtime` | WebSocket real-time yangilanishlar | 4 |

## Rollar (RBAC)

- `citizen` — fuqaro (Telegram orqali murojaat)
- `operator` — 103 operatori (murojaatlarni ko'radi, AI tavsiyalarini oladi)
- `dispatcher` — brigada tayinlashni boshqaradi
- `doctor` — brigada shifokori (natija kiritadi)
- `admin` — tizim boshqaruvchisi
- `super_admin` — barcha hududlar

## Murojaat status oqimi

```
new → triaged → dispatched → en_route → on_scene → completed
                                                  ↘ cancelled
```

## Texnologiyalar

Backend: FastAPI, SQLAlchemy 2 (async), Alembic, Pydantic v2, PostgreSQL, Redis.
Frontend: Next.js 14 + TypeScript + Tailwind + shadcn/ui + Leaflet.
Bot: aiogram 3.
AI: provayder-agnostik interfeys (rule-based / Ollama / OpenAI / Anthropic).
DevOps: Docker, docker-compose, GitHub Actions, ruff, mypy, pytest.
