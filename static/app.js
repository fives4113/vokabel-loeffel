// --- State ---
let currentWords = [];
let currentSource = '';

// --- DOM ---
const $ = (id) => document.getElementById(id);
const tabBtns = document.querySelectorAll('.tab');
const tabContents = document.querySelectorAll('.tab-content');

const promptInput = $('prompt');
const countInput = $('count');
const countRange = $('count-range');
const btnGenerate = $('btn-generate');

const fileUpload = $('file-upload');
const uploadArea = $('upload-area');
const fileNameDisplay = $('file-name');
const btnExtract = $('btn-extract');

const loading = $('loading');
const loadingText = $('loading-text');

const results = $('results');
const vocabBody = $('vocab-body');
const statsTotal = $('stats-total');
const statsDupes = $('stats-dupes');
const selectAll = $('select-all');

const btnExport = $('btn-export');
const btnExportApkg = $('btn-export-apkg');
const exportCount = $('export-count');

const libraryBody = $('library-body');
const libraryCount = $('library-count');
const libraryCountHero = $('library-count-hero');
const libraryEmpty = $('library-empty');
const libraryTableWrapper = $('library-table-wrapper');
const btnClearLibrary = $('btn-clear-library');

const toastContainer = $('toast-container');

// --- Utils ---
function esc(text) {
    const div = document.createElement('div');
    div.textContent = text ?? '';
    return div.innerHTML;
}

function toast(message, type = 'info', timeout = 3500) {
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    const icon = type === 'error' ? 'i-alert' : type === 'success' ? 'i-check' : 'i-sparkle';
    el.innerHTML = `<svg><use href="#${icon}"/></svg><span>${esc(message)}</span>`;
    toastContainer.appendChild(el);
    setTimeout(() => {
        el.classList.add('leaving');
        el.addEventListener('animationend', () => el.remove(), { once: true });
    }, timeout);
}

async function apiFetch(url, options = {}) {
    const res = await fetch(url, options);
    if (!res.ok) {
        let msg = `HTTP ${res.status}`;
        try {
            const body = await res.json();
            msg = body.detail || body.message || msg;
        } catch { /* keep default */ }
        throw new Error(msg);
    }
    return res;
}

function buildFilename(source, ext = 'txt') {
    const slug = (source || '')
        .toLowerCase()
        .normalize('NFKD')
        .replace(/[\u0300-\u036f]/g, '')
        .replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ß/g, 'ss')
        .replace(/[^a-z0-9]+/g, '_')
        .replace(/^_+|_+$/g, '')
        .slice(0, 60);
    const date = new Date().toISOString().slice(0, 10);
    const base = slug || 'russisch_vokabeln';
    return `${base}_${date}.${ext}`;
}

function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

// --- Tabs ---
tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        tabBtns.forEach(b => b.classList.remove('active'));
        tabContents.forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
        $(`tab-${btn.dataset.tab}`).classList.add('active');
        if (btn.dataset.tab === 'library') loadLibrary();
    });
});

// --- Range/Number sync ---
countRange.addEventListener('input', () => { countInput.value = countRange.value; });
countInput.addEventListener('input', () => {
    const v = parseInt(countInput.value) || 0;
    if (v >= Number(countRange.min) && v <= Number(countRange.max)) countRange.value = v;
});

// --- Upload ---
uploadArea.addEventListener('click', () => fileUpload.click());
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});
uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));
uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
        fileUpload.files = e.dataTransfer.files;
        handleFileSelect();
    }
});
fileUpload.addEventListener('change', handleFileSelect);

function handleFileSelect() {
    if (fileUpload.files.length > 0) {
        fileNameDisplay.textContent = `Ausgewählt: ${fileUpload.files[0].name}`;
        btnExtract.disabled = false;
    }
}

// --- Generate ---
btnGenerate.addEventListener('click', async () => {
    const prompt = promptInput.value.trim();
    if (!prompt) {
        toast('Bitte gib eine Beschreibung ein.', 'error');
        return;
    }
    showLoading('Vokabeln werden generiert…');
    try {
        const res = await apiFetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, count: parseInt(countInput.value) || 30 }),
        });
        const data = await res.json();
        currentSource = prompt;
        showResults(data);
    } catch (error) {
        toast(error.message, 'error', 5000);
    } finally {
        hideLoading();
    }
});

// --- Extract ---
btnExtract.addEventListener('click', async () => {
    if (fileUpload.files.length === 0) return;
    showLoading('Dokument wird analysiert…');
    const formData = new FormData();
    formData.append('file', fileUpload.files[0]);
    try {
        const res = await apiFetch('/api/extract', { method: 'POST', body: formData });
        const data = await res.json();
        currentSource = fileUpload.files[0].name.replace(/\.[^.]+$/, '');
        showResults(data);
    } catch (error) {
        toast(error.message, 'error', 5000);
    } finally {
        hideLoading();
    }
});

