class Config:
    DEBUG = True
    SECRET_KEY = "MY SECRET_KEY"
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False