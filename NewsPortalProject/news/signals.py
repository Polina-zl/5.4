from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Post, Category


@receiver(m2m_changed, sender=Post.categories.through)
def notify_subscribers_on_new_post(sender, instance, action, **kwargs):
    """
    Когда пост добавляется в категорию, отправляем письма всем подписчикам этой категории
    """
    if action == 'post_add':
        categories = instance.categories.all()
        for category in categories:
            subscribers = category.subscribers.all()
            for subscriber in subscribers:
                send_mail(
                    subject=f'Новая статья: {instance.title}',
                    message=f'Здравствуй, {subscriber.username}. Новая статья в твоём любимом разделе "{category.name}"!\n\n'
                            f'{instance.preview()}\n\n'
                            f'Читать полностью: http://127.0.0.1:8000/news/{instance.id}/',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscriber.email],
                    fail_silently=True,
                )