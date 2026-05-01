const sourceText = document.getElementById("source-text");
const summaryText = document.getElementById("summary-text");
const sourceStats = document.getElementById("source-stats");
const summaryStats = document.getElementById("summary-stats");
const summarizeBtn = document.getElementById("summarize-btn");
const clearBtn = document.getElementById("clear-btn");
const copyBtn = document.getElementById("copy-btn");
const whatsappBtn = document.getElementById("whatsapp-btn");
const saveBtn = document.getElementById("save-btn");
const themeBtn = document.getElementById("theme-btn");
const lengthInput = document.getElementById("summary-length");
const lengthControlRoot = document.getElementById("length-control-root");
const keywordList = document.getElementById("keyword-list");
const editorTools = document.querySelector(".editor-tools");
const foreColorBtn = document.getElementById("tool-fore-color-btn");
const foreColorInput = document.getElementById("tool-fore-color");
const hiliteColorBtn = document.getElementById("tool-hilite-color-btn");
const hiliteColorInput = document.getElementById("tool-hilite-color");
const blockquoteBtn = document.getElementById("tool-blockquote-btn");
const codeBtn = document.getElementById("tool-code-btn");
const linkBtn = document.getElementById("tool-link-btn");

let mode = "paragraph";
const selectedKeywords = new Set();

function getSourcePlainText() {
    if (!sourceText) {
        return "";
    }
    return sourceText.innerText || "";
}

function syncEmptyClass() {
    if (!sourceText) {
        return;
    }
    const text = (sourceText.innerText || "").trim();
    const hasMedia = Boolean(sourceText.querySelector("img"));
    sourceText.classList.toggle("is-empty", text.length === 0 && !hasMedia);
}

function getWordCount(text) {
    return text.trim() ? text.trim().split(/\s+/).length : 0;
}

function updateSourceStats() {
    sourceStats.innerHTML = `<i class="bi bi-chat-text"></i> ${getWordCount(getSourcePlainText())} words`;
}

function updateSummaryStats(words, sentences) {
    summaryStats.innerHTML = `<i class="bi bi-bar-chart"></i> ${sentences} sentences · ${words} words`;
}

function syncRangePercent() {
    if (!lengthInput || !lengthControlRoot) {
        return;
    }
    const min = Number(lengthInput.min);
    const max = Number(lengthInput.max);
    const val = Number(lengthInput.value);
    const pct = max > min ? ((val - min) / (max - min)) * 100 : 0;
    lengthControlRoot.style.setProperty("--range-pct", `${pct}%`);
}

function preventToolbarLoseSelection(e) {
    e.preventDefault();
}

function exec(cmd, value = null) {
    try {
        return document.execCommand(cmd, false, value);
    } catch {
        return false;
    }
}

function runAfterEdit() {
    syncEmptyClass();
    updateSourceStats();
}

function bindRichToolbar() {
    if (!editorTools || !sourceText) {
        return;
    }

    editorTools.querySelectorAll("button.tool-btn, button.tool-block").forEach((el) => {
        el.addEventListener("mousedown", preventToolbarLoseSelection);
    });

    editorTools.querySelectorAll("[data-cmd]").forEach((btn) => {
        btn.addEventListener("click", () => {
            sourceText.focus();
            exec(btn.dataset.cmd);
            runAfterEdit();
        });
    });

    editorTools.querySelectorAll("[data-block]").forEach((btn) => {
        btn.addEventListener("click", () => {
            sourceText.focus();
            const tag = btn.dataset.block === "p" ? "p" : btn.dataset.block;
            exec("formatBlock", tag);
            runAfterEdit();
        });
    });

    if (foreColorBtn && foreColorInput) {
        foreColorBtn.addEventListener("click", () => {
            sourceText.focus();
            foreColorInput.click();
        });
        foreColorInput.addEventListener("input", () => {
            sourceText.focus();
            exec("foreColor", foreColorInput.value);
            runAfterEdit();
        });
    }

    if (hiliteColorBtn && hiliteColorInput) {
        hiliteColorBtn.addEventListener("click", () => {
            sourceText.focus();
            hiliteColorInput.click();
        });
        hiliteColorInput.addEventListener("input", () => {
            sourceText.focus();
            document.execCommand("styleWithCSS", false, true);
            if (!exec("hiliteColor", hiliteColorInput.value)) {
                exec("backColor", hiliteColorInput.value);
            }
            runAfterEdit();
        });
    }

    if (blockquoteBtn) {
        blockquoteBtn.addEventListener("click", () => {
            sourceText.focus();
            exec("formatBlock", "blockquote");
            runAfterEdit();
        });
    }

    if (codeBtn) {
        codeBtn.addEventListener("click", () => {
            sourceText.focus();
            exec("formatBlock", "pre");
            runAfterEdit();
        });
    }

    if (linkBtn) {
        linkBtn.addEventListener("click", () => {
            sourceText.focus();
            const url = window.prompt("Link URL:", "https://");
            if (url && url.trim()) {
                exec("createLink", url.trim());
            }
            runAfterEdit();
        });
    }
}

