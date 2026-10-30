
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

from app.database import Base
from app.models.resume import Resume
from app.models.ai_viva_question import AIVivaQuestion
from app.models.mcq_attempt import MCQAttempt

load_dotenv()

DATABASE_URL = os.getenv("CLOUD_DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("CLOUD_DATABASE_URL is missing from .env")

engine = create_engine(DATABASE_URL)

try:
    Base.metadata.create_all(bind=engine)
    print("Neon database tables created successfully!")
finally:
    engine.dispose()
