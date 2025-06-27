from .utils import read_changelog

def footer_version(request):
    current_version = read_changelog()[0]
    return {
        'current_version' : current_version
    }