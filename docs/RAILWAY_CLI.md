# Railway CLI — шпаргалка команд

Установка: `npm install -g @railway/cli` или [pre-built binaries](https://github.com/railwayapp/cli/releases).

## Аутентификация

- `railway login` — войти в аккаунт
- `railway login --browserless` — вход без браузера (SSH и т.п.)
- `railway logout` — выйти
- `railway whoami` — текущий пользователь

**Токены (CI/CD):**
- Проект: `RAILWAY_TOKEN=xxx railway up`
- Аккаунт: `RAILWAY_API_TOKEN` для действий на уровне аккаунта

---

## Проекты

- `railway init` — создать проект
- `railway link` — привязать текущую папку к проекту
- `railway unlink` — отвязать
- `railway list` — список проектов
- `railway status` — информация о проекте
- `railway open` — открыть в браузере

---

## Деплой

- `railway up` — задеплоить текущую директорию
- `railway up --detach` — деплой без стрима логов
- `railway deploy --template postgres` — деплой шаблона
- `railway redeploy` — передеплой последнего
- `railway restart` — перезапуск сервиса
- `railway down` — удалить последний деплой

---

## Сервисы

- `railway add` — добавить сервис (интерактивно)
- `railway add --database postgres` — добавить PostgreSQL
- `railway add --repo user/repo` — из GitHub
- `railway service` — привязать сервис
- `railway scale` — масштабирование
- `railway delete` — удалить проект

---

## Переменные

- `railway variable list` — список
- `railway variable set KEY=value` — задать
- `railway variable delete KEY` — удалить

---

## Окружения

- `railway environment` — переключить (интерактивно)
- `railway environment new staging` — создать
- `railway environment delete dev` — удалить

---

## Локальная разработка

- `railway run npm start` — запуск с переменными Railway
- `railway shell` — шелл с переменными Railway
- `railway dev` — сервисы локально через Docker

---

## Логи и отладка

- `railway logs` — стрим логов
- `railway logs --build` — логи сборки
- `railway logs -n 100` — последние 100 строк
- `railway ssh` — SSH в контейнер
- `railway connect` — подключиться к оболочке БД

---

## Сеть

- `railway domain` — выдать домен
- `railway domain example.com` — свой домен

---

## Глобальные флаги

- `-s, --service` — целевой сервис (имя или ID)
- `-e, --environment` — окружение
- `--json` — вывод в JSON
- `-y, --yes` — без подтверждений
- `-h, --help` — справка
- `-V, --version` — версия

Подробнее: [Railway CLI Docs](https://docs.railway.com/develop/cli).
