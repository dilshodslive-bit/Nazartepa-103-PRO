# Nazartepa 103 — Frontend

Operator dispetcherlik paneli. **Next.js 14 (App Router) + TypeScript + TailwindCSS +
React-Leaflet**. O'zbek tilida.

## Imkoniyatlar

- **Login** — backend JWT auth (`/api/v1/auth/login`)
- **Murojaatlar ro'yxati** — jonli (har 5s yangilanadi), AI triaj tavsiyasi
  (ustuvorlik, tavsiya etilgan brigada, ishonchlilik) bilan
- **Amallar** — murojaatni triaj qilish va eng yaqin brigadani tayinlash
- **Jonli xarita (Leaflet)** — ambulanslar va murojaatlar; brigada GPS'i
  `/ws/dispatch` WebSocket orqali real vaqtda yangilanadi

## Ishga tushirish

Backend `http://localhost:8000` da ishlab turishi kerak (asosiy `docker compose up`).

```bash
cd frontend
npm install
cp .env.example .env.local   # kerak bo'lsa manzillarni sozlang
npm run dev                  # http://localhost:3000
```

Kirish: `admin@nazartepa.uz` / `Admin12345!` (backend seed super-admin).

## Tuzilma

- `app/` — App Router sahifalari (login, dashboard)
- `components/` — CallList, MapView (Leaflet), PriorityBadge
- `lib/` — API klient, auth konteksti, WebSocket hook, tiplar, i18n
