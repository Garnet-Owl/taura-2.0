# Taura: A Case Study in Low-Resource Bantu Machine Translation

*Living Research Wiki & Whitepaper Draft*

## 1. Abstract / Introduction

The Kikuyu language (Gĩkũyũ) is a Bantu language spoken by approximately 9 to 10 million people in Kenya. Despite its demographic significance, it remains severely underrepresented in modern Natural Language Processing (NLP) and Machine Translation (MT) systems. The **Taura** project represents an iterative, empirical approach to building a functional Kikuyu-English translation engine starting from a zero-resource paradigm.

This document tracks our ongoing findings, architectural decisions, and data curation challenges. It serves as a living foundation for future publication.

---

## 2. Corpus Curation & Data Engineering

One of the largest hurdles in low-resource MT is the lack of clean parallel corpora. We rely heavily on domain-specific texts, primarily religious texts (the Bible) and agricultural data, to bootstrap our datasets.

### 2.1 The "Toxic Anchor" Phenomenon and Alignment Drift
During the extraction of parallel texts from English and Kikuyu PDFs, we utilized a coordinate-matching algorithm (Chapter:Verse) instead of naive sentence-by-sentence alignment to ensure high precision.

**Observation:** We discovered that seemingly minor extraction errors can have catastrophic global effects on vector alignment. For example, a PDF header parsing bug in the English Genesis text caused 40 verses in Chapter 50 to be mislabeled as Chapter 49. Because the Kikuyu text extracted perfectly, the English Chapter 50 verses were misaligned with random Kikuyu Chapter 49 verses.
- **Impact:** These 40 "toxic pairs" acted as massive negative anchors during Orthogonal Procrustes projection, degrading the entire dictionary space. Kikuyu → English BLEU dropped by 4.6 points, and Top-5 retrieval accuracy plummeted by 10%.
- **Resolution:** Fixing the offset and restoring the missing 40 verses instantly restored the global alignment space, pushing the Mutual Nearest Neighbors (MNN) up by over 500 words and drastically improving BLEU.
- **Conclusion:** In extremely low-resource settings, data cleanliness vastly outweighs data volume. A 0.2% misalignment in the corpus can degrade the entire projection matrix.

---

## 3. Linguistic Challenges & Morphological Segmentation

Kikuyu is highly agglutinative, heavily relying on prefixes and suffixes to denote tense, subject, object, and aspect. This creates sparse vocabularies when using standard whitespace tokenization.

### 3.1 Morfessor & Unsupervised Segmentation
To combat vocabulary sparsity, we applied **Morfessor**, an unsupervised morphological segmentation tool.
- By training Morfessor on the Kikuyu monolingual corpus, we enabled the engine to split complex agglutinative words into subword morphemes (e.g., breaking down a verb into its subject marker, tense marker, and root).
- This allowed the FastText embeddings to map syntactic components more accurately to English equivalents.

### 3.2 Embedding N-Gram Adjustments
Standard FastText configurations (`minn=3`, `maxn=6`) are optimized for Indo-European languages. Because Kikuyu morphemes (especially prefixes) can be as short as 1 or 2 characters, we tightened the character n-gram range to `minn=2` and `maxn=7`. This allows the model to correctly encode short morphological markers, increasing retrieval accuracy.

---

## 4. Cross-Lingual Embedding Alignment

Instead of relying solely on unsupervised techniques, which often fail on highly distant language pairs, we use a **Hybrid Supervised Procrustes Alignment**.

### 4.1 Multi-Source Anchoring
We supply the Procrustes solver with a highly diverse set of constraints by combining three distinct anchor sources:
1. **Parallel Sentence Embeddings:** Means of sentence vectors from our curated parallel corpus.
2. **Seed Dictionaries:** Legacy word-to-word mappings.
3. **Identical String Matching:** Exploiting shared proper nouns, loanwords, and numbers.

### 4.2 Iterative Refinement
Using Cross-Domain Similarity Local Scaling (CSLS) and Mutual Nearest Neighbors (MNN), the projection matrices undergo iterative refinement. This combination pushed our exact-vocabulary overlap from near-zero in standard unsupervised runs to over **7,100 MNN pairs**, representing a robust, learned bilingual dictionary.

---

## 5. Evaluation Dynamics: Interpreting Metric Fluctuations

As we systematically inject new books (e.g., Psalms, Genesis, Jeremiah) into the parallel corpus, we frequently observe counterintuitive metric fluctuations.

### 5.1 The "Crowded Vector Space" Phenomenon (Top-1 vs. Top-5)
When adding large volumes of new vocabulary (such as the 1,364 verses of Jeremiah), we observed **Top-1 retrieval accuracy increase, while Top-5 accuracy decreased.**
- **Analysis:** As the retrieval pool expands, the vector space becomes significantly more crowded. The model becomes more precise at nailing the exact correct sentence (Top-1 rises), but the increased presence of "distractor" sentences (sentences with similar vocabulary) makes the immediate neighborhood more competitive, occasionally pushing correct answers out of the Top 5.

### 5.2 Word Overlap vs. Character Overlap (BLEU vs. chrF)
Domain shifts often decouple evaluation metrics. Injecting prophetic, poetic texts like Jeremiah introduces entirely new semantic fields (e.g., destruction, exile).
- **Analysis:** We observed BLEU (word-level match) rising while chrF (character-level match) slightly dropped. The model successfully mapped the new whole-word semantic concepts, but the sudden influx of novel morphological structures and inflections temporarily increased character-level noise.

---

## 6. Future Work

- **Sequence-to-Sequence Modeling:** Utilizing the FastText retrieval engine as a diagnostic baseline, the next phase involves LoRA fine-tuning on the `facebook/nllb-200-distilled-600M` model.
- **Multilingual Transfer:** Exploring zero-shot or few-shot transfer using Swahili as an intermediary high-resource Bantu language.
