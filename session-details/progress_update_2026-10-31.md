# Taura 2.0 - Progress Update (2026-10-31)

## Overall Status

Still in Milestone 3: corpus expansion and quality control.

## Current Phase

Latest (2026-11-01, latest): 1 John (50 books) and 2 Timothy (51 books) added; split now 27,306 / 3,452 / 3,363. FastText Run 32 (1 John, 3,445 val; Kaggle `jameswanjiku/taura-fasttext-run32`): Ki->En 34.91 BLEU / 50.11 chrF, En->Ki 36.22 / 56.70, within noise of Run 31 (35.95 / 35.34); models not republished. Earlier: 1 Peter added (49 books; split 27,153 / 3,427 / 3,353); FastText Run 31 below. Earlier: James added (48 books; split 27,071 / 3,415 / 3,342); FastText Run 30 below. Earlier: Nahum added (46 books; split 26,902 / 3,390 / 3,315). GPU run N5 (Kaggle `jameswanjiku/taura-marian-sw`): En->Ki Marian opus-mt-en-mul retrained 12 epochs = 26.79 BLEU / 54.93 chrF on 3,390 val (N4 26.39 on an older val; 1.51 s/sentence CPU int8 beam 4, 78 MB); opus-mt-en-sw base = 7.97 / 36.27 (rejected). Published models unchanged. Run 28 below is the latest FastText run.


Run 23 (Daniel, Hebrews and 148 chapter-number-cleaned verses; 25,770 train pairs, 3,254 val pairs), single Kaggle run (kernel jameswanjiku/taura-fasttext-run23): Ki->En 37.64 BLEU / 53.41 chrF, Top-1 24.2%, MRR 0.328; En->Ki 35.81 / 56.43, Top-1 22.9%, MRR 0.323. Within noise of Run 22; models not republished. Corpus is now 38 books (Ezra added after this run; the split is 25,992 / 3,279 / 3,192, so the next run is Run 24).

Previous: Run 22 (Revelation added, 25,270 train pairs, 3,178 val pairs = Run 21's 3,135 plus Revelation's 43), single Kaggle run (kernel jameswanjiku/taura-fasttext-run22; FastText is CPU-only, the GPU sat idle):
Ki->En 35.74 BLEU / 52.16 chrF, Top-1 23.2%, MRR 0.322; En->Ki 36.83 / 57.38, Top-1 23.3%, MRR 0.326. Within noise of Run 21 (35.69 / 36.63).
Models published to Garnet-Owl/taura-marian-kikuyu-english under fasttext/. Owner rule: training only on Kaggle GPU, never the container CPU.

