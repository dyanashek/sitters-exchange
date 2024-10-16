import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')
ADMIN_CHAT_REVIEWS_ID = os.getenv('ADMIN_CHAT_REVIEWS_ID')
ADMIN_CHAT_PROPOSALS_ID = os.getenv('ADMIN_CHAT_PROPOSALS_ID')
BOT_NAME = 'Israel_workExchange_bot'

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = int(os.getenv('REDIS_PORT'))
REDIS_DB = int(os.getenv('REDIS_DB'))

PER_PAGE = 5
MAX_SYMBOLS = 4000 # максимально допустимая длина сообщения (для показа всех вакансий/отзывов)
MAX_LEN = 1000 # максимально допустимая длина отзыва/описания вакансии/рассказа о себе