from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import JellyfinAccount
from .jellyfin import remove_item_from_playlist, add_items_to_playlist
import json

def configView(request):
    return HttpResponse('<h1>Hello</h1>')

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
