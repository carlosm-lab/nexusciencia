from app import create_app

app = create_app()
with app.app_context():
    with app.test_request_context():
        # Obtener context processor
        processors = app.template_context_processors[None]
        context = {}
        for processor in processors:
            context.update(processor())
        
        print("Context variables:")
        for key, value in context.items():
            print(f"  {key}: {value if not callable(value) else '<function>'}")
        
        if 'todas_las_categorias' in context:
            print(f"\n✅ todas_las_categorias found: {context['todas_las_categorias']}")
        else:
            print("\n❌ todas_las_categorias NOT in context!")
