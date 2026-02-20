# lemmatizer.py
import re
from utils import normalize, simplify_tag
from suffix_model import guess_pos_by_suffix
from collections import Counter


def guess_lemma(token, pos, lemma_transforms):
    tok = token.lower().replace('ё','е')
    if pos == 'V':
        if re.match(r'.*(ую|ю)$', tok):
            return tok[:-1] + 'ть'
        if re.match(r'.*(у)$', tok):
            return tok + 'ть'
        if re.match(r'.*(ешь|ет|ем|ете|ют)$', tok):
            return tok[:-2] + 'ть'
        if re.match(r'.*(л|ла|ло|ли)$', tok):
            return tok[:-1] + 'ть'
        return tok

    if pos in lemma_transforms:
        rules = lemma_transforms[pos].most_common()
        for (form_suf, lemma_suf), freq in rules:
            if len(tok) <= len(form_suf):
                continue
            if tok.endswith(form_suf):
                base = tok[:-len(form_suf)]
                candidate = base + lemma_suf
                if abs(len(candidate) - len(tok)) <= 2:
                    return candidate


    return tok

def lemmatize_sentence(sentence, morph_dict, suffix_probs, lemma_transforms):
    tokens = re.findall(r'[а-яА-ЯёЁa-zA-Z]+',sentence)
    result=[]

    for token in tokens:
        key = normalize(token)

        if key in morph_dict:
            lemma,tag = morph_dict[key]
        else:
            pos, prob = guess_pos_by_suffix(token,suffix_probs)
            simple_pos = simplify_tag(pos)

            lemma = guess_lemma(token, simple_pos, lemma_transforms)
            tag = f"{simple_pos}?{round(prob, 2)}"

        result.append(f"{token}{{{lemma}={tag}}}")

    return ' '.join(result)