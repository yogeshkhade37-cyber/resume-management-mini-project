/**
 * Candidates Directory JS - Status updates, re-screening, and deletions
 */

function updateCandidateStatus(candidateId, newStatus) {
    fetch(`/api/candidates/${candidateId}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            showToast(`Status updated to "${newStatus}"`, 'success');
            setTimeout(() => window.location.reload(), 600);
        } else {
            showToast('Failed to update status', 'danger');
        }
    })
    .catch(err => {
        console.error(err);
        showToast('Error updating status', 'danger');
    });
}

function deleteCandidateRecord(candidateId, candidateName) {
    if (confirm(`Are you sure you want to delete "${candidateName}" and their screening results?`)) {
        fetch(`/api/candidates/${candidateId}/delete`, {
            method: 'POST'
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                showToast('Candidate deleted successfully', 'success');
                setTimeout(() => window.location.href = '/candidates', 600);
            } else {
                showToast('Failed to delete candidate', 'danger');
            }
        })
        .catch(err => {
            console.error(err);
            showToast('Error deleting candidate', 'danger');
        });
    }
}

function rescreenCandidate(candidateId, jobId) {
    if (!jobId) {
        alert("Please select a valid job to screen against.");
        return;
    }
    
    fetch(`/api/candidates/${candidateId}/rescreen`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_id: jobId })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            showToast('Candidate re-screened successfully!', 'success');
            setTimeout(() => window.location.href = `/candidates/${candidateId}?job_id=${jobId}`, 600);
        } else {
            showToast('Failed to re-screen candidate: ' + (data.error || ''), 'danger');
        }
    })
    .catch(err => {
        console.error(err);
        showToast('Error during re-screening', 'danger');
    });
}
