import pymorphy2
from string import ascii_letters, digits

CYRILLIC_LETTERS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
ALLOWED_SYMBOLS = ascii_letters + CYRILLIC_LETTERS + digits
ALLOWED_POS = {'NOUN', 'ADJF', 'ADJS', 'VERB', 'INFN', 'NUMR', 'ADVB', 'GRND', 'PRTS', 'PRTF', 'COMP'}

morph = pymorphy2.MorphAnalyzer()


def remove_punctuation(st):
    return ''.join([char if char in ALLOWED_SYMBOLS else ' ' for char in st.lower()])


def normalize(st):
    return [word for word in remove_punctuation(st).split() if word]


def tokenize(st):
    words = normalize(st)
    tokens = []
    for word in words:
        if word.isascii():
            tokens.append(word)
        else:
            parsed = morph.parse(word)
            if parsed:
                pos = parsed[0].tag.POS
                if pos in ALLOWED_POS:
                    tokens.append(parsed[0].normal_form)
    return tokens
