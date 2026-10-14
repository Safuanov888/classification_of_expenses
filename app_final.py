import os
import logging

from fastapi import FastAPI

APP_NAME = os.getenv('APP_NAME', 'Приложение')
APP_VERSION = os.getenv('APP_VERSION', 'нет')
LOG_LEVEL= os.getenv('LOG_LEVEL', 'По умолчанию')
CONFIDENCE_THRESHOLD= os.getenv('CONFIDENCE_THRESHOLD', 0.5)
MAX_BATCH_SIZE= os.getenv('MAX_BATCH_SIZE', 10)


app = FastAPI(title=APP_NAME)