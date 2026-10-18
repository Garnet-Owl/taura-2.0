# Taura 2.0

> *"Taũra"* is Kikuyu for *"Translate."*

**Taura** is an open-source machine translation engine for **Kikuyu ↔ English**, one of the first of its kind for this low-resource Bantu language. The Kikuyu are Kenya's largest ethnic group, with 9 to 10 million speakers making up roughly 17 to 20% of the country's population.

Modern translation tools largely ignore Kikuyu. Taura exists to change that, starting with strong linguistic foundations: curated parallel corpora, morphological segmentation tuned to Kikuyu's agglutinative structure, and cross-lingual embedding alignment using Orthogonal Procrustes mapping.

![Taura 2.0 Web UI](data/assets/taura-iu-screenshot.png)


## What We're Building

Taura is not just a translation API. It is a full pipeline:

- **Corpus curation:** parallel sentence pairs from the Bible (28 books, from the Gospels through Genesis, Exodus, Leviticus, Numbers, Deuteronomy, 1 Kings, 1 Chronicles, 2 Chronicles, Ezekiel, Job, Psalms, Proverbs, Ecclesiastes, Isaiah and Jeremiah) and agriculture sector data (coffee, dairy, poultry, potato, banana, mango, cabbage, avocado): over 20,500 curated pairs and growing
- **Cross-lingual alignment:** monolingual FastText embeddings aligned via iterative Orthogonal Procrustes with three anchor sources (parallel sentence embeddings, seed dictionary, and identical-string vocabulary pairs) and CSLS-based refinement
- **Translation API:** FastAPI service with retrieval and word-by-word modes, top-K candidates, and a lightweight web UI

The long-term goal is to push translation quality to the point where Taura is genuinely useful to Kikuyu speakers, and to serve as a replicable blueprint for other low-resource African languages.


## Performance Progression

> This section tracks the evolution of Taura's cross-lingual alignment. Every row represents a real training run, evaluated on a 100-sentence held-out validation set.

> [!NOTE]
> **Metrics Key:**
> - **BLEU / chrF:** Measures translation similarity to a human reference. Higher is better.
> - **Top-1 / Top-5:** The percentage of times the exact correct translation was in the #1 or Top 5 retrieved results.
> - **MRR (Mean Reciprocal Rank):** How close the correct translation was to rank #1 on average.
> - **MNN (Mutual Nearest Neighbors):** The number of Kikuyu and English vocabulary words that perfectly aligned. Higher means a better vocabulary bridge.

| Run | Direction | BLEU | chrF | Top-1 | Top-5 | MRR | MNN |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Baseline**<br>Raw FastText + simple Procrustes | Ki→En<br>En→Ki | 5.34<br>4.91 | -<br>- | -<br>- | -<br>- | -<br>- | - |
| **2. Hybrid alignment**<br>Sentence anchors + seed dict + identical strings; iterative Procrustes with MNN+CSLS | Ki→En<br>En→Ki | 21.00<br>35.09 | -<br>- | -<br>- | -<br>- | -<br>- | 3,007 |
| **3. Agriculture + Proper-Nouns**<br>+3,852 agri pairs; proper-noun anchors; restored default n-grams | Ki→En<br>En→Ki | 23.36<br>34.92 | 44.16<br>51.92 | 6%<br>27% | 32%<br>50% | 0.208<br>0.398 | 4,788 |
| **4. Expanded Bible Corpus**<br>+Galatians, Ephesians, Philippians, Colossians, 1 Thess (10,255 pairs) | Ki→En<br>En→Ki | 35.27<br>34.38 | 49.10<br>55.18 | 20%<br>22% | 38%<br>41% | 0.305<br>0.320 | 4,859 |
| **5. Psalms Expansion**<br>+Psalms (12,716 pairs total) | Ki→En<br>En→Ki | 33.18<br>35.96 | 49.02<br>56.75 | 25%<br>22% | 44%<br>46% | 0.345<br>0.342 | 5,654 |
| **6. Genesis, Proverbs, Ecclesiastes**<br>+2,670 pairs (15,386 pairs total) | Ki→En<br>En→Ki | 38.67<br>38.53 | 56.04<br>58.76 | 18%<br>20% | 44%<br>48% | 0.299<br>0.328 | 6,571 |
| **7. Jeremiah**<br>+1,364 pairs (16,750 pairs total) | Ki→En<br>En→Ki | 39.18<br>38.73 | 54.38<br>57.62 | 20%<br>27% | 42%<br>52% | 0.317<br>0.386 | 7,109 |
| **8. Exodus + Isaiah**<br>+2,505 validated verse pairs (19,255 pairs total) | Ki→En<br>En→Ki | 28.95<br>35.47 | 44.34<br>53.75 | 16%<br>23% | 38%<br>41% | 0.277<br>0.338 | 7,981 |
| **9. Numbers**<br>+1,288 validated verse pairs (20,643 pairs loaded by training); mean of 2 runs | Ki→En<br>En→Ki | 32.92<br>35.58 | 49.24<br>54.40 | 16.5%<br>24% | 42.5%<br>43% | 0.292<br>0.339 | 8,318 |
| **10. Ezekiel**<br>+1,273 validated verse pairs (21,916 pairs loaded by training); mean of 2 runs | Ki→En<br>En→Ki | 32.20<br>39.04 | 48.02<br>56.40 | 19%<br>21% | 36.5%<br>45.5% | 0.282<br>0.335 | 8,533 |
| **11. Job**<br>+1,070 validated verse pairs (22,986 pairs loaded by training); mean of 2 runs | Ki→En<br>En→Ki | 32.88<br>37.88 | 49.34<br>56.53 | 21%<br>21.5% | 44%<br>46.5% | 0.325<br>0.341 | 8,676 |
| **12. Deuteronomy**<br>+959 validated verse pairs (23,945 pairs loaded by training); mean of 2 runs | Ki→En<br>En→Ki | 35.99<br>33.49 | 50.63<br>52.75 | 21.5%<br>22.5% | 43%<br>46% | 0.330<br>0.341 | 8,679 |
| **13. 1 Chronicles**<br>+942 validated verse pairs (24,887 pairs loaded by training); mean of 2 runs | Ki→En<br>En→Ki | 34.38<br>35.94 | 50.83<br>55.46 | 17%<br>21.5% | 41%<br>46% | 0.290<br>0.341 | 8,805 |
| **14. Leviticus**<br>+859 validated verse pairs (25,746 pairs loaded by training); mean of 2 runs | Ki→En<br>En→Ki | 32.13<br>31.37 | 48.17<br>50.82 | 19%<br>18% | 39.5%<br>38.5% | 0.296<br>0.296 | 8,967 |
| **15. 2 Chronicles**<br>+822 validated verse pairs (26,568 pairs loaded by training); mean of 2 runs | Ki→En<br>En→Ki | 27.01<br>34.30 | 44.42<br>51.07 | 17%<br>19.5% | 40%<br>44% | 0.285<br>0.319 | 9,098 |

