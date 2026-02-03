/* ==========================================================================
   NEXUS CIENCIA - LÓGICA CORE CENTRALIZADA (MAIN.JS)
   ==========================================================================
   Versión: 5.0 (CSRF Token Support + Rate Limiting Ready)
   Descripción: 
   - Control de acceso para invitados (Modal Boostrap vs Redirección).
   - Visibilidad garantizada del Toast.
   - Funcionalidad de vaciado masivo de biblioteca.
   - Soporte para CSRF tokens en peticiones AJAX.
   ========================================================================== */

// --- 1. FUNCIONES GLOBALES ---

/**
 * Obtiene el token CSRF del meta tag.
 * @returns {string} Token CSRF o string vacío si no existe.
 */
function getCsrfToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    return metaTag ? metaTag.getAttribute('content') : '';
}

// --- 2. CONSTANTES VISUALES (SVG) ---
const ICONS = {
    FILLED: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>`,
    OUTLINE: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>`
};

document.addEventListener("DOMContentLoaded", function () {

    // --- 2. INYECCIÓN DE COMPONENTES GLOBALES ---
    // Verificación defensiva: Si no existe, lo creamos. Si existe, no duplicamos.
    if (!document.getElementById('nexus-toast')) {
        const toastHTML = `<div id="nexus-toast" role="alert" aria-live="polite" aria-atomic="true">Notificación</div>`;
        document.body.insertAdjacentHTML('beforeend', toastHTML);
    }

    if (!document.getElementById('confirmation-modal')) {
        const modalHTML = `
        <div id="confirmation-modal" class="nexus-modal-overlay">
            <div class="nexus-modal-box">
                <span class="modal-icon-warning">⚠️</span>
                <h3 class="modal-title-custom" id="modal-title">¿Estás seguro?</h3>
                <p class="modal-text-custom" id="modal-text">Esta acción no se puede deshacer.</p>
                <div class="modal-actions-custom">
                    <button id="btn-cancel-modal" class="btn-modal btn-modal-cancel">Cancelar</button>
                    <button id="btn-confirm-modal" class="btn-modal btn-modal-confirm">Confirmar</button>
                </div>
            </div>
        </div>`;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    // Referencias DOM Globales
    const toastEl = document.getElementById('nexus-toast');
    const modalEl = document.getElementById('confirmation-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalText = document.getElementById('modal-text');
    let toastTimeout;
    let pendingAction = null;

    // --- 3. SISTEMA DE NOTIFICACIONES "RAPID FIRE" ---
    window.showNexusToast = function (message, type = 'default') {
        if (!toastEl) return;

        if (toastTimeout) clearTimeout(toastTimeout);

        // Reset agresivo de animación
        toastEl.style.transition = 'none';
        toastEl.classList.remove('show');
        void toastEl.offsetWidth; // Force Reflow

        toastEl.textContent = message;
        toastEl.className = '';
        toastEl.id = 'nexus-toast';

        // VISUALIZACIÓN: Z-Index extremo en línea (redundancia con CSS)
        toastEl.style.zIndex = '2147483647';

        // Usar clases CSS para colores (Auditoría: evitar estilos inline)
        toastEl.classList.remove('toast-error', 'toast-success', 'toast-default');
        if (type === 'error') toastEl.classList.add('toast-error');
        else if (type === 'success') toastEl.classList.add('toast-success');
        else toastEl.classList.add('toast-default');

        requestAnimationFrame(() => {
            toastEl.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            toastEl.classList.add('show');
        });

        // Read config from Flask-injected data attribute (fallback to 5000ms)
        const appConfig = document.getElementById('app-config');
        const TOAST_DURATION_MS = appConfig ? parseInt(appConfig.dataset.toastDuration, 10) || 5000 : 5000;

        toastTimeout = setTimeout(() => {
            toastEl.classList.remove('show');
        }, TOAST_DURATION_MS);
    };

    // --- LOADING STATES ---
    window.showLoading = function (button) {
        if (!button) return;
        const originalText = button.innerHTML;
        button.dataset.originalText = originalText;
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Cargando...';
    };

    window.hideLoading = function (button) {
        if (!button) return;
        button.disabled = false;
        if (button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
        }
    };

    // --- 4. CONTROL DEL SIDEBAR ---
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const mobileToggle = document.getElementById('mobile-toggle');
    const sidebarOverlay = document.getElementById('sidebar-overlay');

    // Variable para guardar posición de scroll
    let savedScrollY = 0;

    function openSidebar() {
        // Guardar posición de scroll antes de bloquear el body
        savedScrollY = window.scrollY;
        document.body.classList.add('sidebar-toggled');
        // Mantener visualmente la posición usando top negativo
        document.body.style.top = `-${savedScrollY}px`;
    }

    function closeSidebar() {
        document.body.classList.remove('sidebar-toggled');
        document.body.style.top = '';
        // Restaurar la posición de scroll instantáneamente (sin animación)
        window.scrollTo({
            top: savedScrollY,
            left: 0,
            behavior: 'instant'
        });
    }

    function toggleSidebar() {
        if (document.body.classList.contains('sidebar-toggled')) {
            closeSidebar();
        } else {
            openSidebar();
        }
    }

    if (sidebarToggle) sidebarToggle.addEventListener('click', toggleSidebar);
    if (mobileToggle) mobileToggle.addEventListener('click', toggleSidebar);
    if (sidebarOverlay) sidebarOverlay.addEventListener('click', closeSidebar);


    // --- 5. GESTIÓN DEL MODAL UNIFICADO ---
    function openModal(title, text, confirmCallback) {
        if (!modalEl) return;
        modalTitle.textContent = title;
        modalText.textContent = text;
        pendingAction = confirmCallback;
        modalEl.classList.add('active');
    }

    function closeModal() {
        if (!modalEl) return;
        modalEl.classList.remove('active');
        pendingAction = null;
    }

    // Exponer closeModal globalmente para keyboard shortcuts
    window.closeModal = closeModal;

    const btnCancel = document.getElementById('btn-cancel-modal');
    const btnConfirm = document.getElementById('btn-confirm-modal');

    if (btnCancel) btnCancel.addEventListener('click', closeModal);
    if (btnConfirm) btnConfirm.addEventListener('click', () => {
        if (pendingAction) pendingAction();
        closeModal();
    });

    if (modalEl) {
        modalEl.addEventListener('click', (e) => {
            if (e.target === modalEl) closeModal();
        });
    }

    // --- 6. LÓGICA DE BIBLIOTECA (OPTIMISTIC UI) ---
    function setButtonState(btn, isSaved) {
        if (!btn) return;

        if (isSaved) {
            btn.classList.add('saved');
            if (btn.classList.contains('btn-save')) {
                btn.innerHTML = `${ICONS.FILLED} Guardado`;
            } else {
                btn.innerHTML = ICONS.FILLED;
            }
        } else {
            btn.classList.remove('saved');
            if (btn.classList.contains('btn-save')) {
                btn.innerHTML = `${ICONS.OUTLINE} Guardar en Biblioteca`;
            } else {
                btn.innerHTML = ICONS.OUTLINE;
            }
        }
    }

    function executeLibraryToggle(articleId, btn) {
        const wasSaved = btn.classList.contains('saved');
        const isProfilePage = window.location.pathname.includes('/perfil');
        const rowElement = btn.closest('tr');

        setButtonState(btn, !wasSaved);

        if (isProfilePage && wasSaved && rowElement) {
            rowElement.style.transition = 'opacity 0.2s';
            rowElement.style.opacity = '0.3';
            rowElement.style.pointerEvents = 'none';
        }

        fetch(`/api/toggle_biblioteca/${articleId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()  // CSRF protection
            }
        })
            .then(response => {
                if (response.status === 403) throw new Error("AUTH_REQUIRED");
                if (!response.ok) throw new Error("SERVER_ERROR");
                return response.json();
            })
            .then(data => {
                if (data.action === 'added') {
                    window.showNexusToast("📚 Guardado en biblioteca", "success");
                } else {
                    window.showNexusToast("Archivo Eliminado");

                    if (isProfilePage && rowElement) {
                        setTimeout(() => {
                            rowElement.remove();
                            const tbody = document.getElementById('libraryTableBody');
                            if (tbody && tbody.children.length === 0) window.location.reload();
                        }, 500);
                    }
                }
            })
            .catch(error => {
                console.error(error);
                setButtonState(btn, wasSaved);

                if (isProfilePage && rowElement) {
                    rowElement.style.opacity = '1';
                    rowElement.style.pointerEvents = 'auto';
                }

                if (error.message === "AUTH_REQUIRED") {
                    window.location.href = '/login';
                } else {
                    window.showNexusToast("Error de conexión. Intenta de nuevo.", "error");
                }
            });
    }

    // --- 7. LÓGICA DE VACIADO MASIVO DE BIBLIOTECA ---
    function executeEmptyLibrary() {
        fetch('/api/vaciar_biblioteca', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()  // CSRF protection
            }
        })
            .then(response => {
                if (response.status === 403) throw new Error("AUTH_REQUIRED");
                if (!response.ok) throw new Error("SERVER_ERROR");
                return response.json();
            })
            .then(data => {
                window.showNexusToast("Archivos Eliminados", "success");
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            })
            .catch(error => {
                console.error(error);
                window.showNexusToast("Error al vaciar biblioteca.", "error");
            });
    }

    // --- 8. DELEGACIÓN DE EVENTOS CENTRALIZADA ---
    document.body.addEventListener('click', function (e) {

        const btnSave = e.target.closest('.btn-save-card, .btn-save, .action-save');

        if (btnSave) {

            // CASO A: Documento no disponible (PDF inactivo)
            if (btnSave.classList.contains('btn-pdf')) {
                const available = btnSave.getAttribute('data-available');
                if (available === 'false') {
                    e.preventDefault();
                    window.showNexusToast("⚠️ Documento no disponible", "error");
                }
                return;
            }

            // CASO B: Gestión de Acceso (Usuario Logueado vs Invitado)
            const id = btnSave.getAttribute('data-id');
            const available = btnSave.getAttribute('data-available');

            // 1. INVITADO: Botón sin ID (Disparador de Login)
            if (!id) {
                window.showNexusToast("🔒 Inicia sesión para guardar", "default");

                // Si es un botón nativo de Bootstrap (tiene data-bs-toggle), NO bloqueamos el evento.
                // Permitimos que Bootstrap abra el modal.
                if (btnSave.hasAttribute('data-bs-toggle')) {
                    return;
                }

                // Si no tiene modal (fallback), bloqueamos y redirigimos.
                e.preventDefault();
                e.stopPropagation();
                setTimeout(() => window.location.href = '/login', 1000);
                return;
            }

            // 2. USUARIO: Lógica de Biblioteca
            e.preventDefault();
            e.stopPropagation();

            if (available === 'false') {
                window.showNexusToast("⚠️ Recurso no disponible", "error");
                return;
            }

            if (btnSave.classList.contains('saved')) {
                openModal(
                    "¿Quitar de la biblioteca?",
                    "Este artículo ya no aparecerá en tu lista de guardados.",
                    () => executeLibraryToggle(id, btnSave)
                );
            } else {
                executeLibraryToggle(id, btnSave);
            }
            return;
        }

        // CASO C: Botón "Vaciar Biblioteca"
        const btnEmpty = e.target.closest('#btn-empty-library');
        if (btnEmpty) {
            e.preventDefault();
            openModal(
                "¿Vaciar toda tu biblioteca?",
                "Esta acción eliminará TODOS los artículos guardados. No se puede deshacer.",
                () => executeEmptyLibrary()
            );
        }

        // NOTA: Los botones de eliminar admin (.btn-delete) se manejan en admin.js
        // mediante formularios POST con la clase .delete-form para seguridad CSRF
    });

});

// ========================================
// DARK MODE TOGGLE
// ========================================
const themeToggle = document.getElementById('theme-toggle');
const currentTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', currentTheme);

// Update toggle state and icon highlighting
function updateThemeState(theme) {
    const sunIcon = document.querySelector('.theme-icon-sun');
    const moonIcon = document.querySelector('.theme-icon-moon');
    const toggle = document.getElementById('theme-toggle');

    if (theme === 'dark') {
        if (sunIcon) sunIcon.style.opacity = '0.4';
        if (moonIcon) moonIcon.style.opacity = '1';
        if (toggle && toggle.type === 'checkbox') toggle.checked = true;
    } else {
        if (sunIcon) sunIcon.style.opacity = '1';
        if (moonIcon) moonIcon.style.opacity = '0.4';
        if (toggle && toggle.type === 'checkbox') toggle.checked = false;
    }
}

updateThemeState(currentTheme);

if (themeToggle) {
    themeToggle.addEventListener('change', () => {
        const newTheme = themeToggle.checked ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeState(newTheme);
    });
}

// ========================================
// KEYBOARD SHORTCUTS
// ========================================
document.addEventListener('keydown', (e) => {
    // Ctrl+K o Cmd+K: Abrir búsqueda
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[name=\"q\"]');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }

    // Esc: Cerrar modal
    if (e.key === 'Escape') {
        if (typeof window.closeModal === 'function') {
            window.closeModal();
        }
    }
});
