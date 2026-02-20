# lemmatizer.py
import re
from utils import normalize, simplify_tag
from suffix_model import guess_pos_by_suffix

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
            pos, conf = guess_pos_by_suffix(token, suffix_probs)
            lemma = key
            tag = f"{simplify_tag(pos)}?{round(conf, 2)}"
        result.append(f"{token}{{{lemma}={tag}}}")
    return ' '.join(result)