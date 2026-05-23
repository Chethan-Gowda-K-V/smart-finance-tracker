from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from .models import Notification

@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(user=request.user)
    unread_only = request.GET.get('unread_only', 'false').lower() == 'true'
    if unread_only:
        notifications = notifications.filter(is_read=False)
        
    data = []
    for n in notifications[:20]: # Limit to last 20
        data.append({
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'type': n.type,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%Y-%m-%d %H:%M')
        })
    return JsonResponse({'notifications': data})

@login_required
@require_POST
def mark_as_read(request, pk):
    notification = get_object_or_404(Notification, id=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success', 'message': 'Notification marked as read'})

@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success', 'message': 'All notifications marked as read'})
