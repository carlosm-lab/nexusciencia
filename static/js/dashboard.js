/* ==========================================================================
   NEXUS CIENCIA - LÓGICA DE DASHBOARD & MULTIMEDIA (DASHBOARD.JS)
   ==========================================================================
   Versión: 2.1 (Fix: PDF Downloads & ID-Based Logic)
   Descripción: Controla la reproducción de audio y la disponibilidad de recursos.
   ========================================================================== */

document.addEventListener("DOMContentLoaded", function() {
    
    // --- 1. GESTIÓN DE DISPONIBILIDAD ---
    // Intercepta clics en botones de acción. Solo previene si data-available="false".
    document.body.addEventListener('click', function(e) {
        const btn = e.target.closest('.action-read, .action-play, .action-pdf');
        
        if (btn) {
            const available = btn.getAttribute('data-available');
            
            // Si NO está disponible -> Bloquear y notificar
            if (available === 'false') {
                e.preventDefault();
                e.stopPropagation();
                if (window.showNexusToast) {
                    window.showNexusToast("⚠️ Recurso no disponible temporalmente", "error");
                }
            }
            // Si está disponible ('true'), dejamos que el evento continúe.
            // Esto permite que los enlaces <a> del PDF funcionen nativamente.
        }
    });
});

// --- 2. MOTOR DE AUDIO (GLOBAL SCOPE) ---

/**
 * Inicia la reproducción de un audio específico y gestiona la UI.
 * @param {string|number} id - ID del artículo (ej: 1, 45)
 */
window.playCardAudio = function(id) {
    const audioEl = document.getElementById(`audio-${id}`);
    const defaultActionsEl = document.getElementById(`actions-${id}`);
    const playerControlsEl = document.getElementById(`player-wrapper-${id}`);

    if (!audioEl) {
        console.error(`Audio element #audio-${id} not found.`);
        if(window.showNexusToast) window.showNexusToast("Error: Audio no encontrado", "error");
        return;
    }

    // 1. Detener otros audios
    document.querySelectorAll('audio').forEach(audio => {
        if (audio.id !== `audio-${id}`) {
            audio.pause();
            audio.currentTime = 0;
        }
    });

    // 2. Resetear UI global
    document.querySelectorAll('.actions-player').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.actions-default').forEach(el => el.classList.remove('hidden'));

    // 3. Activar UI local
    if (defaultActionsEl && playerControlsEl) {
        defaultActionsEl.classList.add('hidden');
        playerControlsEl.classList.remove('hidden');
    }

    // 4. Play
    const playPromise = audioEl.play();
    
    if (playPromise !== undefined) {
        playPromise.catch(error => {
            console.warn("Autoplay prevenido o error de fuente:", error);
            // Revertir UI
            if (defaultActionsEl && playerControlsEl) {
                playerControlsEl.classList.add('hidden');
                defaultActionsEl.classList.remove('hidden');
            }
            if(window.showNexusToast) window.showNexusToast("No se pudo reproducir el audio", "error");
        });
    }
};

window.stopCardAudio = function(id) {
    const audioEl = document.getElementById(`audio-${id}`);
    const defaultActionsEl = document.getElementById(`actions-${id}`);
    const playerControlsEl = document.getElementById(`player-wrapper-${id}`);

    if (audioEl) audioEl.pause();

    if (defaultActionsEl && playerControlsEl) {
        playerControlsEl.classList.add('hidden');
        defaultActionsEl.classList.remove('hidden');
    }
};

window.rewindAudio = function(id) {
    const audioEl = document.getElementById(`audio-${id}`);
    if (audioEl) {
        audioEl.currentTime = 0;
        if (audioEl.paused) audioEl.play().catch(e => console.error(e));
    }
};

window.forwardAudio = function(id) {
    const audioEl = document.getElementById(`audio-${id}`);
    if (audioEl) {
        audioEl.currentTime += 10;
    }
};