# config.py
UD_FOLDER = 'UD_Russian-SynTagRus'   # путь к папке с Conllu-файлами
PICKLE_FILE = 'syntagrus_dict.pkl'   # файл для сохранения словаря

TRAIN_FILES = [
    'ru_syntagrus-ud-train-a.conllu',
    'ru_syntagrus-ud-train-b.conllu',
    'ru_syntagrus-ud-train-c.conllu'
]
TEST_FILES = ['ru_syntagrus-ud-test.conllu']

TAG_MAP = {
    'NOUN': 'S', 'PROPN': 'S',
    'ADJ': 'A',
    'VERB': 'V', 'AUX': 'V',
    'ADV': 'ADV',
    'ADP': 'PR',
    'CONJ': 'CONJ',
    'PRON': 'NI',
    'NUM': 'NI',
    'INTJ': 'NI',
    'PART': 'CONJ',
    'X': 'UNK'
}