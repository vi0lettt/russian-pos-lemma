# evaluation.py
import os
from utils import normalize, simplify_tag
from suffix_model import guess_pos_by_suffix

def evaluate_accuracy_simple(folder_path, morph_dict, suffix_probs):
    total = 0
    correct_pos = 0
    correct_lemma = 0

    for fname in os.listdir(folder_path):
        if not fname.endswith('.conllu'): continue
        with open(os.path.join(folder_path,fname), encoding='utf-8') as f:
            for line in f:
                line=line.strip()
                if not line or line.startswith('#'): continue
                parts = line.split('\t')
                if len(parts)<4: continue
                form, gold_lemma, gold_upos = parts[1], normalize(parts[2]), parts[3]
                if not form.isalpha(): continue
                total += 1
                key = normalize(form)

                # POS
                if key in morph_dict:
                    _, predicted_tag = morph_dict[key]
                    predicted_upos = gold_upos if simplify_tag(gold_upos)==predicted_tag else None
                    predicted_lemma = morph_dict[key][0]
                else:
                    predicted_upos,_ = guess_pos_by_suffix(form,suffix_probs)
                    predicted_lemma = key

                if predicted_upos==gold_upos: correct_pos += 1
                if predicted_lemma==gold_lemma: correct_lemma += 1

    print("\n========== РЕЗУЛЬТАТЫ ==========")
    print(f"Accuracy POS: {correct_pos/total:.2f}")
    print(f"Accuracy Lemma: {correct_lemma/total:.2f}")