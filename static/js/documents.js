// Document management functionality

class DocumentManager {
    constructor() {
        this.fileUploadArea = document.getElementById('file-upload-area');
        this.fileInput = document.getElementById('file-input');
        this.browseButton = document.getElementById('browse-button');
        this.uploadProgress = document.getElementById('upload-progress');
        this.uploadBar = document.getElementById('upload-bar');
        this.uploadPercentage = document.getElementById('upload-percentage');
        this.uploadStatus = document.getElementById('upload-status');
        this.refreshStatsButton = document.getElementById('refresh-stats');
        this.vectorCountElement = document.getElementById('vector-count');
        this.longestVectorElement = document.getElementById('longest-vector');
        this.lastUpdatedElement = document.getElementById('last-updated');
        this.recentActivityElement = document.getElementById('recent-activity');

        this.initializeEventListeners();
        this.loadStatistics();
    }

    initializeEventListeners() {
        // File input change
        this.fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });

        // Browse button click
        this.browseButton.addEventListener('click', () => {
            this.fileInput.click();
        });

        // Drag and drop
        this.fileUploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.fileUploadArea.classList.add('dragover');
        });

        this.fileUploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            this.fileUploadArea.classList.remove('dragover');
        });

        this.fileUploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.fileUploadArea.classList.remove('dragover');
            this.handleFiles(e.dataTransfer.files);
        });

        // Refresh stats button
        this.refreshStatsButton.addEventListener('click', () => {
            this.loadStatistics();
        });
    }

    async handleFiles(files) {
        const validFiles = Array.from(files).filter(file => {
            if (file.type !== 'text/plain') {
                toast.show(`File "${file.name}" is not a text file and will be skipped`, 'warning');
                return false;
            }
            if (file.size > 10 * 1024 * 1024) { // 10MB limit
                toast.show(`File "${file.name}" is too large (max 10MB)`, 'warning');
                return false;
            }
            return true;
        });

        if (validFiles.length === 0) {
            toast.show('No valid files selected', 'warning');
            return;
        }

        this.showUploadProgress();

        try {
            for (let i = 0; i < validFiles.length; i++) {
                const file = validFiles[i];
                await this.uploadFile(file);

                // Update progress
                const progress = ((i + 1) / validFiles.length) * 100;
                this.updateProgress(progress);
            }

            this.showUploadSuccess(validFiles.length);
            this.loadStatistics(); // Refresh stats after upload
            this.addRecentActivity(`Uploaded ${validFiles.length} file(s)`);

        } catch (error) {
            this.showUploadError(error);
        } finally {
            this.hideUploadProgress();
        }
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/add-document', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Failed to upload ${file.name}`);
        }

        return response;
    }

    showUploadProgress() {
        this.uploadProgress.classList.remove('d-none');
        this.uploadStatus.innerHTML = '';
        this.updateProgress(0);
    }

    hideUploadProgress() {
        setTimeout(() => {
            this.uploadProgress.classList.add('d-none');
        }, 1000);
    }

    updateProgress(percentage) {
        this.uploadBar.style.width = `${percentage}%`;
        this.uploadPercentage.textContent = `${Math.round(percentage)}%`;
    }

    showUploadSuccess(fileCount) {
        const message = fileCount === 1 ? 'File uploaded successfully!' : `${fileCount} files uploaded successfully!`;
        this.uploadStatus.innerHTML = `
            <div class="alert alert-success">
                <i class="fas fa-check-circle mr-2"></i>
                ${message}
            </div>
        `;
        toast.show(message, 'success');
    }

    showUploadError(error) {
        const message = `Upload failed: ${error.message}`;
        this.uploadStatus.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle mr-2"></i>
                ${message}
            </div>
        `;
        toast.show(message, 'danger');
    }

    async loadStatistics() {
        utils.setLoading(this.refreshStatsButton, true);

        try {
            const response = await api.get('/get-vectors-data');
            const data = await response.json();

            this.vectorCountElement.textContent = utils.formatNumber(data.number_of_vectors);
            this.longestVectorElement.textContent = utils.formatNumber(data.longest_vector);
            this.lastUpdatedElement.textContent = utils.formatDate(new Date());

            toast.show('Statistics updated successfully', 'success');

        } catch (error) {
            handleError(error, 'Failed to load statistics');
            this.vectorCountElement.textContent = 'Error';
            this.longestVectorElement.textContent = 'Error';
        } finally {
            utils.setLoading(this.refreshStatsButton, false);
        }
    }

    addRecentActivity(activity) {
        const activityElement = document.createElement('div');
        activityElement.className = 'border-l-4 border-blue-500 pl-3 py-2';
        activityElement.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <span class="text-sm text-gray-700">${activity}</span>
                <span class="text-xs text-gray-500">${utils.formatDate(new Date())}</span>
            </div>
        `;

        // Clear "no activity" message if present
        const noActivity = this.recentActivityElement.querySelector('.text-center');
        if (noActivity) {
            noActivity.remove();
        }

        // Add new activity at the top
        this.recentActivityElement.insertBefore(activityElement, this.recentActivityElement.firstChild);

        // Keep only last 5 activities
        const activities = this.recentActivityElement.querySelectorAll('.border-l-4');
        if (activities.length > 5) {
            activities[activities.length - 1].remove();
        }
    }
}

// Initialize document manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.documentManager = new DocumentManager();
});
