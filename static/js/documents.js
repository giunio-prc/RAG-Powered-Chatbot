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
            this.fileUploadArea.classList.add('border-primary-500', 'bg-primary-50');
            this.fileUploadArea.classList.remove('border-gray-300');
        });

        this.fileUploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            if (!this.fileUploadArea.contains(e.relatedTarget)) {
                this.fileUploadArea.classList.remove('border-primary-500', 'bg-primary-50');
                this.fileUploadArea.classList.add('border-gray-300');
            }
        });

        this.fileUploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.fileUploadArea.classList.remove('border-primary-500', 'bg-primary-50');
            this.fileUploadArea.classList.add('border-gray-300');
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

                // Update status to show which file is being processed
                if (validFiles.length > 1) {
                    this.uploadStatus.innerHTML = `
                        <div class="text-sm text-gray-600 mb-2">
                            Processing file ${i + 1} of ${validFiles.length}: ${file.name}
                        </div>
                    `;
                }

                await this.uploadFile(file);
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

        // Handle streaming response
        if (response.body) {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            try {
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });

                    // Process complete lines from buffer
                    const lines = buffer.split('\n');
                    buffer = lines.pop() || ''; // Keep incomplete line in buffer

                    for (const line of lines) {
                        if (line.trim()) {
                            const progress = parseFloat(line.trim());
                            if (!isNaN(progress)) {
                                this.updateProgress(progress);
                            }
                        }
                    }
                }

                // Process any remaining data in buffer
                if (buffer.trim()) {
                    const progress = parseFloat(buffer.trim());
                    if (!isNaN(progress)) {
                        this.updateProgress(progress);
                    }
                }
            } finally {
                reader.releaseLock();
            }
        }

        return response;
    }

    showUploadProgress() {
        this.uploadProgress.classList.remove('hidden');
        this.uploadStatus.innerHTML = '';
        this.updateProgress(0);
    }

    hideUploadProgress() {
        setTimeout(() => {
            this.uploadProgress.classList.add('hidden');
        }, 1000);
    }

    updateProgress(percentage) {
        this.uploadBar.style.width = `${percentage}%`;
        this.uploadPercentage.textContent = `${Math.round(percentage)}%`;
    }

    showUploadSuccess(fileCount) {
        const message = fileCount === 1 ? 'File uploaded successfully!' : `${fileCount} files uploaded successfully!`;
        this.uploadStatus.innerHTML = `
            <div class="bg-green-50 border border-green-200 text-green-800 rounded-lg p-4 flex items-center">
                <svg class="w-5 h-5 mr-3 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                ${message}
            </div>
        `;
        toast.show(message, 'success');
    }

    showUploadError(error) {
        const message = `Upload failed: ${error.message}`;
        this.uploadStatus.innerHTML = `
            <div class="bg-red-50 border border-red-200 text-red-800 rounded-lg p-4 flex items-center">
                <svg class="w-5 h-5 mr-3 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
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
        activityElement.className = 'border-l-4 border-purple-500 bg-purple-50 pl-4 py-3 rounded-r-lg mb-3';
        activityElement.innerHTML = `
            <div class="flex justify-between items-center">
                <div class="flex items-center space-x-2">
                    <div class="w-2 h-2 bg-purple-500 rounded-full"></div>
                    <span class="text-sm text-gray-700 font-medium">${activity}</span>
                </div>
                <span class="text-xs text-gray-500">${this.formatTime(new Date())}</span>
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

    formatTime(date) {
        return date.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }
}

// Initialize document manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.documentManager = new DocumentManager();
});
