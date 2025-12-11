from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from backend.api.routes import router
from backend.database.db import init_db, SessionLocal, UserDB
from backend.config import settings
from passlib.context import CryptContext

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Traffic Monitoring System",
    description="Система автоматического мониторинга и анализа сетевого трафика",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

# Монтирование статических файлов (фронтенд)
try:
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
except Exception as e:
    logger.warning(f"Could not mount frontend: {e}")

@app.on_event("startup")
async def startup_event():
    """Инициализируйте базу данных и создание демо пользователя"""
    logger.info("Initializing database...")
    init_db()

    # Создание демо пользователя, если он еще не существует
    db = SessionLocal()
    try:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        existing_user = db.query(UserDB).filter(UserDB.username == "admin").first()
        if not existing_user:
            demo_user = UserDB(
                username="admin",
                email="admin@example.com",
                hashed_password=pwd_context.hash("admin123"),
                role="administrator",
                is_active=True
            )
            db.add(demo_user)
            db.commit()
            logger.info("Created demo user: admin / admin123")
    finally:
        db.close()

    logger.info("Application started successfully")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )
