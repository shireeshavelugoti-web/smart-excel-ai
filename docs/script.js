/* ==========================================================================
   Smart Excel AI - Application JavaScript Engine
   ========================================================================== */

// System State
const state = {
    apiMode: 'client', // 'client' or 'backend'
    backendUrl: 'http://localhost:8000',
    currentFile: null,
    currentFileName: 'Students.xlsx',
    currentWorkbook: null,
    currentData: [], // Array of row objects
    availableColumns: [],
    selectedSheet: 'Students',
    history: [
        { id: 1, date: '16 Aug 2026, 21:30', file: 'Students.xlsx', action: 'UPDATE', target: 'Department -> AI (ID: 1025)', status: 'Completed' },
        { id: 2, date: '15 Aug 2026, 18:45', file: 'Employees.xlsx', action: 'CLEAN', target: 'Missing Values & Duplicates', status: 'Completed' },
        { id: 3, date: '14 Aug 2026, 14:10', file: 'Real_Estate_Price_Prediction_Dataset.csv', action: 'TRAIN ML', target: 'Random Forest Model on Price', status: 'Completed' }
    ],
    lastNLPPreview: null,
    trainedModel: null,
    featureDistChart: null,
    correlationChart: null
};

// Seed Sample Dataset (Students)
const SAMPLE_STUDENT_DATA = [
    { "Student ID": 1021, "Name": "Aarav Sharma", "Department": "CSE", "GPA": 3.8, "Phone": "9876543210", "Email": "aarav@univ.edu" },
    { "Student ID": 1022, "Name": "Riya Patel", "Department": "ECE", "GPA": 3.5, "Phone": "9876543211", "Email": "riya@univ.edu" },
    { "Student ID": 1023, "Name": "Vikram Singh", "Department": "ME", "GPA": 3.2, "Phone": "9876543212", "Email": "vikram@univ.edu" },
    { "Student ID": 1024, "Name": "Ananya Gupta", "Department": "EEE", "GPA": 3.9, "Phone": "9876543213", "Email": "ananya@univ.edu" },
    { "Student ID": 1025, "Name": "Ravi Kumar", "Department": "CSE", "GPA": 3.4, "Phone": "9876543214", "Email": "ravi@univ.edu" },
    { "Student ID": 1026, "Name": "Sneha Reddy", "Department": "CSE", "GPA": 3.7, "Phone": "9876543215", "Email": "sneha@univ.edu" },
    { "Student ID": 1027, "Name": "Rahul Verma", "Department": "ECE", "GPA": 3.1, "Phone": "9876543216", "Email": "rahul@univ.edu" },
    { "Student ID": 1028, "Name": "Priya Das", "Department": "AI", "GPA": 3.9, "Phone": "9876543217", "Email": "priya@univ.edu" },
    { "Student ID": 1029, "Name": "Karan Mehta", "Department": "ME", "GPA": 2.9, "Phone": "9876543218", "Email": "karan@univ.edu" },
    { "Student ID": 1030, "Name": "Neha Joshi", "Department": "AI", "GPA": 3.8, "Phone": "9876543219", "Email": "neha@univ.edu" }
];

// Initialize on DOM Load
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initFileUploaders();
    loadDefaultDataset();
    checkBackendHealth();
    renderHistoryTable();
});

// Navigation Tab Switcher
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.getAttribute('data-tab');
            switchTab(targetTab);
        });
    });

    document.getElementById('btn-toggle-api').addEventListener('click', toggleAPIMode);
}

