import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    # Database configuration would go here