Run 12 was an evaluated checkpoint, again the mean of two identical retrains: run C scored Ki→En 35.98 BLEU / 50.11 chrF and En→Ki 35.70 / 55.40 (MNN 8,666); run D scored Ki→En 36.00 / 51.15 and En→Ki 31.28 / 50.10 (MNN 8,692). Against Run 11, Ki→En rose (32.88 to 35.99 BLEU) but En→Ki fell (37.88 to 33.49 BLEU, chrF 56.53 to 52.75). The En→Ki drop comes mostly from run D, which scored 4.4 BLEU below run C on the same data, and run C alone (35.70) is close to Run 11, so this looks like run-to-run noise on the 100-sentence validation set rather than a real regression; however it is a second dip in a row from Run 10's 39.04 and should be watched, since Deuteronomy's legal/ritual vocabulary could shift the En→Ki retrieval pool. The vocabulary bridge (MNN) was flat (8,676 to 8,679). BLEU differences between runs of under about 6 points should not be read as real changes.

Run 13 was an evaluated checkpoint, the mean of two identical retrains: run E scored Ki→En 37.24 BLEU / 53.42 chrF and En→Ki 39.77 / 58.56; run F scored Ki→En 31.52 / 48.23 and En→Ki 32.12 / 52.37 (MNN 8,835 and 8,775). Against Run 12, Ki→En fell slightly (35.99 to 34.38 BLEU, chrF 50.63 to 50.83 flat) and En→Ki recovered (33.49 to 35.94 BLEU, chrF 52.75 to 55.46) toward the Run 10-11 range. The two runs differ by 5.7 BLEU (Ki→En) and 7.6 BLEU (En→Ki) on identical data, larger than every change between Runs 12 and 13, so these movements are noise on the 100-sentence validation set, not a real gain or loss from 1 Chronicles. Top-1 retrieval for Ki→En dipped (21.5% to 17%) for the same reason. The vocabulary bridge (MNN) grew from 8,679 to about 8,805.

Run 14 was an evaluated checkpoint, the mean of two identical retrains on 25,746 pairs (Leviticus added): run G scored Ki→En 30.67 BLEU / 47.55 chrF and En→Ki 22.99 / 46.15 (MNN 8,943); run H scored Ki→En 33.60 / 48.79 and En→Ki 39.74 / 55.50 (MNN 8,991). Against Run 13, Ki→En fell (34.38 to 32.13 BLEU, chrF 50.83 to 48.17) and En→Ki fell (35.94 to 31.37 BLEU, chrF 55.46 to 50.82), so both directions are lower. The averages hide a very wide spread: the two runs differ by 2.9 BLEU (Ki→En) and 16.8 BLEU (En→Ki) on identical data, and run H's En→Ki (39.74) is the best score so far while run G's (22.99) is the worst. Because that gap is far larger than the difference between Runs 13 and 14, the dip is most likely noise on the 100-sentence validation set rather than harm from Leviticus, but this is the third averaged En→Ki figure in four runs below Run 10 and it should be watched; no hyperparameters were changed. The vocabulary bridge (MNN) kept growing (8,805 to about 8,967), the one steady signal.

