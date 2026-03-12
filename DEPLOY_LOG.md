# Лог деплоя: Git + Supabase + Railway + Vercel

Документ фиксирует найденные проблемы и пошаговые действия для корректного подключения и деплоя.

---

## Диагностика (что было не так)

| Проблема | Причина | Решение |
|----------|--------|---------|
| **Railway: Healthcheck failed** | `DATABASE_URL` с портом **5432** (Direct/Session) — на бесплатном Supabase из Railway часто недоступен; для serverless нужен **Transaction pooler** (порт **6543**). | В `DATABASE_URL` использовать порт **6543** и хост вида `aws-X-REGION.pooler.supabase.com`. |
| **Tenant or user not found** (при смене на aws-0) | У части проектов Supabase пулер в кластере **aws-1**, а не aws-0. Подставка `aws-0` даёт неверный хост. | Взять точный хост из Supabase Dashboard → Database → **Connection string** → **Transaction pooler (URI)** (там будет либо aws-0, либо aws-1). В коде добавлена переменная `SUPABASE_POOLER_PREFIX=aws-1` при необходимости. |
| **Network is unreachable** (db.xxx.supabase.co:6543) | Хост `db.PROJECT_REF.supabase.co` резолвится в **IPv6**; Railway не поддерживает IPv6. | Не использовать `db.*.supabase.co` для Railway. Использовать только **pooler**: `aws-0-REGION.pooler.supabase.com` или `aws-1-REGION.pooler.supabase.com` (порт 6543). |
| **CORS блокирует фронт** | В Railway было `CORS_ORIGINS=medhouse-web.vercel.app` без `https://`. | Задать `CORS_ORIGINS=https://medhouse-web.vercel.app` (без слеша в конце). |
| **Vercel: билд из корня** | Root Directory не был указан или был неверный. | В Vercel → Project Settings → **Root Directory** = `frontend`, **Framework Preset** = **Vite**. |
| **Расхождение настроек Vercel** | Production Overrides (Vite) не совпадали с Project Settings (Other). | В Project Settings выставить **Framework Preset** = **Vite** и сохранить. |

---

## Что сделано в репозитории

1. **backend/app/config.py**  
   Добавлена переменная `SUPABASE_POOLER_PREFIX` (по умолчанию `aws-0`). Если в дашборде Supabase в Connection string указан хост **aws-1**-region, в Railway задать `SUPABASE_POOLER_PREFIX=aws-1`.

2. **backend/.env.example**  
   Добавлены комментарии для `SUPABASE_POOLER_PREFIX` и напоминание смотреть точный хост в Supabase (Transaction pooler).

3. **DEPLOY_LOG.md** (этот файл)  
   Зафиксированы причины сбоев и пошаговые действия.

---

## Пошаговые действия (сделать вручную)

Я не имею доступа к панелям Railway, Vercel и Supabase — эти шаги нужно выполнить у себя.

### 1. Supabase: получить строку подключения

