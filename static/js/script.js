document.getElementById('currentYear').textContent = new Date().getUTCFullYear();

const fileInput = document.getElementById('fileInput');
const modeSelector = document.getElementById('modeSelector');
const rowSelector = document.getElementById('rowSelector');
const rowSelection = document.getElementById('rowSelection');
const resultArea = document.getElementById('resultArea');

fileInput.addEventListener('change', handleFileUpload);
modeSelector.addEventListener('change', resetForm);
rowSelector.addEventListener('change', processRowData);

function resetForm() {
    fileInput.value = '';
    rowSelection.style.display = 'none';
    resultArea.innerHTML = '⬇️​​ Results will appear here... ⬇️​';
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('mode', modeSelector.value);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        rowSelector.innerHTML = `<option value="">Choose a row</option>` + 
            data.rowOptions.map(row => 
                `<option value="${row.value}">${row.label}</option>`
            ).join('');
        rowSelection.style.display = 'block';
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error uploading file');
    });
}

function processRowData() {
    const selectedRow = rowSelector.value;
    if (!selectedRow) return;

    const formData = new FormData();
    formData.append('row', selectedRow);
    formData.append('mode', modeSelector.value);
    formData.append('filename', fileInput.files[0].name);

    fetch('/process_row', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        let resultHTML = '';
        for (const [key, value] of Object.entries(data)) {
            resultHTML += `
                <div class="result-section">
                    <h4>${key.charAt(0).toUpperCase() + key.slice(1)}</h4>
                    <div class="result-content">${value}</div>
                    <button class="copy-btn" onclick="copyToClipboard('${value}', this)">Copy ${key}</button>
                </div>
            `;
        }
        document.getElementById('resultArea').innerHTML = resultHTML;
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error processing row');
    });
}

function copyToClipboard(text, button) {
    navigator.clipboard.writeText(text).then(() => {
        button.style.backgroundColor = '#00ff00';
        setTimeout(() => {
            button.style.backgroundColor = '';
        }, 1000);
    }).catch(err => {
        console.error('Error in copying text: ', err);
    });
}