function getCsrfToken() {
    return window.APP_CONFIG.csrfToken;
}

async function postJson(url, payload) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok || data.ok === false) {
        throw new Error("Request failed");
    }
    return data;
}

function renderKeywords(keywords) {
    const safe = Array.isArray(keywords) ? keywords : [];
    const active = new Set(selectedKeywords);
    keywordList.innerHTML = "";

    safe.forEach((keyword) => {
        const chip = document.createElement("button");
        chip.className = "keyword-chip";
        chip.type = "button";
        chip.textContent = keyword;
        if (active.has(keyword)) {
            chip.classList.add("active");
        }
        chip.addEventListener("click", () => {
            if (selectedKeywords.has(keyword)) {
                selectedKeywords.delete(keyword);
                chip.classList.remove("active");
            } else {
                selectedKeywords.add(keyword);
                chip.classList.add("active");
            }
        });
        keywordList.appendChild(chip);
    });
}

if (lengthInput) {
    lengthInput.addEventListener("input", syncRangePercent);
    syncRangePercent();
}

bindRichToolbar();

let keywordTimer = null;

if (sourceText) {
    sourceText.addEventListener("paste", (e) => {
        e.preventDefault();
        const text = e.clipboardData.getData("text/plain");
        document.execCommand("insertText", false, text);
        runAfterEdit();
    });

    sourceText.addEventListener("input", () => {
        syncEmptyClass();
        updateSourceStats();
        clearTimeout(keywordTimer);
        keywordTimer = setTimeout(async () => {
            const plain = getSourcePlainText();
            if (!plain.trim()) {
                selectedKeywords.clear();
                renderKeywords([]);
                return;
            }
            try {
                const data = await postJson(window.APP_CONFIG.keywordsUrl, { text: plain });
                const valid = new Set(data.keywords || []);
                [...selectedKeywords].forEach((item) => {
                    if (!valid.has(item)) {
                        selectedKeywords.delete(item);
                    }
                });
                renderKeywords(data.keywords);
            } catch (err) {
                console.error(err);
            }
        }, 300);
    });

    sourceText.addEventListener("keyup", () => {
        syncEmptyClass();
    });
}

document.querySelectorAll(".mode-btn").forEach((button) => {
    button.addEventListener("click", () => {
        document.querySelectorAll(".mode-btn").forEach((b) => b.classList.remove("active"));
        button.classList.add("active");
        mode = button.dataset.mode;
    });
});

summarizeBtn.addEventListener("click", async () => {
    const plain = getSourcePlainText();
    if (!plain.trim()) {
        return;
    }
    summarizeBtn.disabled = true;
    summarizeBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Summarizing';
    try {
        const data = await postJson(window.APP_CONFIG.summarizeUrl, {
            text: plain,
            mode,
            length_ratio: Number(lengthInput.value),
            keywords: [...selectedKeywords].join(","),
        });
        summaryText.value = data.summary || "";
        updateSummaryStats(data.stats.words, data.stats.sentences);
    } catch (err) {
        console.error(err);
        alert("Unable to summarize right now.");
    } finally {
        summarizeBtn.disabled = false;
        summarizeBtn.innerHTML = '<i class="bi bi-lightning-charge-fill"></i> Summarize';
    }
});

clearBtn.addEventListener("click", () => {
    if (sourceText) {
        sourceText.innerHTML = "";
        syncEmptyClass();
    }
    summaryText.value = "";
    selectedKeywords.clear();
    renderKeywords([]);
    updateSourceStats();
    updateSummaryStats(0, 0);
});

copyBtn.addEventListener("click", async () => {
    if (!summaryText.value.trim()) {
        return;
    }
    await navigator.clipboard.writeText(summaryText.value);
});

saveBtn.addEventListener("click", () => {
    const blob = new Blob([summaryText.value || ""], { type: "text/plain;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "summary.txt";
    link.click();
    URL.revokeObjectURL(link.href);
});

if (whatsappBtn) {
    whatsappBtn.addEventListener("click", () => {
        const raw = (summaryText.value || "").trim();
        if (!raw) {
            alert("Generate a summary first, then share it on WhatsApp.");
            return;
        }
        const header = "Free Text Summarizer\n\n";
        let text = header + raw;
        const maxLen = 2800;
        if (text.length > maxLen) {
            text = `${text.slice(0, maxLen - 40)}\n\n…(truncated — copy full text from the app if needed)`;
        }
        const url = `https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`;
        window.open(url, "_blank", "noopener,noreferrer");
    });
}

themeBtn.addEventListener("click", () => {
    document.body.classList.toggle("theme-dark");
    document.body.classList.toggle("theme-light");
});

syncEmptyClass();
updateSourceStats();
updateSummaryStats(0, 0);