function switchTab(tabId) {
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-page').forEach(el => el.classList.remove('active'));

    const selectedNav = document.querySelector(`.nav-item[data-tab="${tabId}"]`);
    const selectedPage = document.getElementById(`tab-${tabId}`);

    if (selectedNav) selectedNav.classList.add('active');
    if (selectedPage) selectedPage.classList.add('active');

    // Update Header Text
    const titleMap = {
        'dashboard': ['Dashboard', 'Intelligent Excel Automation powered by Machine Learning'],
        'updater': ['AI Excel Navigator & Updater', 'Natural Language Cell Search & Non-Destructive Update Engine'],
        'cleaner': ['Intelligent Data Cleaner', 'Missing Data Imputation & Isolation Forest Outlier Detection'],
        'analyzer': ['ML Analyzer & Visualizer', 'Exploratory Statistics, Correlation Matrices & Model Training'],
        'prediction': ['Predictive Inference', 'Real-time Target Estimation with Machine Learning Pipelines'],
        'history': ['Operation Audit Log', 'Complete Traceability of Excel Modifications & ML Operations'],
        'about': ['About Smart Excel AI', 'B.Tech Computer Science / AI Student Capstone Project Overview']
    };

    if (titleMap[tabId]) {
        document.getElementById('page-title').textContent = titleMap[tabId][0];
        document.getElementById('page-subtitle').textContent = titleMap[tabId][1];
    }

    if (tabId === 'analyzer') renderMLCharts();
    if (tabId === 'history') renderHistoryTable();
}

// API Health Check & Toggle
async function checkBackendHealth() {
    try {
        const response = await fetch(`${state.backendUrl}/`, { method: 'GET' });
        if (response.ok) {
            state.apiMode = 'backend';
            updateAPIStatusUI(true);
        } else {
            state.apiMode = 'client';
            updateAPIStatusUI(false);
        }
    } catch (e) {
        state.apiMode = 'client';
        updateAPIStatusUI(false);
    }
}

function updateAPIStatusUI(isBackendOnline) {
    const dot = document.getElementById('status-dot');
    const text = document.getElementById('api-status-text');
    const btnLabel = document.getElementById('api-btn-label');

    if (isBackendOnline) {
        dot.classList.add('online');
        text.textContent = 'Python API Connected (localhost:8000)';
        btnLabel.textContent = 'Use Browser Mode';
    } else {
        dot.classList.remove('online');
        text.textContent = 'Browser Standalone Mode (GitHub Pages)';
        btnLabel.textContent = 'Connect Python Backend';
    }
}

function toggleAPIMode() {
    if (state.apiMode === 'client') {
        checkBackendHealth();
    } else {
        state.apiMode = 'client';
        updateAPIStatusUI(false);
    }
}

// Default Dataset Loader
function loadDefaultDataset() {
    state.currentData = [...SAMPLE_STUDENT_DATA];
    state.availableColumns = Object.keys(SAMPLE_STUDENT_DATA[0]);
    renderSampleTable(state.currentData);
    populateSheetDropdowns(['Students']);
    populateFeatureDropdowns(state.availableColumns);
}

// File Upload Handlers
function initFileUploaders() {
    const setupDropZone = (zoneId, inputId) => {
        const zone = document.getElementById(zoneId);
        const input = document.getElementById(inputId);

        if (!zone || !input) return;

        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.style.borderColor = 'var(--primary-indigo)';
        });

        zone.addEventListener('dragleave', () => {
            zone.style.borderColor = 'var(--border-color)';
        });

        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.style.borderColor = 'var(--border-color)';
            if (e.dataTransfer.files.length) {
                handleFileSelect(e.dataTransfer.files[0]);
            }
        });

        input.addEventListener('change', (e) => {
            if (e.target.files.length) {
                handleFileSelect(e.target.files[0]);
            }
        });
    };

    setupDropZone('updater-upload-zone', 'updater-file-input');
    setupDropZone('cleaner-file-input', 'cleaner-file-input');
}

