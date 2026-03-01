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
