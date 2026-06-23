// === THEME TOGGLE ===
const themeToggle = document.getElementById('themeToggle');
const html = document.documentElement;
const themeIcon = themeToggle ? themeToggle.querySelector('i') : null;

function setTheme(theme) {
    html.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    if (themeIcon) {
        themeIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'light';
setTheme(savedTheme);

if (themeToggle) {
    themeToggle.addEventListener('click', function() {
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });
}

// === MODAL ===
const modal = document.getElementById('transactionModal');
const fabAdd = document.getElementById('fabAdd');
const modalClose = document.getElementById('modalClose');

function openModal() {
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        // Set today's date
        const dateInput = document.getElementById('modal-date');
        if (dateInput && !dateInput.value) {
            const today = new Date();
            const yyyy = today.getFullYear();
            const mm = String(today.getMonth() + 1).padStart(2, '0');
            const dd = String(today.getDate()).padStart(2, '0');
            dateInput.value = `${yyyy}-${mm}-${dd}`;
        }
    }
}

function closeModal() {
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

if (fabAdd) {
    fabAdd.addEventListener('click', openModal);
}

if (modalClose) {
    modalClose.addEventListener('click', closeModal);
}

if (modal) {
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal();
        }
    });
}

// Close modal on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && modal && modal.classList.contains('active')) {
        closeModal();
    }
});

// === TYPE SELECTOR (Modal) ===
const modalTypeBtns = document.querySelectorAll('#modalTransactionForm .type-btn');
const modalExpenseGroup = document.getElementById('modal-expense-cats');
const modalIncomeGroup = document.getElementById('modal-income-cats');

modalTypeBtns.forEach(btn => {
    btn.addEventListener('click', function() {
        const type = this.dataset.type;

        modalTypeBtns.forEach(b => b.classList.remove('active'));
        this.classList.add('active');

        const radio = this.querySelector('input[type="radio"]');
        if (radio) radio.checked = true;

        if (type === 'income') {
            if (modalExpenseGroup) modalExpenseGroup.style.display = 'none';
            if (modalIncomeGroup) {
                modalIncomeGroup.style.display = '';
                const firstOpt = modalIncomeGroup.querySelector('option');
                if (firstOpt) firstOpt.selected = true;
            }
        } else {
            if (modalIncomeGroup) modalIncomeGroup.style.display = 'none';
            if (modalExpenseGroup) {
                modalExpenseGroup.style.display = '';
                const firstOpt = modalExpenseGroup.querySelector('option');
                if (firstOpt) firstOpt.selected = true;
            }
        }
    });
});

// === TODAY BUTTON (Modal) ===
const modalTodayBtn = document.getElementById('modalTodayBtn');
const modalDateInput = document.getElementById('modal-date');

if (modalTodayBtn && modalDateInput) {
    modalTodayBtn.addEventListener('click', function() {
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        modalDateInput.value = `${yyyy}-${mm}-${dd}`;
    });
}

// === FLASH MESSAGES ===
document.querySelectorAll('.close-alert').forEach(btn => {
    btn.addEventListener('click', function() {
        this.closest('.alert').remove();
    });
});

// Auto-hide flash messages after 5 seconds
setTimeout(() => {
    document.querySelectorAll('.alert').forEach(alert => {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(() => alert.remove(), 300);
    });
}, 5000);

// === BACK TO TOP ===
const backToTop = document.getElementById('backToTopBtn');
if (backToTop) {
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            backToTop.classList.add('visible');
        } else {
            backToTop.classList.remove('visible');
        }
    });

    backToTop.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// === FILTERS ===
const applyFilters = document.getElementById('applyFilters');
if (applyFilters) {
    applyFilters.addEventListener('click', function() {
        const type = document.getElementById('filterType').value;
        const category = document.getElementById('filterCategory').value;
        window.location.href = window.location.pathname + "?type=" + type + "&category=" + category;
    });
}

// ========== ЗАПРЕТ НА ОТКРЫТИЕ НОВЫХ ВКЛАДОК (полный контроль) ==========
(function() {
    // Перехватываем все клики по ссылкам и кнопкам
    document.addEventListener('mousedown', function(e) {
        // Если зажат Ctrl, Cmd, Shift или средняя кнопка — отменяем
        if (e.ctrlKey || e.metaKey || e.shiftKey || e.button === 1) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
    }, true);
    
    document.addEventListener('click', function(e) {
        let target = e.target.closest('a');
        if (target && target.href) {
            // Принудительно убираем target="_blank"
            target.removeAttribute('target');
            // Если всё ещё пытается открыться в новом окне
            if (target.target === '_blank') {
                e.preventDefault();
                target.target = '';
                window.location.href = target.href;
            }
        }
    }, true);
})();