Previous: Run 21 (Nehemiah added, 24,958 train pairs, 3,135 val pairs = Run 20's 3,096 plus Nehemiah's 39), mean of two retrains (35.71 / 51.96 and 35.67 / 52.00 Ki->En; 37.08 / 56.82 and 36.19 / 57.23 En->Ki):
Ki->En 35.69 BLEU / 51.98 chrF, Top-1 22.8%, MRR 0.313; En->Ki 36.63 / 57.03, Top-1 23.7%, MRR 0.327.
Within retrain noise of Runs 19-20 (Run 20 pair spread was 2.5 BLEU; Run 21's is 0.05 / 0.9). Training's built-in evaluation was OOM-killed with 4 workers; worker count is now also capped by memory (2 on this 15 GB container), so no wrapper was needed.

Previous: Run 20 (Joshua + Judges added, 24,628 train pairs, 3,096 val pairs = Run 19's 2,984 plus Joshua's 58 and Judges' 54), mean of two retrains (30.47 / 33.10 and 34.68 / 37.06):
Ki->En 31.79 BLEU / 47.13 chrF, Top-1 21.0%, MRR 0.298; En->Ki 35.87 / 55.17, Top-1 23.3%, MRR 0.324.
Within retrain noise of Run 19 (spread 2.6 / 2.4 BLEU between the two retrains). Evaluation with 4 worker processes was OOM-killed on the 15 GB
container (each worker loads a 2.4 GB model); it was re-run with 2 workers via a throwaway wrapper, so no repo change was needed.

Previous: Run 19 (2 Samuel added, 23,593 train pairs, 2,984 val pairs = Run 18's 2,906 plus 2 Samuel's 78), mean of two retrains:
Ki->En 35.11 BLEU / 50.75 chrF, Top-1 22.8%, MRR 0.315; En->Ki 34.87 / 55.54, Top-1 22.7%, MRR 0.317.
The two retrains differ by 2.2 BLEU Ki->En and 0.5 En->Ki, so the +3.7 Ki->En over Run 18 is within noise.
A concurrent session ran two more independent Run 19 retrains on the same split: 32.38 / 32.89 and 35.44 / 33.52 BLEU
(Ki->En / En->Ki), mean 33.91 / 33.21. Across all four retrains the spread is about 3 BLEU per direction.

Previous: Run 18 (2 Kings added, 23,047 train pairs, 2,906 val pairs = Run 17's 2,836 plus 2 Kings' 70), mean of two retrains:
Ki->En 31.42 BLEU / 47.43 chrF, Top-1 20.3%, MRR 0.287; En->Ki 34.33 / 54.48, Top-1 21.9%, MRR 0.309; MNN about 8,699.
Within Run 17's run-to-run spread; the two Run 18 retrains agree within 0.8 BLEU.

The split is now stable: each pair is placed in train / validation / test by a seeded hash of its text (seed 42), so adding a
book only appends pairs. Run 17 (new baseline, 1 Samuel included) trained on 22,467 train pairs and was scored on 2,836
validation pairs, mean of two retrains (M and N):

- Kikuyu -> English: 33.01 BLEU, 49.22 chrF, Top-1 21.7%, Top-5 39.6%, MRR 0.305.
- English -> Kikuyu: 34.67 BLEU, 54.82 chrF, Top-1 21.8%, Top-5 38.9%, MRR 0.304.
- MNN about 8,668.

The runs differ by 3.8 BLEU Ki->En. Run 17 is not comparable with Run 16 (different validation verses); Run 18 onward will
be. The test split has not been used.

Run 16 (previous shuffled split, 2,723 validation pairs): Ki->En 30.82 / 47.41, En->Ki 35.84 / 55.65.

GPU experiments below were scored on the Run 16 validation split; they need re-scoring on the stable split (the Kaggle
dataset `jameswanjiku/taura-splits-20261018` now holds the new train.tsv / val.tsv).

GPU experiments on the Run 16 validation split (generated translations, not retrieval; not directly comparable with FastText):

- NLLB-600M fine-tuned (Kaggle T4, 75 min): Ki->En 37.95 BLEU / 57.51 chrF, En->Ki 27.51 / 54.85. 623 MB int8, 1.5-3.4 s
  per sentence on CPU. Too slow for the CPU target.
- Marian opus-mt fine-tuned (Kaggle T4, 20 min, 77M params per direction): Ki->En 39.21 / 55.67, En->Ki 22.13 / 50.45
  (beam 4). 78 MB int8 each; 0.42 s (Ki->En) and 1.0 s (En->Ki) per sentence greedy on CPU, 75 / 137 ms batched; greedy
  CPU int8 scores 33.98 / 20.67 BLEU. Served by the API's 'neural' method. Model: private HF repo
  Garnet-Owl/taura-marian-kikuyu-english.

GPU run N3 (Kaggle `jameswanjiku/taura-marian-ft` v2, Marian, stable split, fixed epochs Ki->En 4 / En->Ki 7, 30 min T4),
scored on CPU int8 on Run 18's 2,906 val pairs: Ki->En 39.56 / 56.30 (beam 4), 34.98 / 53.07 (greedy); En->Ki 25.19 / 53.47
(beam 4), 24.22 / 52.32 (greedy). Latency per sentence beam 4: 0.59 s / 1.34 s; greedy 0.29 s / 0.64 s. 78 MB per
direction. Uploaded to HF `Garnet-Owl/taura-marian-kikuyu-english` (replaces N2; N2 is in the repo history).

GPU run N4 (Kaggle `jameswanjiku/taura-marian-ft` v3, En->Ki only, 12 epochs at lr 2e-4, 24,118 train pairs incl.
Joshua, 36 min T4), scored on CPU int8 beam 4 on the current 3,042 val pairs: En->Ki 26.39 BLEU / 54.36 chrF (N3 on the same
pairs: 25.15 / 53.61; on Run 18's 2,906: 26.26 vs 25.19). 2.05 s per sentence on a seeded 100-sentence sample (N3 2.09 s),
78 MB. Replaces en_ki in HF `Garnet-Owl/taura-marian-kikuyu-english`; Ki->En stays N3. The Kaggle dataset
`jameswanjiku/taura-splits-20261018` now holds the current train.tsv / val.tsv (with Joshua).

## Corpus

32 Bible books plus agriculture data: 30,266 pairs loaded, 30,101 unique (Joshua added 2026-10-31; split now 24,118 train / 3,042 val / 2,941 test).

## Next Work

1. Improve En->Ki further (26.39 BLEU with N4, still the weak direction): e.g. add Kikuyu tokens to the en-mul vocabulary or
   back-translate monolingual Kikuyu; compare on the same val.tsv with CPU latency.
2. Joshua, Judges and Nehemiah are extracted and trained (Run 21). Next book: the largest without an aligned CSV (check MASTER_PLAN / data/parallel).

## Blockers

None.

## Owner Decisions (2026-10-18)

- Validation split: seeded random 80/10/10 (train/validation/test) across all books. Done in Run 16.
- Method: experiment with lighter translation models trained on the Kaggle GPU, provided inference runs fast on CPU.
  Kaggle GPU access was verified this session (2x Tesla T4).

Run 24 (Ezra and Zechariah; 26,147 train pairs, 3,309 val pairs), single Kaggle run (kernel jameswanjiku/taura-fasttext-run24): Ki->En 36.13 BLEU / 51.68 chrF, Top-1 23.7%, MRR 0.323; En->Ki 37.32 / 56.35, Top-1 23.3%, MRR 0.326. Versus Run 23 (37.64 / 35.81): Ki->En down 1.5, En->Ki up 1.5, both inside run-to-run noise, so the two books made no measurable difference. Models not republished. Corpus is 39 books.

Run 25 (Hosea and Esther; 26,439 train pairs, 3,346 val pairs), single Kaggle run (kernel jameswanjiku/taura-fasttext-run25): Ki->En 34.86 BLEU / 50.97 chrF, Top-1 22.9%, MRR 0.315; En->Ki 37.94 / 58.26, Top-1 23.9%, MRR 0.329. Versus Run 24 (36.13 / 37.32): Ki->En down 1.3 BLEU, En->Ki up 0.6 BLEU and 1.9 chrF; the validation set also grew, so differences are within run-to-run noise. Models not republished. Corpus is 41 books.

Run 26 (Lamentations; 26,565 train pairs, 3,357 val pairs), single Kaggle run (kernel jameswanjiku/taura-fasttext-run26): Ki->En 35.70 BLEU / 51.21 chrF, Top-1 23.5%, MRR 0.322; En->Ki 37.55 / 56.88, Top-1 22.9%, MRR 0.324. Versus Run 25 (34.86 / 37.94): Ki->En up 0.8 BLEU, En->Ki down 0.4 BLEU and 1.4 chrF, within run-to-run noise. Models not republished. Corpus is 42 books on this run; Amos (43rd book) is extracted but not yet in a training run.

Run 27 (Amos, Song of Solomon; 26,780 train pairs, 3,378 val pairs), single Kaggle run (kernel jameswanjiku/taura-fasttext-run27): Ki->En 34.89 BLEU / 50.37 chrF, Top-1 24.2%, MRR 0.328; En->Ki 35.03 / 55.72, Top-1 22.2%, MRR 0.312. Versus Run 26 (35.70 / 37.55): Ki->En down 0.8, En->Ki down 2.5 BLEU; the val set gained 21 prophetic/poetic verses, so likely noise, but watch the next run. Models not republished. Corpus is 44 books.

Run 28 (Micah; 26,863 train pairs, 3,388 val pairs), single Kaggle run (kernel jameswanjiku/taura-fasttext-run28): Ki->En 35.05 BLEU / 51.14 chrF, Top-1 23.8%, MRR 0.329; En->Ki 39.32 / 58.79, Top-1 23.8%, MRR 0.331. Versus Run 27 (34.89 / 35.03): Ki->En +0.2, En->Ki +4.3 BLEU, recovering the Run 27 dip; retrain noise is ~3 BLEU per direction, so treat as noise. Models not republished. Corpus is 45 books.

Run 29 (1 Timothy; 26,950 train pairs, 3,401 val pairs), single Kaggle run (kernel jameswanjiku/taura-fasttext-run29): Ki->En 36.35 BLEU / 51.63 chrF, Top-1 24.1%, MRR 0.329; En->Ki 35.91 / 56.23, Top-1 24.0%, MRR 0.327. Versus Run 28 (35.05 / 39.32): Ki->En +1.3, En->Ki -3.4 BLEU, within retrain noise. Models not republished. Corpus is 46 books. Note: the previous handoff named Nahum as next, but larger books still lack CSVs (James 108, 1 Peter 105, 1 John 105, Ruth 85, 2 Timothy 83, Joel 73).

Run 30 (James; 27,071 train pairs, 3,415 val pairs), single Kaggle run (kernel jameswanjiku/taura-fasttext-run30): Ki->En 35.52 BLEU / 50.69 chrF, Top-1 24.2%, MRR 0.327; En->Ki 36.19 / 56.15, Top-1 22.8%, MRR 0.321. Versus Run 29 (36.35 / 35.91): Ki->En -0.8, En->Ki +0.3 BLEU, inside run-to-run noise (~3 BLEU). Models not republished. Corpus is 48 books.

Run 31 (1 Peter; 27,153 train pairs, 3,427 val pairs), single Kaggle run (kernel jameswanjiku/taura-fasttext-run31): Ki->En 35.95 BLEU / 51.82 chrF, Top-1 24.0%, MRR 0.330; En->Ki 35.34 / 56.28, Top-1 22.1%, MRR 0.315. Versus Run 30 (35.52 / 36.19): Ki->En +0.4, En->Ki -0.8 BLEU, inside run-to-run noise (~3 BLEU). Models not republished. Corpus is 49 books.
