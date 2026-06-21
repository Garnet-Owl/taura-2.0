// Taura 2.0 Web UI Translation Controller SPA

document.addEventListener("DOMContentLoaded", () => {
    // Elements
    const sourceLangSelect = document.getElementById("source-lang");
    const targetLangSelect = document.getElementById("target-lang");
    const swapLangsBtn = document.getElementById("swap-langs");
    const methodRetrieval = document.getElementById("method-retrieval");
    const methodWbw = document.getElementById("method-wbw");
    const sourceTextarea = document.getElementById("source-text");
    const charCountSpan = document.getElementById("char-count");
    const clearTextBtn = document.getElementById("clear-text");
    const translateBtn = document.getElementById("translate-btn");
    const targetTextPlaceholder = document.getElementById("target-text-placeholder");
    const targetTextDiv = document.getElementById("target-text");
    const loadingSpinner = document.getElementById("loading-spinner");
    const copyBtn = document.getElementById("copy-btn");
    
    // Details & Feedback Panels
    const detailsCard = document.getElementById("details-card");
    const alignmentInfo = document.getElementById("alignment-info");
    const feedbackCard = document.getElementById("feedback-card");
    const feedbackDetails = document.getElementById("feedback-details");
    const feedbackComment = document.getElementById("feedback-comment");
    const submitFeedbackBtn = document.getElementById("submit-feedback-btn");
    const feedbackSuccessMsg = document.getElementById("feedback-success-msg");
    const ratingButtons = document.querySelectorAll(".rating-btn");

    let currentTranslation = {
        source_text: "",
        target_text: "",
        source_lang: "",
        target_lang: "",
        method: ""
    };
    let currentRating = null;

    // 1. Language Swapping & Sync Logic
    function handleLanguageSync(changedElement) {
        const src = sourceLangSelect.value;
        const tgt = targetLangSelect.value;
        
        if (src === tgt) {
            if (changedElement === sourceLangSelect) {
                targetLangSelect.value = src === "en" ? "ki" : "en";
            } else {
                sourceLangSelect.value = tgt === "en" ? "ki" : "en";
            }
        }
    }

    sourceLangSelect.addEventListener("change", () => handleLanguageSync(sourceLangSelect));
    targetLangSelect.addEventListener("change", () => handleLanguageSync(targetLangSelect));

    swapLangsBtn.addEventListener("click", () => {
        const temp = sourceLangSelect.value;
        sourceLangSelect.value = targetLangSelect.value;
        targetLangSelect.value = temp;
        
        // Swap textareas content if output exists
        const srcText = sourceTextarea.value;
        const tgtText = targetTextDiv.textContent;
        
        if (tgtText && !targetTextDiv.classList.contains("hidden")) {
            sourceTextarea.value = tgtText;
            targetTextDiv.textContent = srcText;
            charCountSpan.textContent = `${tgtText.length} / 500`;
            currentTranslation.source_text = tgtText;
            currentTranslation.target_text = srcText;
            currentTranslation.source_lang = sourceLangSelect.value;
            currentTranslation.target_lang = targetLangSelect.value;
        }
    });

    // 2. Character Counting & UI Helpers
    sourceTextarea.addEventListener("input", () => {
        const len = sourceTextarea.value.length;
        charCountSpan.textContent = `${len} / 500`;
    });

    clearTextBtn.addEventListener("click", () => {
        sourceTextarea.value = "";
        charCountSpan.textContent = "0 / 500";
        targetTextPlaceholder.classList.remove("hidden");
        targetTextDiv.classList.add("hidden");
        targetTextDiv.textContent = "";
        copyBtn.disabled = true;
        detailsCard.classList.add("hidden");
        feedbackCard.classList.add("hidden");
        resetFeedbackForm();
    });

    // 3. Copy Clipboard
    copyBtn.addEventListener("click", () => {
        const text = targetTextDiv.textContent;
        if (text) {
            navigator.clipboard.writeText(text).then(() => {
                const icon = copyBtn.querySelector("i");
                icon.className = "fa-solid fa-check";
                copyBtn.style.color = "var(--success)";
                setTimeout(() => {
                    icon.className = "fa-regular fa-copy";
                    copyBtn.style.color = "";
                }, 2000);
            });
        }
    });

    // 4. Perform Translation Action
    async function performTranslation() {
        const text = sourceTextarea.value.trim();
        if (!text) return;

        const sourceLang = sourceLangSelect.value;
        const targetLang = targetLangSelect.value;
        const method = methodRetrieval.checked ? "retrieval" : "word-by-word";

        // Show spinner, hide text output
        targetTextPlaceholder.classList.add("hidden");
        targetTextDiv.classList.add("hidden");
        loadingSpinner.classList.remove("hidden");
        copyBtn.disabled = true;
        detailsCard.classList.add("hidden");
        feedbackCard.classList.add("hidden");
        resetFeedbackForm();

        try {
            const response = await fetch("/translate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    text: text,
                    source_lang: sourceLang,
                    target_lang: targetLang,
                    method: method
                })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || "Translation failed.");
            }

            const data = await response.json();
            
            // Render translated text
            targetTextDiv.textContent = data.translated_text;
            targetTextDiv.classList.remove("hidden");
            loadingSpinner.classList.add("hidden");
            copyBtn.disabled = false;

            // Cache translation for feedback
            currentTranslation = {
                source_text: text,
                target_text: data.translated_text,
                source_lang: sourceLang,
                target_lang: targetLang,
                method: method
            };

            // Show panels
            renderDetails(currentTranslation);
            feedbackCard.classList.remove("hidden");

        } catch (error) {
            loadingSpinner.classList.add("hidden");
            targetTextDiv.textContent = `Error: ${error.message}`;
            targetTextDiv.classList.remove("hidden");
        }
    }

    translateBtn.addEventListener("click", performTranslation);

    // Trigger translate on Ctrl+Enter
    sourceTextarea.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
            e.preventDefault();
            performTranslation();
        }
    });

    // 5. Render Translation details
    function renderDetails(translation) {
        alignmentInfo.innerHTML = "";
        detailsCard.classList.remove("hidden");

        const container = document.createElement("div");
        container.style.display = "flex";
        container.style.flexDirection = "column";
        container.style.gap = "12px";
        container.style.width = "100%";

        const methodInfo = document.createElement("p");
        methodInfo.innerHTML = `<strong>Translation System:</strong> Cross-lingual word embedding projection via <strong>${
            translation.method === "retrieval" ? "Global Sentence Retrieval" : "Word-by-word Dictionary Matching"
        }</strong>.`;
        container.appendChild(methodInfo);

        if (translation.method === "word-by-word") {
            const wordMappingTitle = document.createElement("p");
            wordMappingTitle.innerHTML = "<strong>Word alignments:</strong>";
            container.appendChild(wordMappingTitle);

            const chipContainer = document.createElement("div");
            chipContainer.className = "alignment-info";

            const srcWords = translation.source_text.replace(/[.,\/#!$%\^&\*;:{}=\-_`~()?]/g, "").toLowerCase().split(/\s+/).filter(w => w);
            const tgtWords = translation.target_text.split(/\s+/);

            srcWords.forEach((word, idx) => {
                const tgtWord = tgtWords[idx] || "...";
                const chip = document.createElement("div");
                chip.className = "alignment-chip";
                chip.innerHTML = `
                    <span class="src-word">${escapeHTML(word)}</span>
                    <span class="arrow"><i class="fa-solid fa-arrow-right-long"></i></span>
                    <span class="tgt-word">${escapeHTML(tgtWord)}</span>
                `;
                chipContainer.appendChild(chip);
            });
            container.appendChild(chipContainer);
        } else {
            const retrievalInfo = document.createElement("p");
            retrievalInfo.innerHTML = `<em>Retrieved parallel pair matching target representation coordinates in joint Kikuyu-English space.</em>`;
            container.appendChild(retrievalInfo);
        }

        alignmentInfo.appendChild(container);
    }

    // 6. Feedback Handler
    ratingButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            ratingButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            currentRating = parseInt(btn.getAttribute("data-rating"));
            feedbackDetails.classList.remove("hidden");
        });
    });

    submitFeedbackBtn.addEventListener("click", async () => {
        if (currentRating === null) return;
        
        const comment = feedbackComment.value.trim();
        
        try {
            submitFeedbackBtn.disabled = true;
            const response = await fetch("/feedback", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    source_text: currentTranslation.source_text,
                    target_text: currentTranslation.target_text,
                    source_lang: currentTranslation.source_lang,
                    target_lang: currentTranslation.target_lang,
                    method: currentTranslation.method,
                    rating: currentRating,
                    comment: comment ? comment : null
                })
            });

            if (!response.ok) {
                throw new Error("Could not submit feedback.");
            }

            // Success
            feedbackDetails.classList.add("hidden");
            ratingButtons.forEach(b => b.classList.add("hidden"));
            feedbackSuccessMsg.classList.remove("hidden");

        } catch (error) {
            alert(`Error: ${error.message}`);
            submitFeedbackBtn.disabled = false;
        }
    });

    function resetFeedbackForm() {
        currentRating = null;
        feedbackComment.value = "";
        submitFeedbackBtn.disabled = false;
        feedbackDetails.classList.add("hidden");
        feedbackSuccessMsg.classList.add("hidden");
        ratingButtons.forEach(b => {
            b.classList.remove("active");
            b.classList.remove("hidden");
        });
    }

    function escapeHTML(str) {
        return str.replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }
});
