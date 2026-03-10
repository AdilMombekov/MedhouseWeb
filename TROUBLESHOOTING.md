# Диагностика: дашборд висит на «Загрузка данных...»

Чек-лист при рассинхроне frontend/backend. В проекте используются свои ключи и эндпоинты — ниже они учтены.

---

## Шаг 1: Быстрая диагностика (30 секунд)

### 1. Откройте DevTools в браузере

| Браузер       | Горячие клавиши   |
|---------------|-------------------|
| Chrome/Edge   | `F12` или `Ctrl+Shift+I` |
| Firefox       | `Ctrl+Shift+I`    |
| Safari        | `Cmd+Opt+I`       |

### 2. Проверьте 3 вкладки

#### Вкладка **Console** — есть ли красные ошибки?

| Ошибка | Причина | Действие |
|--------|---------|----------|
| `GET http://localhost:8000/api/... net::ERR_CONNECTION_REFUSED` | Бэкенд не запущен или не на порту 8000 | Запустите `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` в папке `backend` |
| CORS policy blocked | Запросы с frontend заблокированы | В нашем проекте CORS уже `allow_origins=["*"]`; проверьте, что запросы идут через **прокси** на `http://localhost:3030` (тогда домен один и CORS не мешает) |
| `Uncaught TypeError: Cannot read properties of undefined` | Фронт получил пустой/неожиданный ответ | Проверьте Network: какой ответ у `/api/analytics/bootstrap` |
| `401 Unauthorized` | Нет или неверный JWT | Перелогиньтесь; при необходимости очистите `localStorage` (ключ **`medhouse_token`**) |

#### Вкладка **Network** — какие запросы висят или падают?

1. Обновите страницу (`F5`).
2. Фильтр по **XHR** или **Fetch**.
3. Найдите запросы к `/api/...`.

В нашем проекте главная страница делает **один** запрос: **`/api/analytics/bootstrap`** (sources + aggregate разом).

| Статус | Что означает | Решение |
|--------|--------------|---------|
| `(failed)` | Бэкенд не отвечает | Запустить бэкенд на порту 8000 |
| `401` | Нет токена / истёк | Очистить `localStorage` и войти снова (admin@medhouse.kz / admin123) |
| `403` | Нет прав | Роли: только admin/moderator для части разделов; дашборд доступен всем авторизованным |
| `500` | Ошибка на бэкенде | Смотреть логи uvicorn в терминале |
| `(pending)` > 8 с | Таймаут (у нас 8 с) | Проверить, что бэкенд запущен и папка «Анализ 2» доступна; при первом старте кэш прогревается — подождать или обновить страницу |

#### Вкладка **Application** → **Local Storage** → `http://localhost:3030`

В этом проекте токен хранится под ключом **`medhouse_token`** (не `token` и не `access_token`).

- Пусто → пользователь не авторизован, нужен вход.
- Есть значение, но запросы 401 → токен протух или на бэкенде сменили `SECRET_KEY`; выйти и войти снова.

Проверка срока действия в Console:

```javascript
const t = localStorage.getItem('medhouse_token');
if (t) {
  const payload = JSON.parse(atob(t.split('.')[1]));
  console.log('Токен истекает:', new Date(payload.exp * 1000));
}
```

---

## Шаг 2: Проверка бэкенда (FastAPI)

### 1. Бэкенд запущен?

```bash
cd backend
.\venv\Scripts\activate   # Windows
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Проверка:

```bash
curl http://127.0.0.1:8000/health
# Ожидается: {"status":"ok"}

# Или в браузере: http://127.0.0.1:8000/docs
```

### 2. База инициализирована?

```bash
cd backend
python -m scripts.init_db
```

Должны создаться таблицы и админ **admin@medhouse.kz** / **admin123**. При необходимости проверка SQLite:

```bash
python -c "import sqlite3; c=sqlite3.connect('medhouse.db'); print(c.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall())"
```

### 3. Логи uvicorn при запросе

При загрузке главной страницы в терминале uvicorn должен появиться запрос к bootstrap, например:

```text
INFO:     127.0.0.1:xxxxx - "GET /api/analytics/bootstrap HTTP/1.1" 200 OK
```

Если при обновлении страницы **логов нет** — запрос не доходит до бэкенда (прокси, URL или фронт падает до запроса).

---

## Шаг 3: CORS и прокси

### Прокси Vite (`frontend/vite.config.js`)

Запросы с фронта идут на тот же origin (`http://localhost:3030`), а Vite проксирует `/api` на бэкенд:

