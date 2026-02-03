/* ==========================================================================
   NEXUS CIENCIA - LÓGICA DE CONTACTO (CONTACT.JS)
   ==========================================================================
   Descripción: Maneja el formulario de contacto y secciones interactivas.
   Funciones:
   - Acordeón para FAQ.
   - Simulación de envío de formulario con feedback visual.
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. LÓGICA DEL ACORDEÓN (FAQ) ---
    const accordionHeaders = document.querySelectorAll('.accordion-header');

    accordionHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const item = header.parentElement;
            
            // Cerrar otros elementos abiertos (Comportamiento de Acordeón estricto)
            document.querySelectorAll('.accordion-item').forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.classList.remove('active');
                }
            });

            // Alternar el elemento actual
            item.classList.toggle('active');
        });
    });

    // --- 2. LÓGICA DEL FORMULARIO ---
    const form = document.getElementById('contactForm');
    const submitBtn = document.getElementById('submitBtn');

    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevenir el envío real para demostración

            // Activar estado de carga
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;

            // Simular petición al servidor (2 segundos)
            setTimeout(() => {
                submitBtn.classList.remove('loading');
                submitBtn.classList.add('success');
                
                // Resetear formulario después del éxito
                setTimeout(() => {
                    form.reset();
                    submitBtn.classList.remove('success');
                    submitBtn.disabled = false;
                    alert('¡Mensaje enviado correctamente! Nos pondremos en contacto pronto.');
                }, 1000);
            }, 2000);
        });
    }
});