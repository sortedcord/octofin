from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import JellyfinAccount, AppConfig
from .jellyfin import remove_item_from_playlist, add_items_to_playlist, sync_playlist_for_account
import json
from django.shortcuts import render, redirect
from .forms import JellyfinAccountForm, AccountToggleForm


def configView(request):
    accounts = JellyfinAccount.objects.all()
    account_form = JellyfinAccountForm(request.POST or None)
    toggle_form = AccountToggleForm(request.POST or None)
    
    if request.method == 'POST':
        if 'add_account' in request.POST and account_form.is_valid():
            account_form.save()
            return redirect('likedplaylist-config')
        
        if 'toggle_account' in request.POST and toggle_form.is_valid():
            account_id = toggle_form.cleaned_data['account_id']
            is_active = toggle_form.cleaned_data['is_active']
            account = JellyfinAccount.objects.get(id=account_id)
            account.is_active = is_active
            account.save()
            return redirect('likedplaylist-config')
        
        if 'sync_account' in request.POST:
            account_id = request.POST.get('account_id')
            account = JellyfinAccount.objects.get(id=account_id)
            config = AppConfig.get_config()
            sync_playlist_for_account(account, config)
            return redirect('likedplaylist-config')
        
        if 'sync_all' in request.POST:
            config = AppConfig.get_config()
            for account in accounts.filter(is_active=True):
                sync_playlist_for_account(account, config)
            return redirect('likedplaylist-config')
    
    return render(request, 'likedplaylist/config.html', {
        'accounts': accounts,
        'account_form': account_form,
        'toggle_form': toggle_form
    })

@csrf_exempt
def jellyfin_webhook(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        print(data)
        user_id = data.get('user_id').replace('-','')
        item_id = data.get('item_id').replace('-', '')
        save_reason = data.get('saveReason')
        
        if not all([user_id, item_id, save_reason]):
            return JsonResponse({"error": "Missing parameters"}, status=400)
        
        try:
            account = JellyfinAccount.objects.get(user_id=user_id)
        except JellyfinAccount.DoesNotExist:
            print("Account not found")
            return JsonResponse({"error": "Account not found"}, status=404)
        
        if save_reason == 'Unsave':
            remove_item_from_playlist(account, account.liked_playlist_id, item_id)
        else:  # 'Save'
            add_items_to_playlist(account, account.liked_playlist_id, [item_id])
        
        return JsonResponse({"status": "success"})
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
