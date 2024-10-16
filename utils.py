import re
import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

from googletrans import Translator


async def extract_digits(input_string):
    return re.sub(r'\D', '', input_string)


async def validate_phone(phone):
    phone = await extract_digits(phone)
    if len(phone) > 6:
        return phone
    else:
        return False


async def validate_salary(input_string):
    try:
        input_string = input_string.replace(',', '.')
        price = int(input_string)
    except:
        return False
    
    if price >= 0:
        return price
    
    return False


async def escape_markdown(text):
    try:
        characters_to_escape = ['_', '*', '[', ']', '`']
        for char in characters_to_escape:
            text = text.replace(char, '\\' + char)
    except:
        pass
    
    return text


async def translate_to_heb(text):
    try:
        translator = Translator()
        text_heb = translator.translate(text=text, dest='he', src='auto')
        if text_heb.text:
            return text_heb.text
        return False
    except:
        return False


async def translate_to_rus(text):
    try:
        translator = Translator()
        text_rus = translator.translate(text=text, dest='ru', src='auto')
        if text_rus.text:
            return text_rus.text
        return False
    except:
        return False