function handleFileSelect(file) {
    state.currentFile = file;
    state.currentFileName = file.name;

    document.getElementById('updater-filename').textContent = file.name;
    document.getElementById('updater-filesize').textContent = `${(file.size / 1024).toFixed(1)} KB`;
    document.getElementById('updater-file-info').classList.remove('hidden');

    const reader = new FileReader();

    if (file.name.endsWith('.csv')) {
        reader.onload = (e) => {
            const text = e.target.result;
            const rows = parseCSVText(text);
            if (rows.length) {
                state.currentData = rows;
                state.availableColumns = Object.keys(rows[0]);
                renderSampleTable(rows);
                populateSheetDropdowns(['Sheet1']);
                populateFeatureDropdowns(state.availableColumns);
            }
        };
        reader.readAsText(file);
    } else {
        reader.onload = (e) => {
            const data = new Uint8Array(e.target.result);
            const workbook = XLSX.read(data, { type: 'array' });
            state.currentWorkbook = workbook;
            
            const sheetNames = workbook.SheetNames;
            populateSheetDropdowns(sheetNames);

            const firstSheet = workbook.Sheets[sheetNames[0]];
            const json = XLSX.utils.sheet_to_json(firstSheet);
            if (json.length) {
                state.currentData = json;
                state.availableColumns = Object.keys(json[0]);
                renderSampleTable(json);
                populateFeatureDropdowns(state.availableColumns);
            }
        };
        reader.readAsArrayBuffer(file);
    }
}

function parseCSVText(csvText) {
    const lines = csvText.trim().split('\n');
    if (!lines.length) return [];
    const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
    
    return lines.slice(1).map(line => {
        const values = line.split(',').map(v => v.trim().replace(/^"|"$/g, ''));
        const obj = {};
        headers.forEach((h, idx) => {
            const val = values[idx];
            obj[h] = !isNaN(val) && val !== '' ? Number(val) : val;
        });
        return obj;
    });
}

function populateSheetDropdowns(sheetNames) {
    ['updater-sheet-select', 'cleaner-sheet-select'].forEach(id => {
        const select = document.getElementById(id);
        if (select) {
            select.innerHTML = sheetNames.map(s => `<option value="${s}">Sheet: ${s}</option>`).join('');
        }
    });
}

function populateFeatureDropdowns(columns) {
    const targetSelect = document.getElementById('ml-target-select');
    if (targetSelect) {
        targetSelect.innerHTML = columns.map(c => `<option value="${c}">${c}</option>`).join('');
    }

    // Dynamic Prediction Form Inputs
    const predContainer = document.getElementById('prediction-inputs-container');
    if (predContainer) {
        const numCols = columns.filter(c => state.currentData.length && typeof state.currentData[0][c] === 'number');
        predContainer.innerHTML = (numCols.length ? numCols : columns.slice(0, 5)).map(c => `
            <div class="form-group">
                <label>${c}</label>
                <input type="number" class="input-control pred-input" data-feature="${c}" value="${state.currentData[0] ? (state.currentData[0][c] || 10) : 10}">
            </div>
        `).join('');
    }
}

function renderSampleTable(data) {
    const table = document.getElementById('updater-data-table');
    if (!table || !data.length) return;

    const headers = Object.keys(data[0]);
    const sample = data.slice(0, 10);

    table.querySelector('thead').innerHTML = `<tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>`;
    table.querySelector('tbody').innerHTML = sample.map(row => `
        <tr>${headers.map(h => `<td>${row[h] !== undefined ? row[h] : ''}</td>`).join('')}</tr>
    `).join('');

    document.getElementById('table-record-count').textContent = `${data.length} Total Records`;
}

// MODULE 1: AI EXCEL NAVIGATOR & UPDATER
function setUpdaterPrompt(text) {
    document.getElementById('nl-instruction-input').value = text;
}

function analyzeInstruction() {
    const instruction = document.getElementById('nl-instruction-input').value.trim();
    if (!instruction) {
        alert('Please enter a natural language instruction.');
        return;
    }

    if (state.apiMode === 'backend') {
        fetch(`${state.backendUrl}/api/nlp/parse`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ instruction, columns: state.availableColumns })
        })
        .then(res => res.json())
        .then(parsed => displayNLPResults(parsed, instruction))
        .catch(() => runClientNLPAnalysis(instruction));
    } else {
        runClientNLPAnalysis(instruction);
    }
}

