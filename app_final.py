import os
import logging
import joblib

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

APP_NAME = os.getenv('APP_NAME', 'Приложение')
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '0.5'))
MAX_BATCH_SIZE = int(os.getenv('MAX_BATCH_SIZE', '10'))

app = FastAPI(title=APP_NAME)


class ExpenseRequest(BaseModel):
    description: str = Field(min_length=1, max_length=100, description='Описание траты')


class BatchExpenseRequest(BaseModel):
    descriptions: list[str] = Field(min_length=1, description='Описание трат')


logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("Classification of expenses")


@app.on_event('startup')
def start():
    logger.info(f'Приложение {APP_NAME} запущено. Версия: {APP_VERSION}')
    try:
        app.state.model = joblib.load('expense_model.joblib')
        logger.info('Модель успешно загружена')
    except Exception as e:
        logger.error(f'Ошибка при загрузке модели: {e}')
        raise e
    logger.info(f'Настройки: LOG_LEVEL={LOG_LEVEL}, CONFIDENCE_THRESHOLD={CONFIDENCE_THRESHOLD}')


def _predict_category(description: str):
    model = app.state.model
    category = model.predict([description])[0]
    probas = model.predict_proba([description])[0]
    conf = float(max(probas))

    is_below = conf < CONFIDENCE_THRESHOLD

    logger.info(f"Классификация: '{description}' -> {category} (уверенность: {conf:.2f})")
    if is_below:
        logger.warning(f"Низкая уверенность для '{description}': {conf:.2f} < {CONFIDENCE_THRESHOLD}")

    return {
        "description": description,
        "category": category,
        "confidence": round(conf, 2),
        "below_threshold": is_below
    }


@app.get('/categories')
def get_categories():
    logger.info('Запрос к /categories (Список категорий)')
    return {'categories': app.state.model.classes_.tolist()}


@app.post("/categorize")
def categorize_expense(request: ExpenseRequest):
    logger.info('Запрос к /categorize (Предсказание класса траты)')
    return _predict_category(request.description)


@app.post('/categorize/batch')
def categorize_batch(request: BatchExpenseRequest):
    logger.info('Запрос к /categorize/batch (Предсказание классов списка трат)')
    if len(request.descriptions) > MAX_BATCH_SIZE:
        logger.warning(f'Превышен размер батча: {len(request.descriptions)} > {MAX_BATCH_SIZE}')
        raise HTTPException(
            status_code=400,
            detail=f"Слишком много описаний. Максимум: {MAX_BATCH_SIZE}"
        )

    result = []
    for description in request.descriptions:
        result.append(_predict_category(description))

    return {"results": result}


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
