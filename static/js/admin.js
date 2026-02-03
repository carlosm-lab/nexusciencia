/* ==========================================================================
   NEXUS CIENCIA - LÓGICA DEL PANEL DE ADMINISTRACIÓN (ADMIN.JS)
   ==========================================================================
   Descripción: Maneja la interactividad del dashboard administrativo.
   Funciones:
   - Filtrado en tiempo real de la tabla de artículos.
   - Ordenamiento dinámico (Fecha / Alfabético).
   - Auto-cierre de alertas del sistema.
   - Confirmación de eliminación con modal.
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function () {

    // --- 1. AUTO-DISMISS DE ALERTAS ---
    // Oculta automáticamente los mensajes flash después de 5 segundos
    const alertBox = document.getElementById('system-alert');
    if (alertBox) {
        setTimeout(() => {
            alertBox.style.transition = "opacity 0.5s ease";
            alertBox.style.opacity = "0";
            setTimeout(() => alertBox.remove(), 500);
        }, 5000);
    }

    // --- 2. LÓGICA DE TABLA (FILTRADO Y ORDEN) ---
    const searchInput = document.getElementById('searchInput');
    const sortSelect = document.getElementById('sortSelect');
    const tableBody = document.getElementById('articlesTableBody');

    // Si no existen estos elementos (ej. si la tabla está vacía), salimos.
    if (!tableBody) return;

    // Convertimos NodeList a Array para poder ordenar
    const rows = Array.from(document.querySelectorAll('.article-row'));

    // A. FILTRADO (BÚSQUEDA EN TIEMPO REAL)
    if (searchInput) {
        searchInput.addEventListener('keyup', function (e) {
            const term = e.target.value.toLowerCase();

            rows.forEach(row => {
                // Buscamos dentro del título del artículo
                // Nota: Usamos .article-title o buscamos strong dentro de la celda
                const titleElement = row.querySelector('.article-title-cell strong');
                if (titleElement) {
                    const titleText = titleElement.textContent.toLowerCase();
                    // Mostrar u ocultar fila según coincidencia
                    row.style.display = titleText.includes(term) ? '' : 'none';
                }
            });
        });
    }

    // B. ORDENAMIENTO (FECHA / ALFABÉTICO)
    if (sortSelect) {
        sortSelect.addEventListener('change', function (e) {
            const criteria = e.target.value;

            const sortedRows = rows.sort((a, b) => {
                // Obtener valores de texto para comparar
                const titleA = a.querySelector('.article-title-cell strong').textContent.toLowerCase();
                const titleB = b.querySelector('.article-title-cell strong').textContent.toLowerCase();

                // Obtener fechas (Formato esperado en HTML: DD/MM/YYYY)
                const dateTextA = a.querySelector('.article-date-cell').textContent.trim();
                const dateTextB = b.querySelector('.article-date-cell').textContent.trim();

                // Conversión simple para sort: invertir cadena (01/12/2025 -> 20251201)
                // Esto permite comparar como números o strings ISO básicos
                const dateA = dateTextA.split('/').reverse().join('');
                const dateB = dateTextB.split('/').reverse().join('');

                switch (criteria) {
                    case 'alpha-asc': return titleA.localeCompare(titleB);
                    case 'alpha-desc': return titleB.localeCompare(titleA);
                    case 'date-asc': return dateA.localeCompare(dateB); // Antiguos primero
                    case 'date-desc': return dateB.localeCompare(dateA); // Recientes primero
                    default: return 0;
                }
            });

            // Re-inyectar filas ordenadas en el DOM
            tableBody.innerHTML = '';
            sortedRows.forEach(row => tableBody.appendChild(row));
        });
    }

    // --- 3. CONFIRMACIÓN DE ELIMINACIÓN (POST FORMS) ---
    document.querySelectorAll('.delete-form').forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            // Usar el modal global de main.js si existe
            if (typeof window.showNexusToast !== 'undefined') {
                // Check if modal exists
                const modalEl = document.getElementById('confirmation-modal');
                const modalTitle = document.getElementById('modal-title');
                const modalText = document.getElementById('modal-text');
                const btnConfirm = document.getElementById('btn-confirm-modal');
                const btnCancel = document.getElementById('btn-cancel-modal');

                if (modalEl && modalTitle && modalText) {
                    modalTitle.textContent = '¿Eliminar artículo?';
                    modalText.textContent = 'El artículo será movido a la papelera. Podrás restaurarlo posteriormente.';
                    modalEl.classList.add('active');

                    // Remove previous listeners and add new ones
                    const newBtnConfirm = btnConfirm.cloneNode(true);
                    btnConfirm.parentNode.replaceChild(newBtnConfirm, btnConfirm);

                    newBtnConfirm.addEventListener('click', () => {
                        modalEl.classList.remove('active');
                        form.submit();
                    });

                    return;
                }
            }

            // Fallback: confirm nativo
            if (confirm('¿Estás seguro de eliminar este artículo?')) {
                form.submit();
            }
        });
    });

    // --- 4. PANEL DE DIAGNÓSTICOS ---
    initDiagnosticsPanel();
});

/**
 * Inicializa el panel de diagnósticos del sistema
 */
