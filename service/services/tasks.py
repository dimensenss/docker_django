import datetime
import time

from celery import shared_task
from celery_singleton import Singleton
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import F


@shared_task(base=Singleton)
def set_sub_price(subscription_id):
    from services.models import Subscription
    # если работаем с разними полями одной модели можно ипоьзовать update_fields без транзакции и select_for_update
    subscription = Subscription.objects.filter(id=subscription_id).annotate(
        annotated_price=F('service__full_price') - F('service__full_price') * F('plan__discount_percent') / 100.00
    )[0]
    subscription.price = subscription.annotated_price
    subscription.save(update_fields=['price'])

    cache.delete(settings.PRICE_CACHE_NAME)


@shared_task(base=Singleton)
def set_comment(subscription_id):
    from services.models import Subscription

    subscription = Subscription.objects.get(id=subscription_id)
    subscription.comment = str(datetime.datetime.now())
    subscription.save(update_fields=['comment'])

    cache.delete(settings.PRICE_CACHE_NAME)