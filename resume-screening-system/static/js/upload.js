/**
 * Upload Page JS - Drag & Drop, File Validation, AJAX Processing
 */

document.addEventListener('DOMContentLoaded', () => {
    const dropzone = document.getElementById('uploadDropzone');
    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('filePreviewList');
    const uploadBtn = document.getElementById('startUploadBtn');
    const progressContainer = document.getElementById('uploadProgressContainer');
    const resultsContainer = document.getElementById('uploadResultsContainer');
    const resultsList = document.getElementById('resultsList');

    let selectedFiles = [];

    if (!dropzone || !fileInput) return;

    // Trigger file browser on click
    dropzone.addEventListener('click', (e) => {
        if (e.target.tagName !== 'BUTTON' && e.target.tagName !== 'INPUT') {
            fileInput.click();
        }
    });

    // Drag & Drop event listeners
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');
        });
    });

    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        if (dt && dt.files.length > 0) {
            handleFiles(dt.files);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (fileInput.files.length > 0) {
            handleFiles(fileInput.files);
        }
    });

    function handleFiles(files) {
        const allowedExtensions = ['pdf', 'docx', 'doc', 'txt'];
        const maxSizeBytes = 10 * 1024 * 1024; // 10 MB

        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const ext = file.name.split('.').pop().toLowerCase();

            if (!allowedExtensions.includes(ext)) {
                alert(`File "${file.name}" is not supported. Please upload PDF, DOCX, or TXT.`);
                continue;
            }

            if (file.size > maxSizeBytes) {
                alert(`File "${file.name}" exceeds the 10MB size limit.`);
                continue;
            }

            // Check if already in list
            if (!selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
                selectedFiles.push(file);
            }
        }

        renderFileList();
    }

    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / 1048576).toFixed(1) + ' MB';
    }

    function renderFileList() {
        fileList.innerHTML = '';
        if (selectedFiles.length === 0) {
            uploadBtn.style.display = 'none';
            return;
        }

        uploadBtn.style.display = 'inline-flex';
        uploadBtn.textContent = `Screen & Process ${selectedFiles.length} Resume${selectedFiles.length > 1 ? 's' : ''}`;

        selectedFiles.forEach((file, index) => {
            const item = document.createElement('div');
            item.className = 'file-item';
            item.innerHTML = `
                <div class="file-info">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                    <div>
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${formatFileSize(file.size)}</div>
                    </div>
                </div>
                <button type="button" class="btn btn-sm btn-secondary" style="color:#ef4444;" onclick="removeFile(${index})">✕ Remove</button>
            `;
            fileList.appendChild(item);
        });
    }

    window.removeFile = function(index) {
        selectedFiles.splice(index, 1);
        renderFileList();
    };

    // Upload & Screening Action
    uploadBtn.addEventListener('click', () => {
        if (selectedFiles.length === 0) return;

        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('resumes', file);
        });

        uploadBtn.disabled = true;
        uploadBtn.textContent = 'Processing & Screening...';
        progressContainer.style.display = 'block';
        resultsContainer.style.display = 'none';

        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            progressContainer.style.display = 'none';
            uploadBtn.disabled = false;
            uploadBtn.textContent = 'Upload Completed';

            if (data.success) {
                selectedFiles = [];
                renderFileList();
                showResults(data.results);
            } else {
                alert('Upload Error: ' + (data.error || 'Unknown error occurred.'));
            }
        })
        .catch(err => {
            progressContainer.style.display = 'none';
            uploadBtn.disabled = false;
            console.error(err);
            alert('An error occurred during upload. Please check your backend connection.');
        });
    });

    function showResults(results) {
        resultsContainer.style.display = 'block';
        resultsList.innerHTML = '';

        results.forEach(res => {
            const card = document.createElement('div');
            card.className = 'card';
            card.style.marginBottom = '12px';

            if (res.error) {
                card.innerHTML = `
                    <div class="card-body" style="padding:16px;display:flex;align-items:center;justify-content:space-between;">
                        <div>
                            <strong style="color:#ef4444;">${res.filename}</strong>
                            <div style="font-size:12px;color:#64748b;">${res.error}</div>
                        </div>
                        <span class="badge badge-low">Failed</span>
                    </div>
                `;
            } else {
                const tierClass = res.score >= 80 ? 'badge-strong' : (res.score >= 60 ? 'badge-moderate' : 'badge-low');
                card.innerHTML = `
                    <div class="card-body" style="padding:16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
                        <div>
                            <h4 style="font-size:15px;font-weight:700;margin-bottom:2px;">${res.name}</h4>
                            <div style="font-size:12px;color:#64748b;">
                                File: ${res.filename} • Extracted Skills: ${res.skills_count} • Matched: ${res.matched_count} • Missing: ${res.missing_count}
                            </div>
                        </div>
                        <div style="display:flex;align-items:center;gap:16px;">
                            <div style="text-align:right;">
                                <div style="font-size:20px;font-weight:800;color:#0f172a;">${res.score}%</div>
                                <span class="badge ${tierClass}">${res.recommendation}</span>
                            </div>
                            <a href="/candidates/${res.candidate_id}" class="btn btn-primary btn-sm">View Profile →</a>
                        </div>
                    </div>
                `;
            }

            resultsList.appendChild(card);
        });

        // Scroll into view
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }
});
