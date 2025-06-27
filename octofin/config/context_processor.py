# config/context_processors.py
from .utils import get_config

def global_config(request):
    return {
        'SITE_NAME': get_config('SITE_NAME', 'Octofin'),
        'FOOTER_TEXT': get_config('FOOTER_TEXT', ''),
        # Add other frequently accessed configs here
    }
