from django.shortcuts import render, redirect
from .models import GlobalConfig

# config/views.py
def settings_view(request):
    context = {
        'po_token': GlobalConfig.objects.get_value('PO_TOKEN', ''),
        'cookies_path': GlobalConfig.objects.get_value('COOKIES_PATH', ''),
        'output_dir': GlobalConfig.objects.get_value('OCTO_OUTPUT_DIR', '/music'),
        # Other values...
    }
    return render(request, 'config/settings.html', context)