function initDiagnosticsPanel() {
    const runAllBtn = document.getElementById('btn-run-all-checks');
    const individualBtns = document.querySelectorAll('.btn-run-check');

    if (!runAllBtn && !individualBtns.length) return;

    // Obtener CSRF token
    function getCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    }

    // Mapeo de checks a sus elementos
    const checkMapping = {
        'database': 'Base de Datos',
        'config': 'Configuración',
        'security': 'Seguridad',
        'templates': 'Templates',
        'static': 'Archivos Estáticos',
        'articles': 'Integridad Artículos',
        'disk': 'Espacio en Disco',
        'logs': 'Archivo de Log'
    };

    // Ejecutar un check individual
    async function runSingleCheck(endpoint, checkName) {
        const card = document.querySelector(`[data-check="${checkName}"]`);
        const statusEl = document.getElementById(`status-${checkName}`);
        const resultEl = document.getElementById(`result-${checkName}`);
        const btn = card?.querySelector('.btn-run-check');

        if (!card) return null;

        // Estado: ejecutando
        card.classList.remove('status-pass', 'status-fail', 'status-error');
        statusEl.innerHTML = '<span class="status-running">⏳ Ejecutando...</span>';
        if (btn) btn.disabled = true;

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            });

            const data = await response.json();

            // Actualizar estado
            if (data.status === 'pass') {
                card.classList.add('status-pass');
                statusEl.innerHTML = '<span class="status-pass-text">✅ Pasó</span>';
            } else if (data.status === 'fail') {
                card.classList.add('status-fail');
                statusEl.innerHTML = '<span class="status-fail-text">❌ Falló</span>';
            } else {
                card.classList.add('status-error');
                statusEl.innerHTML = '<span class="status-error-text">⚠️ Error</span>';
            }

            // Mostrar resultado
            resultEl.classList.add('visible');
            resultEl.innerHTML = `
                <div class="result-message">${data.message}</div>
                ${Object.keys(data.details || {}).length > 0 ?
                    `<div class="result-details">${JSON.stringify(data.details, null, 2)}</div>` : ''
                }
                <div class="result-duration">⏱️ ${data.duration_ms}ms</div>
            `;

            return data;

        } catch (error) {
            card.classList.add('status-error');
            statusEl.innerHTML = '<span class="status-error-text">⚠️ Error</span>';
            resultEl.classList.add('visible');
            resultEl.innerHTML = `<div class="result-message">Error de conexión: ${error.message}</div>`;
            return { status: 'error', message: error.message };
        } finally {
            if (btn) btn.disabled = false;
        }
    }

    // Ejecutar todos los checks
    async function runAllChecks() {
        runAllBtn.disabled = true;
        runAllBtn.innerHTML = '⏳ Ejecutando tests...';

        const summaryEl = document.getElementById('diagnostics-summary');
        summaryEl.style.display = 'flex';

        try {
            const response = await fetch('/api/diagnostics/run-all', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            });

            const data = await response.json();

            // Actualizar resumen
            const score = data.summary.health_score;
            const scoreEl = document.getElementById('health-score');
            scoreEl.textContent = score + '%';
            scoreEl.className = 'summary-score ' +
                (score >= 80 ? 'score-good' : score >= 50 ? 'score-warning' : 'score-bad');

            document.getElementById('stat-passed').textContent = `✅ ${data.summary.passed} pasados`;
            document.getElementById('stat-failed').textContent = `❌ ${data.summary.failed} fallidos`;
            document.getElementById('stat-errors').textContent = `⚠️ ${data.summary.errors} errores`;

            // Actualizar cada card
            data.checks.forEach(check => {
                // Encontrar el checkName basado en el name
                const checkName = Object.keys(checkMapping).find(
                    key => checkMapping[key] === check.name
                );

                if (!checkName) return;

                const card = document.querySelector(`[data-check="${checkName}"]`);
                const statusEl = document.getElementById(`status-${checkName}`);
                const resultEl = document.getElementById(`result-${checkName}`);

                if (!card) return;

                card.classList.remove('status-pass', 'status-fail', 'status-error');

                if (check.status === 'pass') {
                    card.classList.add('status-pass');
                    statusEl.innerHTML = '<span class="status-pass-text">✅ Pasó</span>';
                } else if (check.status === 'fail') {
                    card.classList.add('status-fail');
                    statusEl.innerHTML = '<span class="status-fail-text">❌ Falló</span>';
                } else {
                    card.classList.add('status-error');
                    statusEl.innerHTML = '<span class="status-error-text">⚠️ Error</span>';
                }

                resultEl.classList.add('visible');
                resultEl.innerHTML = `
                    <div class="result-message">${check.message}</div>
                    ${Object.keys(check.details || {}).length > 0 ?
                        `<div class="result-details">${JSON.stringify(check.details, null, 2)}</div>` : ''
                    }
                    <div class="result-duration">⏱️ ${check.duration_ms}ms</div>
                `;
            });

        } catch (error) {
            console.error('Error running all checks:', error);
            if (typeof window.showNexusToast === 'function') {
                window.showNexusToast('Error al ejecutar diagnósticos', 'error');
            }
        } finally {
            runAllBtn.disabled = false;
            runAllBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                Ejecutar Todos los Tests
            `;
        }
    }

    // Event listeners
    if (runAllBtn) {
        runAllBtn.addEventListener('click', runAllChecks);
    }

    individualBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const endpoint = this.dataset.endpoint;
            const card = this.closest('.diagnostic-card');
            const checkName = card?.dataset.check;

            if (endpoint && checkName) {
                runSingleCheck(endpoint, checkName);
            }
        });
    });
}