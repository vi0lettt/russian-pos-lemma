# suffix_model.py
import re
from collections import defaultdict, Counter

def build_suffix_statistics(file_list, folder_path='.', max_len=4):
    suffix_stats = defaultdict(Counter)
    for fname in file_list:
        path = f"{folder_path}/{fname}"
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
                return max(pos_probs,key=pos_probs.get), max(pos_probs.values())
    return 'X',0.0