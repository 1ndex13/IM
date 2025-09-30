from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('low_stock', 'Низкий запас'),
        ('system', 'Системное'),
        ('alert', 'Важное'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    message = models.TextField(verbose_name='Сообщение')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system',
                                         verbose_name='Тип уведомления')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    related_object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name='ID связанного объекта')
    related_object_type = models.CharField(max_length=100, blank=True, verbose_name='Тип связанного объекта')

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.email}"