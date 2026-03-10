# Чеклист первого деплоя (прод)

Пошагово: что сделать один раз, чтобы вывести проект в прод на Supabase + Railway + Vercel.

---

## 1. Supabase (база данных)

- [ ] Зайти на [supabase.com](https://supabase.com), создать проект (если ещё нет).
- [ ] **Settings → Database** → скопировать **Connection string (URI)**. Подставить пароль в строку (формат: `postgresql://postgres.[ref]:[PASSWORD]@...pooler.supabase.com:6543/postgres`).
- [ ] Сохранить эту строку — она понадобится как `DATABASE_URL` для Railway.

---

## 2. Репозиторий

- [ ] Код в Git, репозиторий на GitHub или GitLab (см. [DEPLOY.md](DEPLOY.md) — раздел «Подключение нового репозитория»).
- [ ] `git push` выполнен, в репозитории актуальная ветка `master`.

---

## 3. Railway (бэкенд)

- [ ] Зайти на [railway.app](https://railway.app), **New Project** → **Deploy from GitHub repo** → выбрать репозиторий.
- [ ] В настройках сервиса указать **Root Directory** = `backend`.
- [ ] **Variables** — добавить:
  - `DATABASE_URL` = строка Postgres из Supabase (п. 1).
  - `SECRET_KEY` = случайная строка (`openssl rand -hex 32` или аналог).
  - `CORS_ORIGINS` = URL фронта на Vercel (после п. 4), например `https://ваш-проект.vercel.app`.
- [ ] **Один раз инициализировать БД** (таблицы + админ + записи шаблонов). Локально в папке проекта задайте `DATABASE_URL` строкой Postgres из Supabase и выполните:
  ```bash
  cd backend
  python -m scripts.init_production_db
  ```
  Либо в Railway использовать **One-off run** (если доступен в интерфейсе) с командой `python -m scripts.init_production_db`.
- [ ] **Networking** → **Generate Domain** → скопировать URL бэкенда (например `https://medhouse-production.up.railway.app`). Он нужен для Vercel как `VITE_API_BASE`.
- [ ] Проверить: открыть в браузере `https://ВАШ-RAILWAY-URL/health` и `https://ВАШ-RAILWAY-URL/health/ready` — оба должны вернуть `{"status":"ok"}` (у ready ещё `"database":"connected"`).

---

## 4. Vercel (фронтенд)

- [ ] Зайти на [vercel.com](https://vercel.com), **Add New** → **Project** → импорт того же репозитория.
- [ ] **Root Directory** = `frontend`. **Framework Preset** = Vite. Build Command = `npm run build`, Output Directory = `dist`.
- [ ] **Environment Variables** — добавить:
  - `VITE_API_BASE` = URL бэкенда Railway **без** слэша в конце (например `https://medhouse-production.up.railway.app`).
- [ ] **Deploy**. После деплоя скопировать URL фронта (например `https://medhouse-xxx.vercel.app`).
- [ ] Если ещё не задавали `CORS_ORIGINS` на Railway — вернуться в Railway → Variables → добавить `CORS_ORIGINS` = URL фронта Vercel (как выше).
- [ ] Открыть сайт на Vercel → войти (admin@medhouse.kz / admin123) → проверить дашборд и разделы.

---

## 5. После первого запуска

- [ ] Сменить пароль админа (через раздел «Администрирование» или напрямую в БД).
- [ ] При необходимости добавить `LOG_LEVEL=INFO`, `LOG_FILE=logs/app.log` на Railway (если нужны файловые логи; на Railway файловая система эфемерная, логи лучше смотреть в панели Railway).
- [ ] **Шаблоны выгрузки:** на Railway диск эфемерный — после редеплоя `backend/templates/` пустой. Варианты: **(А)** Локально выполнить `python -m scripts.create_dashboard_templates`, затем `git add backend/templates/*.xlsx` и `git commit` — тогда 7 шаблонов будут в репо и появятся на Railway при каждом деплое. **(Б)** Один раз после деплоя выполнить one-off `python -m scripts.create_dashboard_templates` (шаблоны появятся до следующего редеплоя).

---

## Ссылки

- Полное описание переменных и вариантов деплоя: [DEPLOY.md](DEPLOY.md).
- Бэкенд, БД, пути, переменные: [docs/04_настройка_и_пути/ЧТО_ТРЕБУЕТСЯ_БЭК_БД_БЭКАП.md](docs/04_настройка_и_пути/ЧТО_ТРЕБУЕТСЯ_БЭК_БД_БЭКАП.md).