1. Откройте [Supabase Dashboard](https://supabase.com/dashboard) → ваш проект.
2. **Project Settings** → **Database**.
3. В блоке **Connection string** выберите **Transaction pooler** (не Session, не Direct).
4. Скопируйте **URI**. Формат будет одним из:
   - `postgresql://postgres.PROJECT_REF:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres`
   - или `...@aws-1-REGION.pooler.supabase.com:6543/postgres`
5. Запомните:
   - используется ли **aws-0** или **aws-1** (первая часть хоста после `@`);
   - **REGION** (например `ap-northeast-2`, `us-east-1`).

### 2. Railway: переменные бэкенда

**Вариант A — задать DATABASE_URL вручную (рекомендуется для быстрого фикса):**

1. Railway → проект → сервис бэкенда (MedhouseWeb) → **Variables**.
2. Переменная **DATABASE_URL**:
   - Должна быть строка вида:  
     `postgresql://postgres.PROJECT_REF:PASSWORD@aws-X-REGION.pooler.supabase.com:6543/postgres`
   - Порт обязательно **6543** (Transaction pooler).
   - Хост — **тот же**, что в Supabase (aws-0 или aws-1, тот же REGION).
   - Если в дашборде Supabase указан **aws-1** — не менять на aws-0 (иначе «Tenant or user not found»).

**Вариант B — собрать URL из переменных (без хардкода DATABASE_URL):**

1. В Railway **удалить** переменную `DATABASE_URL` (или оставить пустой/не задавать).
2. Добавить:
   - `SUPABASE_URL` = `https://PROJECT_REF.supabase.co`
   - `SUPABASE_DB_PASSWORD` = пароль БД из Supabase
   - `SUPABASE_DB_REGION` = регион из URI (например `ap-northeast-2`)
   - `SUPABASE_POOLER_PREFIX` = `aws-1` если в дашборде Supabase хост **aws-1**-region; иначе не задавать (по умолчанию aws-0).

**Общие переменные Railway (в любом варианте):**

- `SECRET_KEY` — случайная строка (например `openssl rand -hex 32`).
- `CORS_ORIGINS` = `https://medhouse-web.vercel.app` (без слеша в конце; при нескольких доменах — через запятую).

После изменений нажать **Deploy** и дождаться успешного деплоя. Проверка:  
`https://ВАШ-RAILWAY-ДОМЕН/health` и `/health/ready` → оба возвращают `{"status":"ok"}` (у ready ещё `"database":"connected"`).

### 3. Vercel: настройки проекта

1. Vercel → проект **medhouse-web** → **Settings** → **General**.
2. **Root Directory**: установить **frontend** (Override → `frontend`).
3. **Build and Deployment**:
   - **Framework Preset**: **Vite**.
   - Build Command: `npm run build`.
   - Output Directory: `dist`.
4. **Environment Variables**:  
   `VITE_API_BASE` = URL бэкенда Railway **без** слэша в конце (например `https://medhouse-web-production.up.railway.app`).
5. Сохранить. При необходимости сделать **Redeploy** (Deployments → … → Redeploy).

### 4. Инициализация БД (один раз)

Если БД Supabase ещё пустая для этого приложения:

- Railway: сервис бэкенда → **…** → **Run Command** (one-off):  
  `python -m scripts.init_production_db`
- Или локально, задав в `backend/.env` тот же `DATABASE_URL` (или SUPABASE_*), из папки `backend`:  
  `python -m scripts.init_production_db`

### 5. Финальная проверка

- Открыть `https://medhouse-web.vercel.app`.
- Войти (например admin@medhouse.kz / admin123, если уже создан через init_production_db).
- Убедиться, что дашборд загружается и нет ошибок CORS в DevTools (Network).

---

## Краткая шпаргалка по DATABASE_URL (Supabase + Railway)

- Порт **6543** — Transaction pooler (для Railway/serverless). Порт 5432 с Railway часто не подходит.
- Хост только **pooler**: `aws-0-REGION.pooler.supabase.com` или `aws-1-REGION.pooler.supabase.com`. Не использовать `db.PROJECT_REF.supabase.co` (IPv6 на Railway не работает).
- Логин в URI для pooler: `postgres.PROJECT_REF` (не просто `postgres`).
- Регион и префикс (aws-0/aws-1) брать **строго** из Supabase → Database → Connection string → Transaction pooler.

---

---

## Логика БД: что добавлено не по докам (для сноса Railway и перепривязки)

Сверка с **docs/00_НАЧНИТЕ_ЗДЕСЬ.md**, **docs/02_источники_данных/** и **docs/03_архитектура_и_тз/ПЛАН_ТЕСТОВОЙ_РЕАЛИЗАЦИИ_И_ОТКРЫТЫЕ_ВОПРОСЫ.md**:

| В доках | В коде (модели/роутеры) | Вывод |
|--------|-------------------------|--------|
| Стек: SQLite (потом PostgreSQL) | `config.py` / `database.py` — SQLite по умолчанию, поддержка Postgres | **По доку.** |
| Этап 1 плана: справочники — **города, номенклатура, контрагенты, адреса** (загрузка из «база для данных» в БД) | Отдельных таблиц «города», «номенклатура», «контрагенты», «адреса» в `models.py` **нет** | В коде справочники не по плану (другие сущности). |
| Данные из Google Drive/Sheets (ПНЛ, МХ формат) — **источники** | **GoogleSheet**, **GoogleSheetSnapshot** — реестр таблиц и **снимки листов в JSON в БД**; `sync_google_sheets.py`, `google_sheets_router` | **Не по запросу:** в доке — «брать данные из Google»; кэшировать листы в SQLite не требовалось. |
| Результаты продаж: данные из «Отгрузка 1», «Выгрузка 2» — **загрузка Excel или API Google** | **MailingBatch**, **MailingRow** — каждая строка выгрузки 1С в БД (organization, kontragent, nomerklatura, amount, profit, raw_data); `import_mailing_to_db.py`, `mailing_router` | **Не по запросу:** в доке — источник Excel/API; хранить построчно в БД не требовалось. |
| Аналитика: папка «Анализ 2», источники данных | **AnalysisDataset** — метаданные «analiz2», «reference», «import»; `analytics_router` | В плане этапов такой таблицы нет; добавлено сверх явного запроса. |
| Пользователи, две компании (Медхаус, Свисс), роли | **User**, **Company**; auth, `users_router`, `companies_router` | По ТЗ (организации, доступ) — допустимо. |
| Загрузка отчётов, шаблоны, тип отчётности 1С | **ReportTemplate**, **ReportUpload**; `templates_router`, `uploads_router` | Упоминается в плане («загрузка Excel»); граница нормы. |

**Что при сносе Railway и перепривязке учесть:**

1. **Оставить только по твоей инициативе:** решить, нужны ли в БД: снимки Google Sheets (`google_sheets`, `google_sheet_snapshots`), построчная рассылка/выгрузка (`mailing_batches`, `mailing_rows`), метаданные аналитики (`analysis_datasets`). По докам достаточно: читать Google по API при запросе; принимать загрузки файлов без обязательного хранения каждой строки в SQLite.
2. **Справочники по плану:** в ПЛАН_ТЕСТОВОЙ_РЕАЛИЗАЦИИ этап 1 — таблицы **города, номенклатура, контрагенты, адреса** и скрипт загрузки из «база для данных». Сейчас в коде этих таблиц нет — при перепривязке можно делать схему по плану.
3. **Деплой:** после сноса Railway — новая БД (например только Supabase или другой хост); задать `DATABASE_URL` или `SUPABASE_*` по новой связке; один раз выполнить `python -m scripts.init_production_db` из `backend/`.

---

## Ссылки

- [PROD_CHECKLIST.md](PROD_CHECKLIST.md) — общий чеклист первого деплоя.
- [DEPLOY.md](DEPLOY.md) — деплой Railway + Vercel, переменные, альтернатива Supabase.
