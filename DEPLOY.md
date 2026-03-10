# Деплой Medhouse / Swiss Energy

## Сборка для продакшена

### 1. Фронтенд (статический билд)

```bash
cd frontend
npm ci
npm run build
```

Собранные файлы появятся в `frontend/dist/`. Их можно раздавать любым веб-сервером (Nginx, Apache, или хостинг статики).

### 2. Бэкенд

На сервере:

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Linux/macOS  или  venv\Scripts\activate  на Windows
pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env: SECRET_KEY, DATABASE_URL при необходимости
python -m scripts.init_db
python -m scripts.create_dashboard_templates
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Для продакшена лучше использовать gunicorn (Linux):

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 3. Проксирование API на фронт

Если фронт и API на одном домене (рекомендуется):

- Nginx: проксировать `/api` на `http://127.0.0.1:8000`.
- Или отдавать статику из `frontend/dist/` и проксировать `/api` на бэкенд.

Пример Nginx (фрагмент):

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/frontend/dist;
    index index.html;
    location / {
        try_files $uri $uri/ /index.html;
    }
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. Переменные окружения на сервере

- `SECRET_KEY` — обязательно смените на случайную строку.
- `DATABASE_URL` — для продакшена лучше PostgreSQL (например `postgresql://user:pass@localhost/medhouse`).
- `ANALIZ2_PATH` — полный путь к папке «Анализ 2» на сервере, если она в другом месте.

## Сохранение проекта (Git)

Инициализация репозитория и первый коммит:

```bash
cd "d:\Разработка медхаус"
git init
git add .
git commit -m "Medhouse/Swiss Energy: дашборд, 7 страниц аналитики, шаблоны выгрузки"
```

Дальше можно подключить удалённый репозиторий (GitHub, GitLab и т.д.) и выполнять `git push`.

---

## Деплой прод: Supabase + Railway + Vercel

Прод рекомендуется разворачивать так: **БД — Supabase (PostgreSQL)**, **бэкенд — Railway**, **фронтенд — Vercel**. 1С пока только через импорт данных; автообновление настраивается отдельно.

### Supabase (база данных)

1. Создайте проект на [supabase.com](https://supabase.com).
2. **Connection string для бэкенда:** в панели Supabase откройте **Settings → Database**. В блоке **Connection string** выберите **URI**, скопируйте строку (типа `postgresql://postgres.[ref]:[YOUR-PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres`). Пароль — тот, что задали при создании проекта (или смените в Database → Database password).
3. **API Keys** (вкладка в разделе Connect): при необходимости для клиентских сценариев используйте **Project URL** и **Anon key**; для серверного доступа — **Service role key** в **API settings** (не в репозиторий).

### Railway (бэкенд)

1. Подключите репозиторий к [Railway](https://railway.app). В настройках сервиса укажите **Root Directory** = `backend`.
2. В **Variables** задайте переменные окружения:
   - `DATABASE_URL` — строка подключения Postgres из Supabase (см. выше).
   - `SECRET_KEY` — случайная строка (например `openssl rand -hex 32`).
   - `CORS_ORIGINS` — домен фронта на Vercel через запятую (например `https://medhouse.vercel.app`), чтобы браузер не блокировал запросы к API. Если не задать — по умолчанию разрешены все (`*`), что подходит для разработки.
   - При необходимости: `MEDHOUSE_API_KEY_1`, `LOG_LEVEL`, `LOG_FILE`, пути к данным (`DATA_BASE_PATH`, `ANALIZ2_PATH`), ключи Google Drive и т.д. (см. `backend/.env.example`).
3. Один раз инициализировать БД: в Railway откройте **Settings → Deploy** и добавьте одноразовую команду **Custom start command** или выполните локально, подставив `DATABASE_URL` от Supabase:
   ```bash
   cd backend
   set DATABASE_URL=postgresql://...
   python -m scripts.init_db
   python -m scripts.create_dashboard_templates
   ```
   После этого верните обычный старт (или удалите custom command). Либо используйте Railway **one-off run** (если доступен) для этих команд.
4. В разделе **Networking** нажмите **Generate Domain** и сохраните URL (например `https://medhouse-backend.up.railway.app`) — он понадобится для фронта на Vercel.

Запуск на Railway задаётся в `backend/railway.json` (или Procfile): `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

### Vercel (фронтенд)

1. Подключите репозиторий к [Vercel](https://vercel.com). Укажите **Root Directory** = `frontend`, **Framework** = Vite, **Build Command** = `npm run build`, **Output Directory** = `dist`.
2. В настройках проекта → **Environment Variables** добавьте:
   - `VITE_API_BASE` = URL бэкенда на Railway **без** завершающего слэша (например `https://medhouse-backend.up.railway.app`). Все запросы к API пойдут на этот адрес.
3. Соберите и задеплойте. После деплоя фронт будет доступен по своему домену Vercel и будет обращаться к API на Railway.

### Краткий чеклист

| Где | Что сделать |
|-----|-------------|
| Supabase | Взять Postgres connection string (Settings → Database), при необходимости — API keys |
| Railway | Root = `backend`, задать `DATABASE_URL`, `SECRET_KEY`, при необходимости `CORS_ORIGINS` (URL фронта на Vercel), один раз выполнить `init_db` и `create_dashboard_templates`, выдать домен |
| Vercel | Root = `frontend`, задать `VITE_API_BASE` = URL бэкенда Railway |
