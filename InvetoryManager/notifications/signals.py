from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from products.models import Product
from .models import Notification

User = get_user_model()


@receiver(post_save, sender=Product)
def check_low_stock(sender, instance, **kwargs):
    if instance.quantity <= instance.min_stock and instance.min_stock > 0:
        admins_managers = User.objects.filter(role__in=['admin', 'manager'])

        for user in admins_managers:
            Notification.objects.create(
                user=user,
                title='Низкий запас товара',
                message=f'Товар "{instance.name}" (артикул: {instance.sku}) достиг минимального запаса. Текущий остаток: {instance.quantity}',
                notification_type='low_stock',
                related_object_id=instance.id,
                related_object_type='product'
            )