import traceback
try:
    import src.sql.templates as t
    print('Loaded OK')
    print('Has SQL_TEMPLATES:', hasattr(t, 'SQL_TEMPLATES'))
    if hasattr(t, 'SQL_TEMPLATES'):
        print('Keys:', list(t.SQL_TEMPLATES.keys()))
except Exception as e:
    traceback.print_exc()
