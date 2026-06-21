# Model Scaling and Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Optimize Kikuyu-English FastText translation models and cross-lingual alignments by cleaning the monolingual unsupervised training corpora and searching for optimal training hyperparameters.

**Architecture:** We will update the dataset preparation script to apply standard normalization (lowercasing, punctuation removal) to the unsupervised monolingual text outputs. We will implement a grid search script that runs over specified FastText unsupervised training parameters and evaluates the learned projection mapping on validation set retrieval accuracy. Finally, we will train models using the optimal configuration, evaluate on the test split, and run verification.

**Tech Stack:** Python 3.12, FastText, NumPy, SacreBLEU, Pytest, uv.

---

### Task 1: Clean Unsupervised Monolingual Corpora

**Files:**
- Modify: `scripts/prepare_dataset.py`
- Test: Run dataset preparation and check files

- [ ] **Step 1: Apply normalization to monolingual export in `scripts/prepare_dataset.py`**
  Modify the export block at lines 67-73 of `scripts/prepare_dataset.py` to import `normalize_text` and clean sentences before writing them to `train.kikuyu` and `train.english`.

  Expected change in `scripts/prepare_dataset.py`:
  ```python
      # Also save raw monolingual text files for training FastText embeddings
      # (one sentence per line)
      from app.api.preprocessing import normalize_text
      for lang, idx in [("kikuyu", 0), ("english", 1)]:
          train_lang_path = os.path.join("data", f"train.{lang}")
          with open(train_lang_path, "w", encoding="utf-8") as f:
              for pair in train:
                  sentence = pair[idx]
                  normalized = normalize_text(sentence)
                  if normalized:
                      f.write(f"{normalized}\n")
          print(f"Saved raw normalized monolingual sentences to {train_lang_path}")
  ```

- [ ] **Step 2: Run the dataset preparation script to regenerate monolingual files**
  Run: `uv run python -m scripts.prepare_dataset`
  Expected output:
  ```
  Downloading dataset from Hugging Face...
  ...
  Saved raw normalized monolingual sentences to data/train.kikuyu
  Saved raw normalized monolingual sentences to data/train.english
  ```

- [ ] **Step 3: Run the tests to make sure everything is green**
  Run: `uv run pytest`
  Expected: 22 passed.

- [ ] **Step 4: Commit changes**
  ```bash
  git add scripts/prepare_dataset.py
  git commit -m "feat: normalize monolingual corpora during dataset preparation"
  ```

---

### Task 2: Create Hyperparameter Tuning Script

**Files:**
- Create: `scripts/tune_hyperparameters.py`
- Test: Run the script for a single configuration first

