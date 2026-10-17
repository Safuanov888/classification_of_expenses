import os
import logging

from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv('APP_NAME', 'Приложение')
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '0.5'))
MAX_BATCH_SIZE = int(os.getenv('MAX_BATCH_SIZE', '10'))

app = FastAPI(title=APP_NAME)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("Classification of expenses")

@app.on_event('startup')
def start():
    logger.info(f'Приложение {APP_NAME} запущено. Версия: {APP_VERSION}')
    logger.info(f'Настройки: LOG_LEVEL={LOG_LEVEL}, CONFIDENCE_THRESHOLD={CONFIDENCE_THRESHOLD}')

@app.get("/")
def root():
    logger.info('Запрос к /')
    return {"message": "Приложение работает"}


@app.get("/health")
def health():
    logger.info('Запрос к /health')
    return {"status": "ok"}


@app.get('/version')
def version():
    logger.info('Запрос к /version')
    return {'version': APP_VERSION}
