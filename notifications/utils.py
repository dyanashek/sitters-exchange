import requests

from googletrans import Translator
from django.http import HttpResponse

from config import TELEGRAM_TOKEN

def translate_to_heb(text):
    try:
        translator = Translator()
        text_heb = translator.translate(text=text, dest='he', src='auto')
        if text_heb.text:
            return text_heb.text
        return False
    except:
        return False


def send_message_on_telegram(params, files=False, token=TELEGRAM_TOKEN):
    """Отправка сообщения в телеграм."""
    if files:
        try:
            endpoint = f'https://api.telegram.org/bot{token}/sendPhoto'
            response = requests.post(endpoint, data=params, files=files)
        except:
            response = False
    else:
        try:
            endpoint = f'https://api.telegram.org/bot{token}/sendMessage'
            response = requests.post(endpoint, data=params)
        except:
            response = False

    return response
    