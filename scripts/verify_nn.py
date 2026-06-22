import sys
import fasttext
from app.api import config


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    print("Loading models...")
    ki_model = fasttext.load_model(config.KI_MODEL_PATH)
    en_model = fasttext.load_model(config.EN_MODEL_PATH)

    print("\n--- Kikuyu Nearest Neighbors ---")
    ki_words = ["Ngai", "mũndũ", "Bibilia", "kũingĩra", "maitho"]
    for word in ki_words:
        print(f"Nearest to '{word}': {ki_model.get_nearest_neighbors(word, k=5)}")

    print("\n--- English Nearest Neighbors ---")
    en_words = ["God", "man", "Bible", "enter", "eyes"]
    for word in en_words:
        print(f"Nearest to '{word}': {en_model.get_nearest_neighbors(word, k=5)}")


if __name__ == "__main__":
    main()