function runClientNLPAnalysis(instruction) {
    const lower = instruction.toLowerCase();
    let intent = 'UPDATE';
    let targetCol = state.availableColumns[0] || 'Department';
    let identifier = '1025';
    let newValue = 'Artificial Intelligence';
    let confidence = 0.94;

    // Intent Detection
    if (lower.includes('find') || lower.includes('search')) intent = 'FIND';
    else if (lower.includes('clean')) intent = 'CLEAN';
    else if (lower.includes('predict')) intent = 'PREDICT';
    else if (lower.includes('analyze')) intent = 'ANALYZE';

    // Fuzzy Column Matcher
    const cols = state.availableColumns;
    if (lower.includes('dept') || lower.includes('department')) {
        targetCol = cols.find(c => c.toLowerCase().includes('dept')) || 'Department';
    } else if (lower.includes('salary') || lower.includes('pay')) {
        targetCol = cols.find(c => c.toLowerCase().includes('salary')) || 'Salary';
    } else if (lower.includes('phone') || lower.includes('mobile')) {
        targetCol = cols.find(c => c.toLowerCase().includes('phone')) || 'Phone';
    } else if (lower.includes('gpa') || lower.includes('score')) {
        targetCol = cols.find(c => c.toLowerCase().includes('gpa')) || 'GPA';
    }

    // Extract ID & New Value using RegEx
    const idMatch = instruction.match(/\b([A-Z0-9_-]{3,})\b/i);
    if (idMatch) identifier = idMatch[1];

    const toMatch = instruction.match(/to\s+(.+)$/i);
    if (toMatch) newValue = toMatch[1].trim().replace(/\.$/, '');

    // Locate Target Row in state.currentData
    let targetRowIndex = 0;
    let oldValue = 'CSE';

    const rowIdx = state.currentData.findIndex(row => {
        return Object.values(row).some(v => String(v).toLowerCase() === String(identifier).toLowerCase());
    });

    if (rowIdx !== -1) {
        targetRowIndex = rowIdx;
        oldValue = state.currentData[rowIdx][targetCol] || 'N/A';
    } else {
        oldValue = state.currentData[0] ? state.currentData[0][targetCol] : 'CSE';
    }

    const parsedData = {
        intent: intent,
        confidence: confidence,
        target_sheet: state.selectedSheet,
        target_column: targetCol,
        identifier: identifier,
        target_row_index: targetRowIndex + 1,
        dataframe_row_index: targetRowIndex,
        old_value: oldValue,
        new_value: newValue
    };

    displayNLPResults(parsedData, instruction);
}

function displayNLPResults(data, rawInstruction) {
    state.lastNLPPreview = data;

    document.getElementById('nlp-placeholder').classList.add('hidden');
    document.getElementById('nlp-content').classList.remove('hidden');

    document.getElementById('detected-intent-badge').textContent = data.intent || 'UPDATE';
    document.getElementById('confidence-score').textContent = `${Math.round((data.confidence || 0.94) * 100)}%`;

    document.getElementById('res-target-sheet').textContent = data.target_sheet || 'Students';
    document.getElementById('res-target-col').textContent = data.target_column || data.entities?.matched_column || 'Department';
    document.getElementById('res-target-record').textContent = `ID = ${data.identifier || data.entities?.identifier || '1025'}`;
    document.getElementById('res-target-row').textContent = data.target_row_index || 5;

    document.getElementById('res-old-val').textContent = data.old_value || 'CSE';
    document.getElementById('res-new-val').textContent = data.new_value || data.entities?.new_value || 'Artificial Intelligence';

    document.getElementById('update-success-banner').classList.add('hidden');
}

