// Управление портфолио в админке
class PortfolioManager {
    constructor() {
        this.apiUrl = '/admin/portfolio';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadPortfolio();
    }

    bindEvents() {
        // Обработка формы добавления/редактирования
        const form = document.getElementById('portfolioForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleSubmit(e));
        }

        // Обработка загрузки изображений
        const imageInput = document.getElementById('portfolioImage');
        if (imageInput) {
            imageInput.addEventListener('change', (e) => this.handleImageUpload(e));
        }

        // Обработка кнопок действий
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('edit-portfolio')) {
                this.editPortfolio(e.target.dataset.id);
            } else if (e.target.classList.contains('delete-portfolio')) {
                this.deletePortfolio(e.target.dataset.id);
            } else if (e.target.classList.contains('toggle-featured')) {
                this.toggleFeatured(e.target.dataset.id);
            }
        });
    }

    async loadPortfolio() {
        try {
            const response = await fetch(`${this.apiUrl}/`);
            const data = await response.json();
            this.renderPortfolio(data);
        } catch (error) {
            console.error('Ошибка загрузки портфолио:', error);
            this.showError('Не удалось загрузить портфолио');
        }
    }

    renderPortfolio(portfolio) {
        const container = document.getElementById('portfolioList');
        if (!container) return;

        container.innerHTML = portfolio.map(item => `
            <div class="portfolio-item" data-id="${item.id}">
                <div class="portfolio-image">
                    <img src="${item.image_url || '/static/images/placeholder.jpg'}" 
                         alt="${item.title}" loading="lazy">
                    ${item.featured ? '<span class="featured-badge">Рекомендуемый</span>' : ''}
                </div>
                <div class="portfolio-content">
                    <h3>${item.title}</h3>
                    <p class="portfolio-category">${item.category || 'Без категории'}</p>
                    <p class="portfolio-description">${item.description.substring(0, 100)}...</p>
                    <div class="portfolio-meta">
                        <span class="status status-${item.status}">${this.getStatusText(item.status)}</span>
                        <span class="technologies">${item.technologies || ''}</span>
                    </div>
                    <div class="portfolio-actions">
                        <button class="btn btn-sm btn-primary edit-portfolio" data-id="${item.id}">
                            <i class="fas fa-edit"></i> Редактировать
                        </button>
                        <button class="btn btn-sm btn-success toggle-featured" data-id="${item.id}">
                            <i class="fas fa-star"></i> ${item.featured ? 'Убрать из рекомендуемых' : 'Сделать рекомендуемым'}
                        </button>
                        <button class="btn btn-sm btn-danger delete-portfolio" data-id="${item.id}">
                            <i class="fas fa-trash"></i> Удалить
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const portfolioId = formData.get('id');
        
        try {
            const method = portfolioId ? 'PUT' : 'POST';
            const url = portfolioId ? `${this.apiUrl}/${portfolioId}` : this.apiUrl;
            
            const response = await fetch(url, {
                method: method,
                body: formData
            });

            if (response.ok) {
                this.showSuccess(portfolioId ? 'Проект обновлен' : 'Проект добавлен');
                this.loadPortfolio();
                this.resetForm();
            } else {
                throw new Error('Ошибка сервера');
            }
        } catch (error) {
            console.error('Ошибка сохранения:', error);
            this.showError('Не удалось сохранить проект');
        }
    }

    async editPortfolio(id) {
        try {
            const response = await fetch(`${this.apiUrl}/${id}`);
            const data = await response.json();
            this.fillForm(data);
        } catch (error) {
            console.error('Ошибка загрузки проекта:', error);
            this.showError('Не удалось загрузить проект');
        }
    }

    async deletePortfolio(id) {
        if (!confirm('Вы уверены, что хотите удалить этот проект?')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiUrl}/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showSuccess('Проект удален');
                this.loadPortfolio();
            } else {
                throw new Error('Ошибка сервера');
            }
        } catch (error) {
            console.error('Ошибка удаления:', error);
            this.showError('Не удалось удалить проект');
        }
    }

    async toggleFeatured(id) {
        try {
            const response = await fetch(`${this.apiUrl}/${id}/toggle-featured`, {
                method: 'POST'
            });

            if (response.ok) {
                this.showSuccess('Статус рекомендуемого изменен');
                this.loadPortfolio();
            } else {
                throw new Error('Ошибка сервера');
            }
        } catch (error) {
            console.error('Ошибка изменения статуса:', error);
            this.showError('Не удалось изменить статус');
        }
    }

    handleImageUpload(e) {
        const file = e.target.files[0];
        if (!file) return;

        // Проверка размера файла (максимум 5MB)
        if (file.size > 5 * 1024 * 1024) {
            this.showError('Файл слишком большой. Максимальный размер: 5MB');
            e.target.value = '';
            return;
        }

        // Проверка типа файла
        const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp'];
        if (!allowedTypes.includes(file.type)) {
            this.showError('Неподдерживаемый формат файла. Используйте JPEG, PNG или WebP');
            e.target.value = '';
            return;
        }

        // Предварительный просмотр изображения
        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = document.getElementById('imagePreview');
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
        };
        reader.readAsDataURL(file);
    }

    fillForm(data) {
        const form = document.getElementById('portfolioForm');
        if (!form) return;

        Object.keys(data).forEach(key => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) {
                input.value = data[key] || '';
            }
        });

        // Обновляем предварительный просмотр изображения
        const preview = document.getElementById('imagePreview');
        if (preview && data.image_url) {
            preview.src = data.image_url;
            preview.style.display = 'block';
        }
    }

    resetForm() {
        const form = document.getElementById('portfolioForm');
        if (form) {
            form.reset();
            
            // Скрываем предварительный просмотр
            const preview = document.getElementById('imagePreview');
            if (preview) {
                preview.style.display = 'none';
            }
        }
    }

    getStatusText(status) {
        const statusMap = {
            'active': 'Активный',
            'completed': 'Завершен',
            'in_progress': 'В процессе',
            'paused': 'Приостановлен'
        };
        return statusMap[status] || status;
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check' : 'exclamation-triangle'}"></i>
            ${message}
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.includes('/admin/portfolio')) {
        new PortfolioManager();
    }
});
