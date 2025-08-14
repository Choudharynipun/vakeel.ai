// Vakeel.ai Main Application Class
class VakeelAI {
    constructor() {
        this.uploadedDocuments = [];
        this.isProcessing = false;
        this.systemHealth = 'unknown';
        this.startTime = Date.now();
        this.init();
    }

    // Initialize Application
    init() {
        this.setupEventListeners();
        this.setupFileUpload();
        this.setupNavigation();
        this.animateOnLoad();
        this.startSystemMonitoring();
        this.initializeChat();
        
        console.log('🚀 Vakeel.ai initialized successfully');
    }

    // Event Listeners Setup
    setupEventListeners() {
        // Chat functionality
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendButton');
        const clearSessionBtn = document.getElementById('clearSessionBtn');

        if (chatInput) {
            chatInput.addEventListener('input', (e) => {
                this.updateSendButton();
                this.handleTyping();
            });

            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        if (sendButton) {
            sendButton.addEventListener('click', () => this.sendMessage());
        }

        if (clearSessionBtn) {
            clearSessionBtn.addEventListener('click', () => this.clearSession());
        }

        // Window events
        window.addEventListener('scroll', () => this.handleScroll());
        window.addEventListener('resize', () => this.handleResize());
        
        // Add AOS (Animate On Scroll) effect
        this.setupScrollAnimations();
    }

    // File Upload Setup
    setupFileUpload() {
        const fileInput = document.getElementById('fileInput');
        const fileDropZone = document.getElementById('fileDropZone');
        const browseBtn = document.getElementById('browseBtn');

        if (fileInput && fileDropZone) {
            // File input change
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.handleFileSelect(e.target.files[0]);
                }
            });

            // Browse button
            if (browseBtn) {
                browseBtn.addEventListener('click', () => fileInput.click());
            }

