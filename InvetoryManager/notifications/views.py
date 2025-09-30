from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification
from django.core.paginator import Paginator


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    if request.method == 'GET' and 'mark_read' in request.GET:
        unread_notifications = notifications.filter(is_read=False)
        unread_notifications.update(is_read=True)

    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'notifications/notification_list.html', {
        'notifications': page_obj
    })


@login_required
def mark_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect('notifications:list')


@login_required
def mark_all_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect('notifications:list')


@login_required
def get_unread_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})