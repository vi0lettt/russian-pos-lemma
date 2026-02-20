import os
import re
import pickle
import sys
from collections import defaultdict, Counter
import subprocess


# ==================== ПАРАМЕТРЫ ====================
UD_FOLDER = 'UD_Russian-SynTagRus'   # путь к папке с Conllu-файлами
PICKLE_FILE = 'syntagrus_dict.pkl'   # файл для сохранения словаря
TRAIN_FILES = ['ru_syntagrus-ud-train-a.conllu',
               'ru_syntagrus-ud-train-b.conllu',
               'ru_syntagrus-ud-train-c.conllu']
TEST_FILES = ['ru_syntagrus-ud-test.conllu']

# ==================== МАППИНГ POS ====================
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

# ==================== УТИЛИТЫ ====================
def normalize(text):
    return text.lower().replace('ё','е')

def simplify_tag(upos):
    return TAG_MAP.get(upos.upper(), 'UNK')

# ==================== СОЗДАНИЕ СЛОВАРЯ ====================
def build_dict_from_files(file_list, folder_path=UD_FOLDER, pickle_file=PICKLE_FILE):
    morph_dict = {}
    for fname in file_list:
        path = os.path.join(folder_path, fname)
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                parts = line.split('\t')
                if len(parts)<4: continue
                form, lemma, upos = parts[1], parts[2], parts[3]
                morph_dict[normalize(form)] = (normalize(lemma), simplify_tag(upos))
    with open(pickle_file,'wb') as f:
        pickle.dump(morph_dict,f)
    print(f"Словарь построен: {len(morph_dict)} форм, сохранено в {pickle_file}")
    return morph_dict

def load_or_build_dict(file_list=TRAIN_FILES, rebuild=False):
    if rebuild or not os.path.exists(PICKLE_FILE):
        return build_dict_from_files(file_list)
    else:
        with open(PICKLE_FILE,'rb') as f:
            print(f"Словарь загружен из {PICKLE_FILE}")
            return pickle.load(f)

# ==================== СУФФИКСНАЯ МОДЕЛЬ ====================
def build_suffix_statistics(file_list, folder_path=UD_FOLDER, max_len=4):
    suffix_stats = defaultdict(Counter)
    for fname in file_list:
        path = os.path.join(folder_path,fname)
        with open(path, encoding='utf-8') as f:
            for line in f:
                line=line.strip()
                if not line or line.startswith('#'): continue
                parts = line.split('\t')
                if len(parts)<4: continue
                form, upos = parts[1].lower().replace('ё','е'), parts[3]
                if not form.isalpha(): continue
                for i in range(1,max_len+1):
                    if len(form)>=i:
                        suffix = form[-i:]
                        suffix_stats[suffix][upos] += 1
    return suffix_stats

def build_suffix_probabilities(suffix_stats):
    suffix_probs={}
    for suffix,counter in suffix_stats.items():
        total=sum(counter.values())
        suffix_probs[suffix]={pos:count/total for pos,count in counter.items()}
    return suffix_probs

def guess_pos_by_suffix(token,suffix_probs,max_len=4):
    token = token.lower().replace('ё','е')
    if re.match(r'.*(ую|ю)$', token) and len(token)>4: return 'VERB',0.9
    if re.match(r'.*(ешь|ет|ем|ете|ют)$', token): return 'VERB',0.95
    if re.match(r'.*(л|ла|ло|ли)$', token): return 'VERB',0.95
    for i in range(max_len,0,-1):
        if len(token)>=i:
            suffix = token[-i:]
            if suffix in suffix_probs:
                pos_probs = suffix_probs[suffix]
                best_pos = max(pos_probs,key=pos_probs.get)
                return best_pos,pos_probs[best_pos]
    return 'X',0.0

# ==================== ЛЕММАТИЗАЦИЯ ====================
def guess_lemma(token):
    tok = normalize(token)
    if re.match(r'.*л[аиы]$', tok): return tok[:-1]+'ать','V'
    if re.match(r'.*(ю|ешь|ет|ем|ете|ют)$', tok): return tok[:-2]+'ать','V'
    return tok,'UNK'

def lemmatize_sentence(sentence, morph_dict, suffix_probs):
    tokens = re.findall(r'[а-яА-ЯёЁa-zA-Z]+',sentence)
    result=[]
    for token in tokens:
        key = normalize(token)
        if key in morph_dict:
            lemma,tag = morph_dict[key]
        else:
            pos,_ = guess_pos_by_suffix(token,suffix_probs)
            lemma = key
            tag = f"{simplify_tag(pos)}?"
        result.append(f"{token}{{{lemma}={tag}}}")
    return ' '.join(result)

# ==================== ОЦЕНКА ТОЧНОСТИ ====================
def evaluate_accuracy_simple(folder_path, morph_dict, suffix_probs):
    total = 0
    correct_pos = 0
    correct_lemma = 0

    for fname in os.listdir(folder_path):
        if not fname.endswith('.conllu'):
            continue

        with open(os.path.join(folder_path, fname), encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split('\t')
                if len(parts) < 4:
                    continue

                form = parts[1]
                gold_lemma = normalize(parts[2])
                gold_upos = parts[3]

                if not form.isalpha():
                    continue

                total += 1
                key = normalize(form)

                # POS
                if key in morph_dict:
                    _, predicted_tag = morph_dict[key]
                    predicted_upos = gold_upos if simplify_tag(gold_upos) == predicted_tag else None
                    predicted_lemma = morph_dict[key][0]
                else:
                    predicted_upos, _ = guess_pos_by_suffix(form, suffix_probs)
                    predicted_lemma = key

                if predicted_upos == gold_upos:
                    correct_pos += 1
                if predicted_lemma == gold_lemma:
                    correct_lemma += 1

    pos_accuracy = correct_pos / total if total else 0
    lemma_accuracy = correct_lemma / total if total else 0

    print("\n========== РЕЗУЛЬТАТЫ ==========")
    print(f"Accuracy POS: {pos_accuracy:.4f}")
    print(f"Accuracy Lemma: {lemma_accuracy:.4f}")

# ==================== MAIN ====================
if __name__=='__main__':
    rebuild = '--rebuild' in sys.argv
    if not os.path.exists(UD_FOLDER):
        print(f"📥 Папка {UD_FOLDER} не найдена, клонируем репозиторий...")
        subprocess.run(['git', 'clone', 'https://github.com/UniversalDependencies/UD_Russian-SynTagRus.git'], check=True)
    morph_dict = load_or_build_dict(TRAIN_FILES,rebuild=rebuild)
    suffix_stats = build_suffix_statistics(TRAIN_FILES)
    suffix_probs = build_suffix_probabilities(suffix_stats)

    if '--eval' in sys.argv:
        evaluate_accuracy_simple(UD_FOLDER, morph_dict, suffix_probs)
        sys.exit()

    # ввод текста
    try:
        for line in sys.stdin:
            line=line.strip()
            if not line: continue
            print(lemmatize_sentence(line,morph_dict,suffix_probs))
    except KeyboardInterrupt:
        pass