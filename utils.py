# utils.py
from config import TAG_MAP

def normalize(text):
    return text.lower().replace('ё','е')

def simplify_tag(upos):
    return TAG_MAP.get(upos.upper(), 'UNK')