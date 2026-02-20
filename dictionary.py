# dictionary.py
import os
import pickle
from utils import normalize, simplify_tag
from config import PICKLE_FILE, TRAIN_FILES

def build_dict_from_files(file_list, folder_path, pickle_file=PICKLE_FILE):
    morph_dict = {}
    for fname in file_list:
        path = os.path.join(folder_path, fname)
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                parts = line.split('\t')
                if len(parts) < 4: continue
                form, lemma, upos = parts[1], parts[2], parts[3]
                morph_dict[normalize(form)] = (normalize(lemma), simplify_tag(upos))
    with open(pickle_file,'wb') as f:
        pickle.dump(morph_dict,f)
    print(f"Словарь построен: {len(morph_dict)} форм, сохранено в {pickle_file}")
    return morph_dict

def load_or_build_dict(file_list=TRAIN_FILES, folder_path='.', rebuild=False):
    if rebuild or not os.path.exists(PICKLE_FILE):
        return build_dict_from_files(file_list, folder_path)
    else:
        with open(PICKLE_FILE,'rb') as f:
            print(f"Словарь загружен из {PICKLE_FILE}")
            return pickle.load(f)
            