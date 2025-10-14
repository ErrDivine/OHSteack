// 主要JavaScript文件

// DOM加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有功能
    initFlashMessages();
    initDropdowns();
    initFormValidation();
    initFileUpload();
    initMarkdownPreview();
    initConfirmDelete();
});

// Flash消息自动消失
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        // 5秒后自动消失
        setTimeout(() => {
            message.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
}

// 下拉菜单处理
function initDropdowns() {
    // 点击外部关闭下拉菜单
    document.addEventListener('click', function(e) {
        const dropdowns = document.querySelectorAll('.nav-dropdown');
        dropdowns.forEach(dropdown => {
            if (!dropdown.parentElement.contains(e.target)) {
                dropdown.style.opacity = '0';
                dropdown.style.visibility = 'hidden';
            }
        });
    });
}

// 表单验证增强
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    
                    // 显示错误提示
                    let feedback = field.nextElementSibling;
                    if (!feedback || !feedback.classList.contains('invalid-feedback')) {
                        feedback = document.createElement('div');
                        feedback.classList.add('invalid-feedback');
                        feedback.textContent = '此字段为必填项';
                        field.parentElement.appendChild(feedback);
                    }
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
        
        // 实时验证
        const inputs = form.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                if (this.hasAttribute('required') && this.value.trim()) {
                    this.classList.remove('is-invalid');
                }
            });
        });
    });
}

// 文件上传预览
function initFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const files = Array.from(e.target.files);
            const preview = document.getElementById(input.getAttribute('data-preview'));
            
            if (preview) {
                preview.innerHTML = '';
                files.forEach(file => {
                    const item = document.createElement('div');
                    item.classList.add('file-preview-item');
                    
                    const icon = getFileIcon(file.type);
                    const size = formatFileSize(file.size);
                    
                    item.innerHTML = `
                        <i class="${icon}"></i>
                        <div class="file-info">
                            <div class="file-name">${file.name}</div>
                            <div class="file-size">${size}</div>
                        </div>
                    `;
                    
                    preview.appendChild(item);
                });
            }
        });
    });
}

// Markdown实时预览
function initMarkdownPreview() {
    const markdownInputs = document.querySelectorAll('[data-markdown-preview]');
    markdownInputs.forEach(input => {
        const previewId = input.getAttribute('data-markdown-preview');
        const preview = document.getElementById(previewId);
        
        if (preview) {
            // 防抖函数
            let timeout;
            input.addEventListener('input', function() {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    // 这里应该调用后端API进行Markdown渲染
                    // 暂时使用简单的替换
                    let html = this.value;
                    html = html.replace(/^# (.*?)$/gm, '<h1>$1</h1>');
                    html = html.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
                    html = html.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
                    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
                    html = html.replace(/\n/g, '<br>');
                    
                    preview.innerHTML = html || '<p class="text-muted">预览将在此显示...</p>';
                }, 300);
            });
        }
    });
}

// 删除确认
function initConfirmDelete() {
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm-delete') || '确定要删除吗？';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

// 辅助函数

// 获取文件图标
function getFileIcon(fileType) {
    if (fileType.startsWith('image/')) return 'fas fa-image';
    if (fileType.startsWith('video/')) return 'fas fa-video';
    if (fileType.includes('pdf')) return 'fas fa-file-pdf';
    if (fileType.includes('word') || fileType.includes('document')) return 'fas fa-file-word';
    if (fileType.includes('excel') || fileType.includes('spreadsheet')) return 'fas fa-file-excel';
    if (fileType.includes('powerpoint') || fileType.includes('presentation')) return 'fas fa-file-powerpoint';
    if (fileType.includes('zip') || fileType.includes('rar') || fileType.includes('compressed')) return 'fas fa-file-archive';
    return 'fas fa-file';
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// 添加动画类
function animateElement(element, animationClass) {
    element.classList.add(animationClass);
    element.addEventListener('animationend', function() {
        element.classList.remove(animationClass);
    }, { once: true });
}

// 平滑滚动
function smoothScroll(target) {
    const element = document.querySelector(target);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// 导出函数供其他脚本使用
window.OHSteack = {
    animateElement,
    smoothScroll,
    formatFileSize,
    getFileIcon
};
