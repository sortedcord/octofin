from django.shortcuts import render, redirect
from django.contrib import messages
from .models import GlobalConfig

def settings_view(request):
    if request.method == 'POST':
        # Handle main configuration form
        if 'form_type' in request.POST and request.POST['form_type'] == 'main_config':
            for key, value in request.POST.items():
                if key in ['csrfmiddlewaretoken', 'form_type']:
                    continue

                try:
                    setting = GlobalConfig.objects.get(key=key)
                    if setting.config_type == 'bool':
                        setting.value = 'true' if value == 'on' else 'false'
                    else:
                        setting.value = value
                    setting.save()
                except GlobalConfig.DoesNotExist:
                    pass
            messages.success(request, 'Settings saved successfully!')

        # Handle server connection form
        elif 'form_type' in request.POST and request.POST['form_type'] == 'server_config':
            server_url = request.POST.get('server_url')
            api_key = request.POST.get('api_key')
            # Add your server connection logic here
            messages.success(request, 'Server connection updated successfully!')

        return redirect('config-settings')

    # Prepare context for GET request
    _settings = GlobalConfig.objects.all()
    settings = {}
    for setting in _settings:
        if setting.group not in settings:
            settings[setting.group] = [setting]
        else:
            settings[setting.group].append(setting)

    context = {
        'settings': settings,
        'server_url': '',  # Replace with actual value
        'api_key': ''      # Replace with actual value
    }
    return render(request, 'config/settings.html', context)