Run 15 is the latest evaluated checkpoint, the mean of two identical retrains on 26,568 pairs (2 Chronicles added): run I scored Ki→En 28.00 BLEU / 44.19 chrF and En→Ki 31.99 / 51.66 (MNN 9,065); run J scored Ki→En 26.01 / 44.65 and En→Ki 36.61 / 50.49 (MNN 9,131). Against Run 14, En→Ki rose (31.37 to 34.30 BLEU) but chrF was flat (50.82 to 51.07), so that gain is within noise. Ki→En fell again (32.13 to 27.01 BLEU, chrF 48.17 to 44.42), its lowest since Run 3, and unlike earlier dips the two runs agree closely (2.0 BLEU apart), so this one should be read as a real decline rather than noise. Ki→En has now fallen four averaged runs in a row (35.99, 34.38, 32.13, 27.01). The validation set itself has not changed: it is the last 100 pairs in file order, all 89 verses of 1 Thessalonians plus the last 11 verses of Romans. The likely cause is a domain mismatch: every recent addition is Old Testament history or law, which shrinks the share of New Testament letter vocabulary that the English side of this NT-only validation set needs. This is a hypothesis and has not been tested, and no hyperparameters were changed. The vocabulary bridge (MNN) kept growing (about 8,967 to 9,098). A validation set drawn from across the whole corpus is needed before more books can be judged fairly.

The hybrid alignment was the single biggest jump: a **4× BLEU improvement** from baseline.
The recent expansion of the Bible corpus significantly balanced the model, driving Kikuyu→English BLEU up by +12 points and pushing Mutual Nearest Neighbors to 4,859.

**What drove the 5 to 21 BLEU jump:**
Three alignment anchor sources were combined (parallel sentence embeddings, a seed dictionary, and identical-string vocabulary pairs), giving the Procrustes solver a much richer and more diverse set of constraints. Iterative refinement with Mutual Nearest Neighbors and CSLS de-hubbing then pushed the MNN count from near-zero to 3,007, meaning 3,007 Kikuyu vocabulary words found their correct English counterpart through the learned projection.

**What the literature says for similar low-resource Bantu scenarios:**
- Supervised cross-lingual alignment (what we do) consistently outperforms unsupervised methods when at least 1–5k parallel pairs are available [(Conneau et al., MUSE)](https://github.com/facebookresearch/MUSE)
- Cross-lingual transfer from related high-resource languages (e.g. Swahili → Kikuyu) can add 1.5–3.5 BLEU in low-resource Bantu pairs [(Congolese Swahili study)](https://arxiv.org/pdf/2103.10734)
- Chain-of-languages multilingual anchors (English → Swahili → Kikuyu) have shown promise for zero-resource directions [(multilingual anchor chains)](https://arxiv.org/pdf/2311.12489)


## Quick Start

**Requirements:** Python 3.12+, [uv](https://github.com/astral-sh/uv)

```bash
git clone https://github.com/Garnet-Owl/taura-2.0.git
cd taura-2.0
uv sync
```

> **Data & models** are not bundled. Download source files from [Garnet-Owl/taura-datasets](https://huggingface.co/datasets/Garnet-Owl/taura-datasets) on Hugging Face and place them in `data/`. Parallel CSV files are already included in the repo.

```bash
# 1. Prepare dataset
uv run python -m scripts.prepare_dataset

# 2. Train embeddings + alignment
uv run python -m scripts.train_embeddings

# 3. Serve
uv run uvicorn app.serve.main:app --reload
```

Open **[http://localhost:8000](http://localhost:8000)** for the web UI or **[http://localhost:8000/docs](http://localhost:8000/docs)** for the API.


## API

```bash
# Translate
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Mũndũ ũmwe nĩ arakorirũo na thĩna", "source_lang": "ki", "target_lang": "en"}'

# Top-K candidates
curl -X POST http://localhost:8000/translate/candidates \
  -H "Content-Type: application/json" \
  -d '{"text": "the man is reading a book", "source_lang": "en", "target_lang": "ki", "k": 5}'

# Model info
curl http://localhost:8000/model/info
```


## Tests

```bash
uv run pytest
```




## Contributing

Contributions are welcome, especially if you speak Kikuyu, work in low-resource NLP, or want to help expand the corpus. See [AGENTS.md](AGENTS.md) for project standards and [CONTRIBUTING.md](CONTRIBUTING.md) to get started.


## License

MIT. See [LICENSE](LICENSE).
