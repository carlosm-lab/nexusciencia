"""
Test de Context Processors - Verifica variables globales de template.
REMEDIACIÓN AUD-001: Convertido de script a test real con fixtures.
"""

import pytest


class TestContextProcessors:
    """Tests para verificar que los context processors inyectan correctamente."""

    def test_todas_las_categorias_en_contexto(self, app):
        """Verifica que 'todas_las_categorias' existe en el contexto de templates."""
        with app.test_request_context():
            processors = app.template_context_processors[None]
            context = {}
            for processor in processors:
                context.update(processor())

            assert 'todas_las_categorias' in context, \
                "todas_las_categorias NO encontrada en context processors"

    def test_context_contiene_variables_esperadas(self, app):
        """Verifica que el context tiene las variables globales esperadas."""
        with app.test_request_context():
            processors = app.template_context_processors[None]
            context = {}
            for processor in processors:
                context.update(processor())

            # Verificar que el context no está vacío
            assert len(context) > 0, "Context processors no inyectaron ninguna variable"
