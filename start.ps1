# Запуск бэкенда и фронтенда
$backend = "d:\Разработка медхаус\backend"
$frontend = "d:\Разработка медхаус\frontend"

Write-Host "Backend: http://127.0.0.1:8000  |  Frontend: http://localhost:3030" -ForegroundColor Green
Write-Host "Login: admin@medhouse.kz / admin123" -ForegroundColor Cyan
Write-Host ""

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backend'; .\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontend'; npm run dev"
