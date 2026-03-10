"""
Сгенерировать API-ключ для доступа из Postman/curl.
Запуск: python -m scripts.generate_api_key
"""
import secrets

key = secrets.token_urlsafe(32)
print("Сгенерирован API-ключ. Добавьте в backend/.env:")
print()
print("MEDHOUSE_API_KEY=" + key)
print()
print("Использование:")
print('  curl -H "X-API-Key: ' + key + '" http://localhost:8000/api/auth/me')
print()
print("Подробнее: API_ACCESS.md в корне проекта.")
