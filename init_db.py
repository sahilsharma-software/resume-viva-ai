from app.db_connection import engine
from app.database import Base
from app.models.resume import Resume
from app.models.mcq_attempt import MCQAttempt
from app.models.ai_viva_question import AIVivaQuestion

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")
