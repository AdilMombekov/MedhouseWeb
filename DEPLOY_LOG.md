# Лог деплоя

Дата: 2026-03-12.

---

## Что сделано

### 1. Railway (бэкенд)

- **Привязка:** пользователь выполнил `railway login` и `railway link` из папки `backend` (проект Medhouse-website, окружение production, сервис MedhouseWeb).
- **Деплой:** выполнена команда `railway up --detach` из `d:\Разработка медхаус\backend`.
  - Результат: Indexing → Uploading, ссылка на Build Logs в панели Railway.
- **Домен сервиса:** уже выдан, активен:
  - **https://medhouseweb-production.up.railway.app**
- **Логи (последний запуск):** контейнер стартует, Uvicorn на порту 8080, application startup complete, cache warm-up 6 sources, GET /health 200.

### 2. Git

- Закоммичены: изменения `.gitignore` (добавлена папка `.railway/`), `docs/RAILWAY_CLI.md`, `docs/ЧТО_ТЫ_ОДИН_РАЗ_ЧТО_Я_САМ.md`.
- Коммит: `a671001` — "docs: Railway CLI, deploy one-time steps, .railway in gitignore".
- Выполнен пуш в `origin master`: `72f483c..a671001` → https://github.com/AdilMombekov/MedhouseWeb.git.

### 3. Проверки

- **railway status** из `backend`: Project Medhouse-website, Environment production, Service MedhouseWeb.
- **railway domain**: домен уже существует — https://medhouseweb-production.up.railway.app.
- **railway logs**: в логах виден успешный старт приложения и ответ 200 на GET /health.

---

## Полезные ссылки и команды

| Что | Значение |
|-----|----------|
| **Backend URL** | https://medhouseweb-production.up.railway.app |
| **Health** | https://medhouseweb-production.up.railway.app/health |
| **Репозиторий** | https://github.com/AdilMombekov/MedhouseWeb |
| **Деплой из backend** | `cd backend` → `railway up` (или `railway up --detach`) |
| **Логи** | `railway logs` или `railway logs -n 100` из папки backend |
| **Переменные** | `railway variable list` / `railway variable set KEY=value` |

---

## Что проверить дальше (по желанию)

1. **Vercel (фронт):** если проект подключён к тому же репо — после push мог запуститься автодеплой. В настройках проекта задать **Root Directory** = `frontend`, **VITE_API_BASE** = `https://medhouseweb-production.up.railway.app` (без слеша).
2. **CORS:** в Railway → сервис MedhouseWeb → Variables задать **CORS_ORIGINS** = URL фронта на Vercel (например `https://medhouse-web.vercel.app`), если фронт на другом домене.
3. **БД:** если используешь Railway Postgres или Supabase — переменная **DATABASE_URL** должна быть задана в Railway; один раз выполнить инициализацию (например `python -m scripts.init_db` через Run Command или локально с этим DATABASE_URL).
4. **Health/ready:** открыть в браузере https://medhouseweb-production.up.railway.app/health (и при наличии эндпоинта /health/ready — его тоже).

---

Конец лога.
