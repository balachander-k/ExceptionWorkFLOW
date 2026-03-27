import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///workflow.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXP_MINUTES = int(os.getenv("JWT_EXP_MINUTES", "120"))
