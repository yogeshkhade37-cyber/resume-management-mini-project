/**
 * Main application JS
 */

function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:9999;display:flex;flex-direction:column;gap:10px;';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const bg = type === 'success' ? '#10b981' : type === 'danger' ? '#ef4444' : '#4f46e5';
    toast.style.cssText = `background:${bg};color:#fff;padding:12px 20px;border-radius:8px;font-size:13px;font-weight:600;box-shadow:0 10px 15px -3px rgba(0,0,0,0.1);display:flex;align-items:center;gap:10px;animation:slideIn 0.2s ease forwards;`;
    toast.textContent = message;

    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Job Activation Selector
function setActiveJob(jobId) {
    if (!jobId) return;
    fetch(`/api/jobs/${jobId}/activate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            showToast("Active Job updated!", "success");
            setTimeout(() => window.location.reload(), 600);
        } else {
            showToast("Failed to change active job", "danger");
        }
    })
    .catch(err => {
        console.error(err);
        showToast("Error updating active job", "danger");
    });
}

// Reset Database Confirmation
function resetDemoDatabase() {
    if (confirm("Are you sure you want to reset all jobs and candidates back to initial sample demo data?")) {
        fetch('/api/settings/reset-db', {
            method: 'POST'
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showToast("Sample data restored successfully!", "success");
                setTimeout(() => window.location.href = '/dashboard', 800);
            }
        })
        .catch(err => {
            showToast("Failed to reset database", "danger");
        });
    }
}