// --- Results ---
function showResults(data) {
    currentWords = data.words;
    statsTotal.textContent = `${data.total_generated} generiert`;
    statsTotal.classList.remove('hidden');
    if (data.duplicates_removed > 0) {
        statsDupes.textContent = `${data.duplicates_removed} Duplikate entfernt`;
        statsDupes.classList.remove('hidden');
    } else {
        statsDupes.classList.add('hidden');
    }

    vocabBody.innerHTML = '';
    currentWords.forEach((word, i) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><input type="checkbox" data-index="${i}" checked></td>
            <td class="ru">${esc(word.russian)}</td>
            <td>${esc(word.transliteration)}</td>
            <td class="de">${esc(word.german)}</td>
            <td class="en">${esc(word.english || '')}</td>
            <td>${esc(word.word_type)}</td>
            <td>${esc(word.example_ru)}</td>
            <td>${esc(word.example_de)}</td>
            <td>${word.level ? `<span class="level-badge">${esc(word.level)}</span>` : ''}</td>
            <td>${esc(word.tags)}</td>
        `;
        vocabBody.appendChild(tr);
    });

    updateExportCount();
    results.classList.remove('hidden');
    selectAll.checked = true;
    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// --- Selection ---
selectAll.addEventListener('change', () => {
    document.querySelectorAll('#vocab-body input[type="checkbox"]').forEach(cb => {
        cb.checked = selectAll.checked;
    });
    updateExportCount();
});

vocabBody.addEventListener('change', (e) => {
    if (e.target.type === 'checkbox') updateExportCount();
});

function updateExportCount() {
    const checked = document.querySelectorAll('#vocab-body input[type="checkbox"]:checked').length;
    exportCount.textContent = `${checked} von ${currentWords.length} ausgewählt`;
    btnExport.disabled = checked === 0;
    btnExportApkg.disabled = checked === 0;
}

function getSelectedWords() {
    const selected = [];
    document.querySelectorAll('#vocab-body input[type="checkbox"]:checked').forEach(cb => {
        selected.push(currentWords[parseInt(cb.dataset.index)]);
    });
    return selected;
}

// --- Exports ---
btnExport.addEventListener('click', async () => {
    const words = getSelectedWords();
    if (words.length === 0) return;
    try {
        const res = await apiFetch('/api/export', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(words),
        });
        downloadBlob(await res.blob(), buildFilename(currentSource, 'txt'));
        toast(`${words.length} Vokabeln als TSV exportiert`, 'success');
        loadLibraryCount();
    } catch (error) {
        toast(error.message, 'error', 5000);
    }
});

btnExportApkg.addEventListener('click', async () => {
    const words = getSelectedWords();
    if (words.length === 0) return;
    try {
        const res = await apiFetch('/api/export-apkg', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                words,
                deck_name: currentSource ? `Russisch: ${currentSource}`.slice(0, 80) : 'Russisch Vokabeln',
            }),
        });
        downloadBlob(await res.blob(), buildFilename(currentSource, 'apkg'));
        toast(`${words.length} Vokabeln als Anki-Paket exportiert`, 'success');
        loadLibraryCount();
    } catch (error) {
        toast(error.message, 'error', 5000);
    }
});

// --- Library ---
async function loadLibrary() {
    try {
        const res = await apiFetch('/api/history');
        const data = await res.json();
        renderLibrary(data.words);
        setLibraryCount(data.count);
    } catch (error) {
        toast(error.message, 'error');
    }
}

function renderLibrary(words) {
    libraryBody.innerHTML = '';
    if (words.length === 0) {
        libraryEmpty.classList.remove('hidden');
        libraryTableWrapper.classList.add('hidden');
        return;
    }
    libraryEmpty.classList.add('hidden');
    libraryTableWrapper.classList.remove('hidden');
    const frag = document.createDocumentFragment();
    words.forEach(word => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="ru">${esc(word.russian)}</td>
            <td>${esc(word.transliteration)}</td>
            <td class="de">${esc(word.german)}</td>
            <td class="en">${esc(word.english || '')}</td>
            <td>${esc(word.word_type)}</td>
            <td>${esc(word.example_ru)}</td>
            <td>${esc(word.example_de)}</td>
            <td>${word.level ? `<span class="level-badge">${esc(word.level)}</span>` : ''}</td>
            <td>${esc(word.tags)}</td>
        `;
        frag.appendChild(tr);
    });
    libraryBody.appendChild(frag);
}

btnClearLibrary.addEventListener('click', async () => {
    if (!confirm('Wirklich alle gespeicherten Vokabeln löschen? Danach werden bereits exportierte Vokabeln nicht mehr als Duplikate erkannt.')) return;
    try {
        await apiFetch('/api/reset', { method: 'POST' });
        loadLibrary();
        toast('Bibliothek geleert', 'success');
    } catch (error) {
        toast(error.message, 'error');
    }
});

async function loadLibraryCount() {
    try {
        const res = await apiFetch('/api/stats');
        const data = await res.json();
        setLibraryCount(data.exported_count);
    } catch { /* ignore */ }
}

function setLibraryCount(n) {
    libraryCount.textContent = n;
    libraryCountHero.textContent = n;
}

// --- Loading ---
function showLoading(text) {
    loadingText.textContent = text;
    loading.classList.remove('hidden');
    results.classList.add('hidden');
    btnGenerate.disabled = true;
    btnExtract.disabled = true;
}

function hideLoading() {
    loading.classList.add('hidden');
    btnGenerate.disabled = false;
    btnExtract.disabled = fileUpload.files.length === 0;
}

// --- Init ---
loadLibraryCount();