            // Drag and drop events
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                fileDropZone.addEventListener(eventName, this.preventDefaults, false);
                document.body.addEventListener(eventName, this.preventDefaults, false);
            });

            ['dragenter', 'dragover'].forEach(eventName => {
                fileDropZone.addEventListener(eventName, () => {
                    fileDropZone.classList.add('dragover');
                }, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                fileDropZone.addEventListener(eventName, () => {
                    fileDropZone.classList.remove('dragover');
                }, false);
            });

            fileDropZone.addEventListener('drop', (e) => {
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.handleFileSelect(files[0]);
                }
            }, false);
        }
    }

    // Navigation Setup
    setupNavigation() {
        const navToggle = document.getElementById('navToggle');
        const navMenu = document.getElementById('navMenu');
        const navLinks = document.querySelectorAll('.nav-link');

        if (navToggle && navMenu) {
            navToggle.addEventListener('click', () => {
                navToggle.classList.toggle('active');
                navMenu.classList.toggle('active');
            });
        }

        // Smooth scrolling for nav links
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');
                if (href.startsWith('#')) {
                    e.preventDefault();
                    this.scrollToSection(href.substring(1));
                    
                    // Close mobile menu
                    if (navToggle && navMenu) {
                        navToggle.classList.remove('active');
                        navMenu.classList.remove('active');
                    }
                }
            });
        });

        // Update active nav link on scroll
        this.updateActiveNavLink();
    }

    // Smooth scroll to section
    scrollToSection(sectionId) {
        const element = document.getElementById(sectionId);
        if (element) {
            const headerHeight = document.querySelector('.navbar').offsetHeight;
            const elementPosition = element.offsetTop - headerHeight - 20;
            
            window.scrollTo({
                top: elementPosition,
                behavior: 'smooth'
            });
        }
    }

    // Handle scroll events
    handleScroll() {
        this.updateNavbarBackground();
        this.updateActiveNavLink();
        this.animateStatsOnScroll();
    }

    // Update navbar background on scroll
    updateNavbarBackground() {
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            if (window.scrollY > 50) {
                navbar.style.background = 'rgba(10, 10, 15, 0.95)';
                navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.3)';
            } else {
                navbar.style.background = 'rgba(10, 10, 15, 0.8)';
                navbar.style.boxShadow = 'none';
            }
        }
    }

    // Update active navigation link
    updateActiveNavLink() {
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.nav-link');
        
        let current = '';
        const scrollPosition = window.scrollY + 200;

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    }

    // Animate stats numbers on scroll
    animateStatsOnScroll() {
        const statNumbers = document.querySelectorAll('.stat-number');
        
        statNumbers.forEach(stat => {
            if (this.isElementInViewport(stat) && !stat.classList.contains('animated')) {
                stat.classList.add('animated');
                this.animateNumber(stat, parseInt(stat.getAttribute('data-target')));
            }
        });
    }

    // Check if element is in viewport
    isElementInViewport(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }

    // Animate number counting
    animateNumber(element, target) {
        let start = 0;
        const increment = target / 50;
        const timer = setInterval(() => {
            start += increment;
            if (start >= target) {
                element.textContent = target;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(start);
            }
        }, 30);
    }

    // Setup scroll animations
    setupScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);

        // Observe elements with animation
        const animatedElements = document.querySelectorAll('[data-aos]');
        animatedElements.forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'all 0.6s ease';
            observer.observe(el);
        });
    }

    // Animate elements on page load
    animateOnLoad() {
        // Typewriter effect for hero subtitle
        this.typewriterEffect();
        
        // Animate hero elements
        setTimeout(() => {
            const heroElements = document.querySelectorAll('.hero-title, .hero-buttons');
            heroElements.forEach((el, index) => {
                setTimeout(() => {
                    el.style.opacity = '1';
                    el.style.transform = 'translateY(0)';
                }, index * 300);
            });
        }, 500);
    }

    // Typewriter effect
    typewriterEffect() {
        const subtitle = document.querySelector('.hero-subtitle');
        if (subtitle && subtitle.classList.contains('typewriter')) {
            const text = subtitle.textContent;
            subtitle.textContent = '';
            subtitle.style.width = '0';
            
            let i = 0;
            const timer = setInterval(() => {
                if (i < text.length) {
                    subtitle.textContent += text.charAt(i);
                    i++;
                } else {
                    clearInterval(timer);
                    subtitle.style.borderRight = 'none';
                }
            }, 50);
        }
    }

    // System monitoring
    startSystemMonitoring() {
        this.checkSystemHealth();
        
        // Check health every 30 seconds
        setInterval(() => {
            this.checkSystemHealth();
        }, 30000);

        // Update uptime every second
        setInterval(() => {
            this.updateSystemUptime();
        }, 1000);
    }

    // Check system health
    async checkSystemHealth() {
        try {
            const response = await fetch('/api/health');
            const health = await response.json();
            
            this.systemHealth = health.status;
            this.updateSystemStatus(health);
            
        } catch (error) {
            console.error('Health check failed:', error);
            this.systemHealth = 'unhealthy';
            this.updateSystemStatus({ 
                status: 'unhealthy', 
                error: 'Connection failed',
                indexed_documents: 0 
            });
        }
    }

    // Update system status display
    updateSystemStatus(health) {
        // Update hero status
        const statusText = document.getElementById('statusText');
        const statusPulse = document.querySelector('.status-pulse');
        
        if (statusText) {
            statusText.textContent = health.status === 'healthy' ? 'Online' : 'Offline';
        }
        
        if (statusPulse) {
            statusPulse.style.background = health.status === 'healthy' ? '#10b981' : '#ef4444';
        }

        // Update footer system info
        const systemHealthStatus = document.getElementById('systemHealthStatus');
        const documentCount = document.getElementById('documentCount');
        
        if (systemHealthStatus) {
            systemHealthStatus.textContent = health.status;
            systemHealthStatus.style.color = health.status === 'healthy' ? '#10b981' : '#ef4444';
        }
        
        if (documentCount) {
            documentCount.textContent = health.indexed_documents || 0;
        }

        // Update chat status
        this.updateChatStatus(health.status === 'healthy' ? 'ready' : 'error');
    }

    // Update system uptime
    updateSystemUptime() {
        const uptimeElement = document.getElementById('systemUptime');
        if (uptimeElement) {
            const uptime = Date.now() - this.startTime;
            const hours = Math.floor(uptime / 3600000);
            const minutes = Math.floor((uptime % 3600000) / 60000);
            const seconds = Math.floor((uptime % 60000) / 1000);
            
            uptimeElement.textContent = 
                `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
    }

    // Initialize chat
    initializeChat() {
        this.updateChatStatus('ready');
        this.updateSendButton();
    }

    // Update chat status
    updateChatStatus(status) {
        const statusDot = document.getElementById('chatStatusDot');
        const statusText = document.getElementById('chatStatusText');
        
        if (statusDot) {
            statusDot.className = `status-dot ${status}`;
        }
        
        if (statusText) {
            const statusMessages = {
                ready: 'Ready',
                loading: 'Processing...',
                error: 'Error',
                typing: 'Typing...'
            };
            statusText.textContent = statusMessages[status] || 'Unknown';
        }
    }

    // Update send button state
    updateSendButton() {
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendButton');
        
        if (chatInput && sendButton) {
            const hasText = chatInput.value.trim().length > 0;
            const canSend = hasText && !this.isProcessing && this.systemHealth === 'healthy';
            
            sendButton.disabled = !canSend;
            sendButton.style.opacity = canSend ? '1' : '0.5';
        }
    }

    // Handle typing in chat input
    handleTyping() {
        // Could implement typing indicators here if needed
        this.updateSendButton();
    }

    // Handle file selection
    handleFileSelect(file) {
        if (!file) return;

        // Validate file type
        const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png', 'image/tiff', 'image/bmp'];
        if (!allowedTypes.includes(file.type)) {
            this.showToast('Please upload a PDF, JPG, PNG, TIFF, or BMP file.', 'error');
            return;
        }

        // Validate file size (50MB limit)
        const maxSize = 50 * 1024 * 1024;
        if (file.size > maxSize) {
            this.showToast('File size must be less than 50MB.', 'error');
            return;
        }

        this.uploadFile(file);
    }

    // Upload file to server
    async uploadFile(file) {
        this.updateUploadStatus('loading', 'Uploading...');
        this.showProgress(true);
        
        const formData = new FormData();
        formData.append('file', file);

        try {
            // Simulate progress
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 90) progress = 90;
                this.updateProgress(progress, 'Processing...');
            }, 200);

            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            clearInterval(progressInterval);

            const result = await response.json();

            if (response.ok && result.success) {
                this.updateProgress(100, 'Complete!');
                
                setTimeout(() => {
                    this.showProgress(false);
                    
                    // Add to uploaded documents
                    this.uploadedDocuments.push({
                        id: result.document_id,
                        name: result.filename,
                        size: this.formatFileSize(file.size),
                        textLength: result.text_length,
                        uploadTime: new Date()
                    });

                    this.updateDocumentsList();
                    this.updateDocumentSelector();
                    this.updateUploadStatus('ready', 'Ready');

                    this.showToast(`Successfully processed: ${result.filename}`, 'success');
                    this.addBotMessage(
                        `Great! I've processed your document "${result.filename}" and extracted ${result.text_length.toLocaleString()} characters of text. You can now ask me questions about its content.`
                    );
                }, 1000);
                
            } else {
                throw new Error(result.error || 'Upload failed');
            }

        } catch (error) {
            console.error('Upload error:', error);
            this.showProgress(false);
            this.updateUploadStatus('error', 'Failed');
            this.showToast(`Failed to process document: ${error.message}`, 'error');
        }
    }

    // Show/hide progress bar
    showProgress(show) {
        const progressElement = document.getElementById('uploadProgress');
        if (progressElement) {
            progressElement.style.display = show ? 'block' : 'none';
        }
    }

    // Update progress bar
    updateProgress(percentage, text) {
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        const progressPercent = document.getElementById('progressPercent');

        if (progressFill) {
            progressFill.style.width = `${percentage}%`;
        }
        
        if (progressText) {
            progressText.textContent = text;
        }
        
        if (progressPercent) {
            progressPercent.textContent = `${Math.round(percentage)}%`;
        }
    }

    // Update upload status
    updateUploadStatus(status, text) {
        const statusDot = document.getElementById('uploadStatusDot');
        const statusText = document.getElementById('uploadStatusText');

        if (statusDot) {
            statusDot.className = `status-dot ${status}`;
        }
        
        if (statusText) {
            statusText.textContent = text;
        }
    }

    // Update documents list display
    updateDocumentsList() {
        const documentsContainer = document.getElementById('uploadedDocuments');
        const documentsList = document.getElementById('documentsList');

        if (this.uploadedDocuments.length > 0) {
            if (documentsContainer) {
                documentsContainer.classList.add('show');
            }
            
            if (documentsList) {
                documentsList.innerHTML = this.uploadedDocuments.map(doc => `
                    <div class="document-item">
                        <div class="document-info">
                            <div class="document-name">${doc.name}</div>
                            <div class="document-meta">${doc.size} • ${doc.textLength.toLocaleString()} chars • ${this.formatTime(doc.uploadTime)}</div>
                        </div>
                    </div>
                `).join('');
            }
        } else {
            if (documentsContainer) {
                documentsContainer.classList.remove('show');
            }
        }
    }

    // Update document selector
    updateDocumentSelector() {
        const selector = document.getElementById('documentSelector');
        if (!selector) return;

        // Clear existing options except the first one
        selector.innerHTML = '<option value="">All Documents & General Knowledge</option>';
        
        // Add uploaded documents
        this.uploadedDocuments.forEach(doc => {
            const option = document.createElement('option');
            option.value = doc.id;
            option.textContent = doc.name;
            selector.appendChild(option);
        });
    }

    // Send chat message
    async sendMessage() {
        const chatInput = document.getElementById('chatInput');
        const documentSelector = document.getElementById('documentSelector');
        
        if (!chatInput || this.isProcessing) return;

        const message = chatInput.value.trim();
        if (!message) return;

        this.isProcessing = true;
        const selectedDocId = documentSelector ? documentSelector.value : null;

        // Clear input and update UI
        chatInput.value = '';
        this.updateSendButton();
        this.updateChatStatus('loading');

        // Add user message
        this.addUserMessage(message);

        // Add typing indicator
        const typingId = this.addTypingIndicator();

        try {
            const requestBody = { message };
            if (selectedDocId) {
                requestBody.document_id = selectedDocId;
            }

            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            const result = await response.json();

            // Remove typing indicator
            this.removeTypingIndicator(typingId);

            if (response.ok && result.success) {
                this.addBotMessage(result.response, {
                    sources: result.sources || [],
                    confidence: result.confidence,
                    processingTime: result.processing_time
                });
                this.updateChatStatus('ready');
            } else {
                throw new Error(result.error || 'Failed to get response');
            }

        } catch (error) {
            console.error('Chat error:', error);
            this.removeTypingIndicator(typingId);
            this.addBotMessage('Sorry, I encountered an error while processing your request. Please check your connection and try again.');
            this.showToast('Failed to send message. Please try again.', 'error');
            this.updateChatStatus('error');
        } finally {
            this.isProcessing = false;
            this.updateSendButton();
        }
    }

    // Add user message to chat
    addUserMessage(message) {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-user"></i>
            </div>
            <div class="message-content">
                <div class="message-text">${this.escapeHtml(message)}</div>
                <div class="message-time">${this.formatTime(new Date())}</div>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        this.scrollChatToBottom();
    }

    // Add bot message to chat
    addBotMessage(message, metadata = {}) {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        
        let metaHtml = '';
        if (metadata.confidence !== undefined || metadata.processingTime !== undefined || 
            (metadata.sources && metadata.sources.length > 0)) {
            
            metaHtml = '<div class="message-meta">';
            
            if (metadata.confidence !== undefined) {
                const confidencePercent = (metadata.confidence * 100).toFixed(1);
                metaHtml += `<span class="confidence-score">Confidence: ${confidencePercent}%</span>`;
            }
            
            if (metadata.processingTime !== undefined) {
                metaHtml += `<span class="processing-time">Time: ${metadata.processingTime.toFixed(2)}s</span>`;
            }
            
            metaHtml += '</div>';
            
            if (metadata.sources && metadata.sources.length > 0) {
                metaHtml += `<div class="sources"><strong>Sources:</strong> ${metadata.sources.join(', ')}</div>`;
            }
        }

        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="message-text">${this.formatMessage(message)}</div>
                <div class="message-time">${this.formatTime(new Date())}</div>
                ${metaHtml}
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        this.scrollChatToBottom();
    }

    // Add typing indicator
    addTypingIndicator() {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return null;

        const typingId = 'typing-' + Date.now();
        const typingDiv = document.createElement('div');
        typingDiv.id = typingId;
        typingDiv.className = 'message bot-message';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;

        chatMessages.appendChild(typingDiv);
        this.scrollChatToBottom();
        return typingId;
    }

    // Remove typing indicator
    removeTypingIndicator(typingId) {
        if (!typingId) return;
        const typingElement = document.getElementById(typingId);
        if (typingElement) {
            typingElement.remove();
        }
    }

    // Scroll chat to bottom
    scrollChatToBottom() {
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            setTimeout(() => {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }, 100);
        }
    }

    // Clear session
    async clearSession() {
        const confirmed = confirm('Are you sure you want to clear all uploaded documents and chat history? This action cannot be undone.');
        if (!confirmed) return;

        try {
            this.showLoading('Clearing session...');

            const response = await fetch('/api/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const result = await response.json();

            if (response.ok && result.success) {
                // Clear local state
                this.uploadedDocuments = [];
                
                // Reset UI
                this.updateDocumentsList();
                this.updateDocumentSelector();
                this.updateUploadStatus('ready', 'Ready');
                
                // Clear chat messages except welcome message
                const chatMessages = document.getElementById('chatMessages');
                if (chatMessages) {
                    chatMessages.innerHTML = `
                        <div class="message bot-message">
                            <div class="message-avatar">
                                <i class="fas fa-robot"></i>
                            </div>
                            <div class="message-content">
                                <div class="message-text">
                                    Session cleared! I'm ready to help you with new legal documents or answer legal questions.
                                </div>
                                <div class="message-time">${this.formatTime(new Date())}</div>
                            </div>
                        </div>
                    `;
                }
                
                this.showToast('Session cleared successfully!', 'success');
                
            } else {
                throw new Error(result.error || 'Failed to clear session');
            }

        } catch (error) {
            console.error('Clear session error:', error);
            this.showToast('Failed to clear session. Please try again.', 'error');
        } finally {
            this.hideLoading();
        }
    }

    // Show loading overlay
    showLoading(text = 'Processing...') {
        const loadingOverlay = document.getElementById('loadingOverlay');
        const loadingTitle = document.getElementById('loadingTitle');
        const loadingDescription = document.getElementById('loadingDescription');

        if (loadingTitle) loadingTitle.textContent = text;
        if (loadingDescription) loadingDescription.textContent = 'Please wait while we process your request';
        if (loadingOverlay) loadingOverlay.classList.add('show');
    }

    // Hide loading overlay
    hideLoading() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) loadingOverlay.classList.remove('show');
    }

    // Show toast notification
    showToast(message, type = 'info', duration = 5000) {
        const toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) return;

        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast ${type}`;

        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };

        toast.innerHTML = `
            <div class="toast-content">
                <i class="toast-icon fas ${icons[type] || icons.info}"></i>
                <span>${message}</span>
            </div>
        `;

        toastContainer.appendChild(toast);

        // Auto remove
        setTimeout(() => {
            this.removeToast(toastId);
        }, duration);

        // Click to dismiss
        toast.addEventListener('click', () => {
            this.removeToast(toastId);
        });
    }

    // Remove toast notification
    removeToast(toastId) {
        const toast = document.getElementById(toastId);
        if (toast) {
            toast.classList.add('slide-out');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, 300);
        }
    }

    // Utility functions
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatTime(date) {
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
        return date.toLocaleDateString();
    }

    formatMessage(message) {
        return message
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    handleResize() {
        // Handle responsive adjustments if needed
        this.updateSendButton();
    }
}

// Global utility functions
function scrollToSection(sectionId) {
    if (window.vakeelAI) {
        window.vakeelAI.scrollToSection(sectionId);
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.vakeelAI = new VakeelAI();
    console.log('🎯 Vakeel.ai application ready!');
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && window.vakeelAI) {
        // Refresh system status when page becomes visible
        window.vakeelAI.checkSystemHealth();
    }
});

// Handle online/offline events
window.addEventListener('online', () => {
    if (window.vakeelAI) {
        window.vakeelAI.showToast('Connection restored', 'success');
        window.vakeelAI.checkSystemHealth();
    }
});

window.addEventListener('offline', () => {
    if (window.vakeelAI) {
        window.vakeelAI.showToast('Connection lost', 'error');
    }
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VakeelAI;
}