```javascript
server: {
  port: 3030,
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
    },
  },
},
```

В Network запрос должен быть к **`http://localhost:3030/api/analytics/bootstrap`** (не к 8000). Если запрос уходит на 8000 — значит прокси не используется (например, жёстко прописан базовый URL).

### CORS в FastAPI (`backend/app/main.py`)

Сейчас: `allow_origins=["*"]` — все источники разрешены. Явно добавлять `http://localhost:3030` нужно только если смените на конкретные origins.

После правок в `vite.config.js` или `main.py` перезапустите и фронт (`npm run dev`), и бэкенд.

---

## Шаг 4: Авторизация и токены

Токен хранится в **`localStorage`** под ключом **`medhouse_token`**.

Быстрый сброс при «зависшей» авторизации:

1. DevTools → Console:
   ```javascript
   localStorage.removeItem('medhouse_token');
   location.reload();
   ```
2. Снова войти: **admin@medhouse.kz** / **admin123**.

---

## Шаг 5: Пустая база / нет данных

Если запрос **`/api/analytics/bootstrap`** возвращает **200 OK**, но экран пустой или «Нет данных»:

- Проверьте ответ в Network → выбран запрос → вкладка **Response**: должен быть JSON с полями `sources` и `aggregate`.
- Если в `aggregate.data` пусто при наличии файлов в «Анализ 2» — проверьте путь в конфиге бэкенда (`ANALIZ2_DIR`, по умолчанию корень проекта + `Анализ 2`).
- При отсутствии файлов или ошибках чтения бэкенд отдаёт **демо-данные**; тогда график и список источников всё равно должны отображаться.

Проверка пользователей и компаний:

```bash
cd backend
python -c "
from app.database import SessionLocal
from app.models import User, Company
db = SessionLocal()
print('Users:', db.query(User).count())
print('Companies:', db.query(Company).count())
db.close()
"
```

---

## Экспресс-тест: минимальный сценарий

```bash
# Терминал 1: бэкенд
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --host 127.0.0.1 --port 8000

# Терминал 2: фронт
cd frontend
npm run dev
```

В браузере:

1. Открыть **http://localhost:3030**
2. F12 → Console: нет красных ошибок.
3. Войти (admin@medhouse.kz / admin123).
4. Network: запрос **`/api/analytics/bootstrap`** → статус **200**, в ответе есть `sources` и `aggregate`.

Если на шаге 4 запрос 200 и JSON валидный, но экран всё ещё «Загрузка данных...» — проблема в обработке ответа на фронте (проверить состояние loading и setState в компоненте дашборда).

---

## Чек-лист самопроверки

- [ ] Бэкенд запущен на порту 8000, `http://127.0.0.1:8000/health` отвечает
- [ ] В Console нет красных ошибок
- [ ] В Network запрос к `/api/analytics/bootstrap` (или к `/api/auth/me` после входа) возвращает 200
- [ ] В Local Storage есть ключ **`medhouse_token`** после входа
- [ ] Выполнен `python -m scripts.init_db` и есть пользователь admin
- [ ] Запросы к API идут на **http://localhost:3030/api/...** (через прокси Vite), а не напрямую на 8000

---

## Если не помогло — пришлите

1. Скриншот вкладки **Console** (красные ошибки).
2. Скриншот вкладки **Network** (статусы запросов к `/api/*`, особенно `/api/analytics/bootstrap`).
3. Логи **uvicorn** в момент загрузки страницы.
4. Содержимое `backend/.env` (без паролей и секретов).

По этим данным можно точнее указать причину зависания на «Загрузка данных...».
