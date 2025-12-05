document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const analyzeBtn = document.getElementById('analyze-btn');
    const languageSelect = document.getElementById('language-select');
    const resultSection = document.getElementById('result-section');
    const resultContent = document.getElementById('result-content');

    let selectedFile = null;

    // Drag & Drop Handlers
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });

    function handleFile(file) {
        selectedFile = file;
        const p = dropZone.querySelector('p');
        p.textContent = `Selected: ${file.name}`;
        analyzeBtn.disabled = false;
    }

    const terminalSection = document.getElementById('terminal-section');
    const terminalLogs = document.getElementById('terminal-logs');

    // Stats Animation
    const stats = document.querySelectorAll('.stat-number');
    stats.forEach(stat => {
        const target = +stat.getAttribute('data-target');
        const increment = target / 200;

        const updateCount = () => {
            const count = +stat.innerText;
            if (count < target) {
                stat.innerText = Math.ceil(count + increment);
                setTimeout(updateCount, 10);
            } else {
                stat.innerText = target;
            }
        };
        updateCount();
    });

    // Fake Logging System
    const logMessages = [
        "Initializing neural network parameters...",
        "Loading Llama 4 Scout model (17B parameters)...",
        "Allocating GPU tensors...",
        "Preprocessing image data...",
        "Vectorizing input stream...",
        "Performing optical character recognition (OCR)...",
        "Detecting handwriting patterns...",
        "Translating context to target language...",
        "Synthesizing summary...",
        "Finalizing output..."
    ];

    async function runTerminalLogs() {
        terminalLogs.innerHTML = '';
        terminalSection.classList.remove('hidden');

        for (const msg of logMessages) {
            const div = document.createElement('div');
            div.className = 'log-line';
            div.textContent = `> ${msg}`;
            terminalLogs.appendChild(div);
            terminalLogs.scrollTop = terminalLogs.scrollHeight;
            await new Promise(r => setTimeout(r, 400)); // Delay between logs
        }
    }

    analyzeBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        analyzeBtn.classList.add('loading');
        analyzeBtn.disabled = true;
        resultSection.classList.add('hidden');

        // Start fake logs
        runTerminalLogs();

        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('language', languageSelect.value);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                // Parse Markdown
                resultContent.innerHTML = marked.parse(data.result);
                resultSection.classList.remove('hidden');
                terminalSection.classList.add('hidden'); // Hide terminal on success
            } else {
                alert(`Error: ${data.error}`);
                terminalSection.classList.add('hidden');
            }
        } catch (error) {
            alert('An error occurred while processing the request.');
            console.error(error);
            terminalSection.classList.add('hidden');
        } finally {
            analyzeBtn.classList.remove('loading');
            analyzeBtn.disabled = false;
        }
    });
});
