/* ==========================================================================
   NEXUS CIENCIA - SOLICITUD DE ARTÍCULO (REQUEST.JS)
   ==========================================================================
   Descripción: Interactividad para la página de sugerencias.
   Funciones:
   - Acordeón FAQ específico de solicitudes.
   - Simulación de envío de solicitud.
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. ACORDEÓN ---
    const accordionHeaders = document.querySelectorAll('.accordion-header');

    accordionHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const item = header.parentElement;
            
            // Cerrar otros
            document.querySelectorAll('.accordion-item').forEach(otherItem => {
                if (otherItem !== item) otherItem.classList.remove('active');
            });
            
            // Alternar actual
            item.classList.toggle('active');
        });
    });

    // --- 2. FORMULARIO DE SOLICITUD ---
    const form = document.getElementById('requestForm');
    const submitBtn = document.getElementById('submitBtn');

    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Estado Loading
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;

            // Simulación
            setTimeout(() => {
                submitBtn.classList.remove('loading');
                submitBtn.classList.add('success');
                
                setTimeout(() => {
                    form.reset();
                    submitBtn.classList.remove('success');
                    submitBtn.disabled = false;
                    alert('¡Solicitud enviada! Analizaremos tu propuesta.');
                }, 1500);
            }, 2000);
        });
    }
});