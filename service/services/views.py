from django.db.models import Prefetch
from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet

from clients.models import Client
from services.models import Subscription
from services.serializers import SubscriptionSerializer


class SubscriptionView(ReadOnlyModelViewSet):
    queryset = Subscription.objects.all().prefetch_related(
        Prefetch('client', queryset=Client.objects.all().select_related('user').only('company_name', 'user__email'))
    )
    # queryset = Subscription.objects.all().select_related('client', 'client__user', 'plan').only('client__user__email',
    #                                                                                             'client__company_name',
    #                                                                                             'plan_id')

    serializer_class = SubscriptionSerializer
