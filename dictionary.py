# dictionary.py
import os
import pickle
from utils import normalize, simplify_tag
from config import PICKLE_FILE, TRAIN_FILES
from collections import defaultdict, Counter

def build_dict_from_files(file_list, folder_path, pickle_file=PICKLE_FILE):
    morph_dict = {}
    lemma_transforms = defaultdict(Counter)

    for fname in file_list:
        path = os.path.join(folder_path, fname)
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                parts = line.split('\t')
                if len(parts) < 4: continue

                form, lemma, upos = parts[1], parts[2], parts[3]

                norm_form = normalize(form)
                norm_lemma = normalize(lemma)
                simple_pos = simplify_tag(upos)

                morph_dict[norm_form] = (norm_lemma, simple_pos)

                # 🔹 собираем статистику преобразований
                if norm_form != norm_lemma:
                    for i in range(1, min(len(norm_form), len(norm_lemma)) + 1):
                        if norm_form[-i:] != norm_lemma[-i:]:
                            form_suf = norm_form[-i:]
                            lemma_suf = norm_lemma[-i:]
                            lemma_transforms[simple_pos][(form_suf, lemma_suf)] += 1
                            break

    with open(pickle_file,'wb') as f:
        pickle.dump((morph_dict, lemma_transforms), f)

    print(f"Словарь построен: {len(morph_dict)} форм")
    return morph_dict, lemma_transforms

def load_or_build_dict(file_list=TRAIN_FILES, folder_path='.', rebuild=False):
    if rebuild or not os.path.exists(PICKLE_FILE):
        return build_dict_from_files(file_list, folder_path)
    else:
        with open(PICKLE_FILE,'rb') as f:
            print(f"Словарь загружен из {PICKLE_FILE}")
            return pickle.load(f)