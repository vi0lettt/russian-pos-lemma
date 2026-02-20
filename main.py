# main.py
import os
import sys
import subprocess
from config import UD_FOLDER, TRAIN_FILES
from dictionary import load_or_build_dict
from suffix_model import build_suffix_statistics, build_suffix_probabilities
from lemmatizer import lemmatize_sentence
from evaluation import evaluate_accuracy_simple

if __name__=='__main__':
    rebuild = '--rebuild' in sys.argv

    if not os.path.exists(UD_FOLDER):
        print(f"Папка {UD_FOLDER} не найдена, клонируем репозиторий...")
        subprocess.run(['git','clone','https://github.com/UniversalDependencies/UD_Russian-SynTagRus.git'], check=True)

    # загрузка словаря
    morph_dict, lemma_transforms = load_or_build_dict(
        TRAIN_FILES,
        folder_path=UD_FOLDER,
        rebuild=rebuild
    )

    # построение суффиксной модели
    suffix_stats = build_suffix_statistics(TRAIN_FILES, folder_path=UD_FOLDER)
    suffix_probs = build_suffix_probabilities(suffix_stats)

    if '--eval' in sys.argv:
        evaluate_accuracy_simple(UD_FOLDER, morph_dict, suffix_probs)
        sys.exit()

    # ввод текста
    try:
        for line in sys.stdin:
            line=line.strip()
            if not line: continue
            print(lemmatize_sentence(line,morph_dict,suffix_probs,lemma_transforms))
    except KeyboardInterrupt:
        pass