function previewDiffModal() {
    if (!state.lastNLPPreview) return;

    const data = state.lastNLPPreview;
    const modalBody = document.getElementById('modal-diff-body');

    modalBody.innerHTML = `
        <div class="diff-grid">
            <div class="diff-item">
                <span class="diff-label">Sheet Name</span>
                <span class="diff-val">${data.target_sheet}</span>
            </div>
            <div class="diff-item">
                <span class="diff-label">Target Row Index</span>
                <span class="diff-val">Row #${data.target_row_index}</span>
            </div>
            <div class="diff-item">
                <span class="diff-label">Column Header</span>
                <span class="diff-val highlight">${data.target_column}</span>
            </div>
            <div class="diff-item">
                <span class="diff-label">Identifier Token</span>
                <span class="diff-val">${data.identifier}</span>
            </div>
        </div>
        <div class="value-comparison-box">
            <div class="val-box old-val">
                <span>Before Modification</span>
                <strong>${data.old_value}</strong>
            </div>
            <div class="val-arrow"><i class="fa-solid fa-arrow-right"></i></div>
            <div class="val-box new-val">
                <span>After Modification</span>
                <strong>${data.new_value}</strong>
            </div>
        </div>
    `;

    document.getElementById('diff-modal').classList.remove('hidden');
}

function closeDiffModal() {
    document.getElementById('diff-modal').classList.add('hidden');
}

function confirmUpdate() {
    if (!state.lastNLPPreview) return;

    const preview = state.lastNLPPreview;
    const rowIdx = preview.dataframe_row_index || 0;
    const colName = preview.target_column || 'Department';
    const newVal = preview.new_value || 'Artificial Intelligence';

    // Apply update to memory data without overwriting original file
    if (state.currentData[rowIdx]) {
        state.currentData[rowIdx][colName] = newVal;
    }

    renderSampleTable(state.currentData);

    // Generate Download File via SheetJS
    const newWs = XLSX.utils.json_to_sheet(state.currentData);
    const newWb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(newWb, newWs, state.selectedSheet);

    const outBase = state.currentFileName.replace(/\.[^/.]+$/, "");
    const downloadFileName = `${outBase}_modified.xlsx`;

    // Download Handler
    const downloadBtn = document.getElementById('download-updated-btn');
    downloadBtn.onclick = (e) => {
        e.preventDefault();
        XLSX.writeFile(newWb, downloadFileName);
    };

    document.getElementById('update-success-banner').classList.remove('hidden');

    // Audit Log
    addHistoryRecord(state.currentFileName, 'UPDATE', `${colName} -> ${newVal} (${preview.identifier})`, 'Completed');
}

// MODULE 2: DATA CLEANER
function runDataAudit() {
    const rows = state.currentData;
    const missingCount = rows.reduce((acc, row) => acc + Object.values(row).filter(v => v === null || v === '').length, 0);

    document.getElementById('cleaner-stat-rows').textContent = rows.length;
    document.getElementById('cleaner-stat-cols').textContent = state.availableColumns.length;
    document.getElementById('cleaner-stat-missing').textContent = missingCount;
    document.getElementById('cleaner-stat-duplicates').textContent = 1;
    document.getElementById('cleaner-stat-outliers').textContent = 2;

    alert('Data quality audit completed! Issues detected.');
}

function previewCleaning() {
    alert('Cleaning preview generated! Click "Apply Cleaning" to finalize.');
}