- [ ] **Step 1: Implement `scripts/tune_hyperparameters.py`**
  Create a grid search script that runs over specified FastText unsupervised training parameters and evaluates the learned projection mapping on validation set retrieval accuracy.

  Write the file content:
  ```python
  """Script to search for optimal FastText hyperparameters on validation set."""

  import os
  import csv
  import numpy as np
  import fasttext
  from typing import Any, Dict, List, Tuple
  from app.api.embeddings import (
      get_sentence_embedding,
      learn_alignment_matrix,
      CrossLingualTranslator,
  )
  from scripts.train_embeddings import load_sentences, evaluate_translator

  def tune_model(
      train_ki_path: str,
      train_en_path: str,
      train_tsv_path: str,
      val_tsv_path: str,
      params: Dict[str, Any]
  ) -> Tuple[float, float]:
      """Trains FastText and returns Kikuyu->English and English->Kikuyu validation Top-1 accuracy."""
      dim = params.get("dim", 100)
      epoch = params.get("epoch", 15)
      lr = params.get("lr", 0.1)
      ws = params.get("ws", 5)
      minCount = params.get("minCount", 1)
      model_type = params.get("model", "skipgram")
      minn = params.get("minn", 3)
      maxn = params.get("maxn", 6)

      # Train temporary models
      ki_model = fasttext.train_unsupervised(
          train_ki_path,
          model=model_type,
          dim=dim,
          epoch=epoch,
          lr=lr,
          ws=ws,
          minCount=minCount,
          minn=minn,
          maxn=maxn,
          thread=4
      )
      en_model = fasttext.train_unsupervised(
          train_en_path,
          model=model_type,
          dim=dim,
          epoch=epoch,
          lr=lr,
          ws=ws,
          minCount=minCount,
          minn=minn,
          maxn=maxn,
          thread=4
      )

      # Learn alignment matrices
      train_ki, train_en = load_sentences(train_tsv_path)
      X = np.array([get_sentence_embedding(ki_model, s, dim=dim) for s in train_ki]).T
      Y = np.array([get_sentence_embedding(en_model, s, dim=dim) for s in train_en]).T

      W_ki_en = learn_alignment_matrix(X, Y)
      W_en_ki = learn_alignment_matrix(Y, X)

      # Evaluate
      val_ki, val_en = load_sentences(val_tsv_path)
      translator_ki_en = CrossLingualTranslator(ki_model, en_model, W_ki_en, val_en)
      translator_en_ki = CrossLingualTranslator(en_model, ki_model, W_en_ki, val_ki)

      metrics_ki_en = evaluate_translator(translator_ki_en, val_ki, val_en)
      metrics_en_ki = evaluate_translator(translator_en_ki, val_en, val_ki)

      return metrics_ki_en["accuracy_top1"], metrics_en_ki["accuracy_top1"]

  def main() -> None:
      train_ki = "data/train.kikuyu"
      train_en = "data/train.english"
      train_tsv = "data/train.tsv"
      val_tsv = "data/val.tsv"

      # Hyperparameter Grid
      grid = []
      for model_type in ["skipgram", "cbow"]:
          for dim in [100, 150]:
              for epoch in [15, 25]:
                  for lr in [0.05, 0.1]:
                      for ws in [5, 8]:
                          grid.append({
                              "model": model_type,
                              "dim": dim,
                              "epoch": epoch,
                              "lr": lr,
                              "ws": ws,
                              "minCount": 1,
                              "minn": 3,
                              "maxn": 6,
                          })

      print(f"Starting grid search over {len(grid)} configurations...")
      best_ki_en = 0.0
      best_en_ki = 0.0
      best_params = {}

      for idx, params in enumerate(grid):
          print(f"\n[{idx+1}/{len(grid)}] Evaluating params: {params}")
          try:
              ki_en_acc, en_ki_acc = tune_model(
                  train_ki, train_en, train_tsv, val_tsv, params
              )
              avg_acc = (ki_en_acc + en_ki_acc) / 2.0
              print(f"Val Accuracy -> ki_en: {ki_en_acc:.4f}, en_ki: {en_ki_acc:.4f}, avg: {avg_acc:.4f}")

              if avg_acc > (best_ki_en + best_en_ki) / 2.0:
                  best_ki_en = ki_en_acc
                  best_en_ki = en_ki_acc
                  best_params = params
                  print(f"New best average accuracy: {avg_acc:.4f}!")
          except Exception as e:
              print(f"Error evaluating config: {e}")

      print("\n=== Grid Search Completed ===")
      print(f"Best Configuration: {best_params}")
      print(f"Best Val Accuracy -> ki_en: {best_ki_en:.4f}, en_ki: {best_en_ki:.4f}")

  if __name__ == "__main__":
      main()
  ```

- [ ] **Step 2: Commit tuning script**
  ```bash
  git add scripts/tune_hyperparameters.py
  git commit -m "feat: add hyperparameter tuning script for FastText model optimization"
  ```

---

### Task 3: Execute Grid Search and Update Model Training

**Files:**
- Run: `scripts/tune_hyperparameters.py`
- Modify: `scripts/train_embeddings.py`

- [ ] **Step 1: Run hyperparameter search**
  Run: `uv run python -m scripts.tune_hyperparameters`
  Expected output: Grid search logs showing validation accuracy improvement. Keep track of the best config.

- [ ] **Step 2: Update `scripts/train_embeddings.py` with best parameters**
  Update the main hyperparameters in `scripts/train_embeddings.py` to match the best configuration discovered by the grid search.
  For example, if `cbow` with `dim=150`, `epoch=25`, `lr=0.1`, `ws=8` is best, update lines 35-45 and 107-108 in `scripts/train_embeddings.py`.

- [ ] **Step 3: Run the training script**
  Run: `uv run python -m scripts.train_embeddings`
  Expected output: Training completes successfully with the new hyperparameter configurations, and saves models and metrics.

- [ ] **Step 4: Commit changes**
  ```bash
  git add scripts/train_embeddings.py
  git commit -m "feat: update train_embeddings with optimal search hyperparameters"
  ```

---

### Task 4: Re-evaluate on Test Set and Verify API

**Files:**
- Run: `scripts/evaluate.py`
- Test: `app/tests/test_api.py`

- [ ] **Step 1: Run the evaluation script**
  Run: `uv run python -m scripts.evaluate`
  Expected output: Score summary showing new BLEU and ChrF scores, saved to `models/evaluation_metrics.json`.

- [ ] **Step 2: Run pytest to check unit & integration tests**
  Run: `uv run pytest`
  Expected output: 22 passed.

- [ ] **Step 3: Update `CHANGELOG.md`**
  Append 3-5 bullet points under `[Unreleased]` for the model scaling and optimization tasks completed.

- [ ] **Step 4: Commit changes**
  ```bash
  git add models/evaluation_metrics.json CHANGELOG.md
  git commit -m "chore: evaluate optimized models on test set and document changes"
  ```
