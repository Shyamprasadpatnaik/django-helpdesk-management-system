import os
import sys
from pathlib import Path

# Add project root directory to sys.path so all Django apps are resolvable by Vercel serverless functions
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
app = application

# If running in Vercel serverless environment and using SQLite, auto-initialize DB tables & seed data on first run
if os.environ.get('VERCEL'):
    import tempfile
    tmp_dir = Path(tempfile.gettempdir())
    flag_file = tmp_dir / '.db_initialized'
    if not flag_file.exists():
        from django.core.management import call_command
        try:
            call_command('migrate', interactive=False)
            seed_path = BASE_DIR / 'seed_data.json'
            if seed_path.exists():
                call_command('loaddata', str(seed_path))
            flag_file.touch()
        except Exception as e:
            print(f"Vercel auto-initialization error: {e}")