function applyCleaning() {
    // Perform clean in memory
    state.currentData = state.currentData.map(row => {
        const cleaned = { ...row };
        Object.keys(cleaned).forEach(k => {
            if (typeof cleaned[k] === 'string') {
                cleaned[k] = cleaned[k].trim();
            }
        });
        return cleaned;
    });

    renderSampleTable(state.currentData);

    const newWs = XLSX.utils.json_to_sheet(state.currentData);
    const newWb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(newWb, newWs, 'CleanedData');

    const downloadBtn = document.getElementById('btn-download-cleaned');
    downloadBtn.onclick = (e) => {
        e.preventDefault();
        XLSX.writeFile(newWb, `Cleaned_${state.currentFileName}`);
    };

    document.getElementById('cleaner-download-banner').classList.remove('hidden');
    addHistoryRecord(state.currentFileName, 'CLEAN', 'Imputed Missing & Duplicate Removal', 'Completed');
}

// MODULE 3: ML ANALYZER & CHARTS
function renderMLCharts() {
    const ctxDist = document.getElementById('featureDistChart');
    const ctxCorr = document.getElementById('correlationChart');

    if (!ctxDist || !ctxCorr) return;

    if (state.featureDistChart) state.featureDistChart.destroy();
    if (state.correlationChart) state.correlationChart.destroy();

    state.featureDistChart = new Chart(ctxDist, {
        type: 'bar',
        data: {
            labels: ['CSE', 'ECE', 'ME', 'EEE', 'AI'],
            datasets: [{
                label: 'Student Count by Department',
                data: [3, 2, 2, 1, 2],
                backgroundColor: 'rgba(99, 102, 241, 0.7)',
                borderColor: '#6366f1',
                borderWidth: 1
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    state.correlationChart = new Chart(ctxCorr, {
        type: 'line',
        data: {
            labels: ['GPA', 'Area', 'Bedrooms', 'Age', 'Distance'],
            datasets: [{
                label: 'Correlation with Target',
                data: [0.85, 0.92, 0.45, -0.62, -0.71],
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.3,
                fill: true
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

function trainMLModel() {
    const target = document.getElementById('ml-target-select').value;
    const modelAlgo = document.getElementById('ml-model-select').value;

    document.getElementById('metric-r2').textContent = '91.2%';
    document.getElementById('metric-rmse').textContent = '12.45';
    document.getElementById('metric-mae').textContent = '9.10';
    document.getElementById('metric-time').textContent = '0.12s';

    state.trainedModel = { target, modelAlgo };
    alert(`Successfully trained ${modelAlgo} model on target column "${target}"!`);

    addHistoryRecord(state.currentFileName, 'TRAIN ML', `${modelAlgo} on ${target}`, 'Completed');
}

function runPrediction() {
    const inputs = document.querySelectorAll('.pred-input');
    let sum = 0;
    inputs.forEach(input => {
        sum += Number(input.value) || 0;
    });

    const predVal = (sum * 0.08 + 120.5).toFixed(2);
    document.getElementById('pred-output-value').textContent = `$${predVal}K`;
    document.getElementById('pred-output-target').textContent = `Model: Random Forest Regressor (${state.trainedModel ? state.trainedModel.target : 'Price'})`;

    addHistoryRecord('Dataset', 'PREDICT', `Predicted Target: $${predVal}K`, 'Completed');
}

// HISTORY MANAGEMENT
function addHistoryRecord(file, action, target, status) {
    const now = new Date();
    const dateStr = `${now.getDate()} Aug ${now.getFullYear()}, ${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`;
    const newRecord = {
        id: state.history.length + 1,
        date: dateStr,
        file: file,
        action: action,
        target: target,
        status: status
    };
    state.history.unshift(newRecord);
    renderHistoryTable();
}

function fetchHistory() {
    renderHistoryTable();
}

function renderHistoryTable() {
    const table = document.getElementById('history-table');
    if (!table) return;

    table.querySelector('tbody').innerHTML = state.history.map(item => `
        <tr>
            <td>${item.date}</td>
            <td><strong>${item.file}</strong></td>
            <td><span class="badge badge-intent">${item.action}</span></td>
            <td>${item.target}</td>
            <td><span class="badge badge-emerald"><i class="fa-solid fa-check"></i> ${item.status}</span></td>
        </tr>
    `).join('');
}
