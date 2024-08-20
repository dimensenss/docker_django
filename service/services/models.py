from django.conf import settings
from django.core.cache import cache
from django.core.validators import MaxValueValidator
from django.db import models, transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from clients.models import Client
from services.tasks import set_sub_price, set_comment


class Service(models.Model):
    name = models.CharField(max_length=100)
    full_price = models.PositiveIntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__full_price = self.full_price

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.full_price != self.__full_price:
            for subscription in self.subscriptions.all():
                set_sub_price.delay(subscription.id)
                set_comment.delay(subscription.id)


class Plan(models.Model):
    PLAN_TYPES = (
        ('full', 'Full'),
        ('student', 'Student'),
        ('discount', 'Discount')
    )
    plan_type = models.CharField(choices=PLAN_TYPES, max_length=20)
    discount_percent = models.IntegerField(default=0, validators=[MaxValueValidator(100)])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__discount_percent = self.discount_percent

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.discount_percent != self.__discount_percent:
            for subscription in self.subscriptions.all():
                set_sub_price.delay(subscription.id)
                set_comment.delay(subscription.id)


class Subscription(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='subscriptions')
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='subscriptions')
    price = models.PositiveIntegerField(default=0)
    comment = models.CharField(max_length=100, default='', db_index=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__plan = self.plan

    def save(self, *args, **kwargs):
        creating = not self.pk

        result = super().save(*args, **kwargs)
        if creating or self.plan != self.__plan:
            set_sub_price.delay(self.id)
        return result

    def delete(self, **kwargs):
        cache.delete(settings.PRICE_CACHE_NAME)
        super().delete(**kwargs)


# @receiver(post_delete, sender=Subscription)
# def delete_sub_price(sender, instance, **kwargs):
#     cache.delete(settings.PRICE_CACHE_NAME)
