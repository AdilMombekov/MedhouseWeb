from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth_router, users_router, companies_router, templates_router, uploads_router, analytics_router, google_drive_router, dashboard_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Medhouse / Swiss Energy — Управленческая отчётность",
    description="Дашборд и API для отчётности Медхаус (дистрибьютор) и Свисс Энерджи (контролирующая компания).",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api")
app.include_router(users_router.router, prefix="/api")
app.include_router(companies_router.router, prefix="/api")
app.include_router(templates_router.router, prefix="/api")
app.include_router(uploads_router.router, prefix="/api")
app.include_router(analytics_router.router, prefix="/api")
app.include_router(google_drive_router.router, prefix="/api")
app.include_router(dashboard_router.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Medhouse / Swiss Energy API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
