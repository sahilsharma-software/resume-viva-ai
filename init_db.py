from app.db_connection import engine
from app.database import Base
from app.models.resume import Resume

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")
