# Деплой: Git → Railway + Supabase → Vercel (одна переменная из Railway)

Пошагово: задеплоить репозиторий на Railway, подключить Supabase, задеплоить фронт на Vercel и в Vercel добавить переменную с URL бэкенда (Railway).

---

## Что делаете вы (в браузере / аккаунтах)

Я не могу зайти в ваши аккаунты Railway, Supabase и Vercel. Ниже — точные шаги, которые вы выполняете сами. Я могу подсказывать по коду и конфигам в репо.

---

## 1. Git

- Код в репозитории (GitHub/GitLab).
- Ветка для деплоя запушена (например `master`).

```bash
git add .
git commit -m "готово к деплою"
git push origin master
```

---

## 2. Supabase (база для Railway)

1. [supabase.com](https://supabase.com) → создать проект (если нет).
2. **Settings → Database** → **Connection string** → **URI**.
3. Подставить пароль в строку:  
   `postgresql://postgres.[ref]:[PASSWORD]@...pooler.supabase.com:6543/postgres`
4. **Скопировать и сохранить** — это будет `DATABASE_URL` для Railway.

---

## 3. Railway (бэкенд из Git)

1. [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo** → выбрать ваш репозиторий.
2. В настройках сервиса:
   - **Root Directory** = `backend`.
3. **Variables** — добавить:
   - `DATABASE_URL` = строка Postgres из Supabase (п. 2).
   - `SECRET_KEY` = случайная строка (например `openssl rand -hex 32`).
   - `CORS_ORIGINS` = URL фронта на Vercel (заполните после п. 4), например `https://ваш-проект.vercel.app`.
4. **Networking** → **Generate Domain** → скопировать URL бэкенда (например `https://medhouse-production.up.railway.app`). **Этот URL понадобится для Vercel.**
5. Один раз инициализировать БД: локально в папке проекта задать `DATABASE_URL` строкой из Supabase и выполнить:
   ```bash
   cd backend
   python -m scripts.init_production_db
   ```
6. Проверка: в браузере открыть `https://ВАШ-RAILWAY-URL/health` и `https://ВАШ-RAILWAY-URL/health/ready`.

---

## 4. Vercel (фронт из Git + переменная «ключ» от Railway)

1. [vercel.com](https://vercel.com) → **Add New** → **Project** → импорт **того же** репозитория.
2. Настройки проекта:
   - **Root Directory** = `frontend`.
   - **Framework Preset** = Vite.
   - **Build Command** = `npm run build`.
   - **Output Directory** = `dist`.
3. **Environment Variables** — добавить переменную со значением от Railway:
   - **Name:** `VITE_API_BASE`
   - **Value:** URL бэкенда Railway **без** слэша в конце, например `https://medhouse-production.up.railway.app`
4. **Deploy**.
5. После деплоя скопировать URL фронта (например `https://medhouse-xxx.vercel.app`).
6. Вернуться в **Railway → Variables** и задать (или обновить) `CORS_ORIGINS` = URL фронта Vercel.

---

## Итог

| Сервис    | Роль                         | Откуда берётся |
|-----------|------------------------------|----------------|
| Git       | Исходный код                 | Ваш репозиторий |
| Railway   | Бэкенд (деплой из Git)       | Repo, Root = `backend` |
| Supabase  | БД для Railway               | `DATABASE_URL` в Railway |
| Vercel    | Фронт (деплой из Git)        | Repo, Root = `frontend` |
| Vercel Env| Обращение фронта к бэкенду   | `VITE_API_BASE` = URL Railway |

Полный чеклист и детали: [PROD_CHECKLIST.md](PROD_CHECKLIST.md) и [DEPLOY.md](DEPLOY.md).
