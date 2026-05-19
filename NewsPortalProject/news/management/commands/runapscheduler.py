import logging
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from news.models import Category, Post

logger = logging.getLogger(__name__)


def send_weekly_newsletter():
    """
    Отправляет еженедельную рассылку новостей подписчикам категорий
    """
    week_ago = timezone.now() - timedelta(days=7)
    categories = Category.objects.all()

    for category in categories:
        new_posts = category.post_set.filter(created_at__gte=week_ago)
        if not new_posts.exists():
            continue

        # Формируем список статей для рассылки
        posts_html = '<ul>'
        for post in new_posts:
            posts_html += f'<li><a href="http://127.0.0.1:8000/news/{post.id}/">{post.title}</a> - {post.preview()}</li>'
        posts_html += '</ul>'

        for subscriber in category.subscribers.all():
            send_mail(
                subject=f'Новые статьи в категории "{category.name}" за неделю',
                message=f'Здравствуй, {subscriber.username}!\n\n'
                        f'За прошедшую неделю в категории "{category.name}" появились новые статьи:\n\n'
                        f'Читать полностью: http://127.0.0.1:8000/news/',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscriber.email],
                fail_silently=True,
                html_message=f'<h2>Здравствуй, {subscriber.username}!</h2>'
                             f'<p>За прошедшую неделю в категории "{category.name}" появились новые статьи:</p>'
                             f'{posts_html}'
                             f'<p><a href="http://127.0.0.1:8000/news/">Перейти на портал</a></p>',
            )


def delete_old_job_executions(max_age=604_800):
    """Удаляет старые записи о выполнении задач"""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Запускает планировщик задач"

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            send_weekly_newsletter,
            trigger=CronTrigger(day_of_week="mon", hour="09", minute="00"),  # Каждый понедельник в 9:00
            id="weekly_newsletter",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'weekly_newsletter'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: 'delete_old_job_executions'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")