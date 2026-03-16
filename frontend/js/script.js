// Unified script for both index.html and dashboard.html
// Backend API: POST /upload to localhost:5000

const API_URL = 'http://localhost:5000/upload';

let chart = null;

// Drag & drop setup
function setupDragDrop(elementId) {
  const dropArea = document.getElementById(elementId || 'dropArea');
  if (!dropArea) return;

  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false);
  });

  ['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, highlight, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, unhighlight, false);
  });

  dropArea.addEventListener('drop', handleDrop, false);
}

// Common upload function
async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  showLoading(true);

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Analysis error:', error);
    throw error;
  } finally {
    showLoading(false);
  }
}

// Show/hide loading
function showLoading(show) {
  const loadingEls = document.querySelectorAll('.loading, #loading');
  loadingEls.forEach(el => {
    el.style.display = show ? 'block' : 'none';
  });
}

// Page-specific result display
function displayResults(data, isDashboard = false) {
  const { risk_level, risk_score, clauses_detected, summary, text } = data;

  if (!isDashboard) {
    // Index.html
    document.getElementById('result').innerHTML = `
      <div class="analysis-result">
        <h3>Risk Level: <span class="risk-badge ${risk_level.toLowerCase().replace(/ /g, '-')}">${risk_level}</span></h3>
        <p><strong>Score:</strong> ${risk_score}/10</p>
        <pre class="summary">${summary}</pre>
        <details>
          <summary>Full Text (${text.length} chars)</summary>
          <pre class="contract-box">${text.substring(0, 2000)}${text.length > 2000 ? '...' : ''}</pre>
        </details>
        <ul>
          ${Object.entries(clauses_detected).map(([key, val]) => 
            `<li class="clause ${val ? 'highlight' : ''}">${key.replace(/_/g, ' ').toUpperCase()}: ${val ? '✅ Detected' : '❌ Not Found'}</li>`
          ).join('')}
        </ul>
      </div>
    `;
  } else {
    // Dashboard
    document.getElementById('riskLevel').textContent = risk_level;
    document.getElementById('riskScore').textContent = `${risk_score}/10`;

    const clausesEl = document.getElementById('clauses');
    clausesEl.innerHTML = Object.entries(clauses_detected).map(([key, val]) => 
      `<li class="clause ${val ? 'highlight' : ''}">${key.replace(/_/g, ' ').toUpperCase()}: ${val ? 'Detected' : 'Not Found'}</li>`
    ).join('');

    document.getElementById('summary').textContent = summary;

    updateChart(risk_score);
  }

  addExportButton(data);
}

// Chart update
function updateChart(score) {
  const canvas = document.getElementById('riskChart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  if (chart) chart.destroy();

  const percent = Math.min((score / 10) * 100, 100);
  chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Risk Level', 'Safe Level'],
      datasets: [{ data: [percent, 100 - percent], backgroundColor: ['#ef4444', '#10b981'] }]
    },
    options: {
      responsive: true,
      plugins: { legend: { position: 'bottom', labels: { color: 'white' } } }
    }
  });
}

// Drag-drop utils
function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

function highlight(e) {
  e.currentTarget.classList.add('drag-highlight');
}

function unhighlight(e) {
  e.currentTarget.classList.remove('drag-highlight');
}

function handleDrop(e) {
  const files = e.dataTransfer.files;
  if (files.length > 0) handleFile(files[0]);
}

async function handleFile(file) {
  if (!file.name.match(/\.(pdf|docx)$/i)) {
    alert('Please use PDF or DOCX files.');
    return;
  }
  try {
    const data = await uploadFile(file);
    const isDash = !!document.querySelector('#fileInput');
    displayResults(data, isDash);
  } catch (err) {
    alert('Error: ' + err.message + '\nStart backend: python backend/app.py');
  }
}

// Export (extra)
function addExportButton(data) {
  if (document.getElementById('exportBtn')) return;
  const btn = document.createElement('button');
  btn.id = 'exportBtn';
  btn.textContent = '📥 Export JSON';
  btn.style.marginTop = '10px';
  btn.onclick = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analysis-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };
  (document.querySelector('.container') || document.getElementById('result') || document.body).appendChild(btn);
}

// Samples (extra)
function addSamples() {
  if (document.getElementById('samples')) return;
  const div = document.createElement('div');
  div.id = 'samples';
  div.innerHTML = `
    <h4 style="margin-top: 20px;">🧪 Test Samples:</h4>
    <button onclick="loadSample('../uploads/CHANDANA_LPWAN.pdf')">CHANDANA PDF</button>
    <button onclick="loadSample('../uploads/TEEGALA KRISHNA REDDY ENGINEERING COLLEGE (1)-1.pdf')">TEEGALA PDF</button>
  `;
  document.querySelector('.container, body').insertBefore(div, document.querySelector('.container, body').firstChild.nextSibling);
}

async function loadSample(path) {
  try {
    const res = await fetch(path);
    const blob = await res.blob();
    const file = new File([blob], path.split('/').pop(), { type: 'application/pdf' });
    handleFile(file);
  } catch (e) {
    alert('Sample error: ' + e.message);
  }
}

// Init
document.addEventListener('DOMContentLoaded', () => {
  addSamples();
  showLoading(false);

  // Index
  const indexFile = document.getElementById('contractFile');
  const indexBtn = document.getElementById('analyzeBtn');
  if (indexFile) {
    indexFile.onchange = (e) => handleFile(e.target.files[0]);
    if (indexBtn) indexBtn.onclick = () => handleFile(indexFile.files[0]);
    setupDragDrop('dropArea');
  }

  // Dashboard
  const dashFile = document.getElementById('fileInput');
  const dashBtn = document.querySelector('button');
  if (dashFile) {
    dashFile.onchange = (e) => handleFile(e.target.files[0]);
    if (dashBtn) dashBtn.onclick = () => handleFile(dashFile.files[0]);
    const card = document.querySelector('.card');
    if (card) setupDragDrop(); // Use first card as drop
  }
});
