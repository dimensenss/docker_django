from django.db.models import Prefetch, F, Sum
from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet

from clients.models import Client
from services.models import Subscription
from services.serializers import SubscriptionSerializer


class SubscriptionView(ReadOnlyModelViewSet):
    queryset = Subscription.objects.all().prefetch_related(
        'plan',
        Prefetch('client', queryset=Client.objects.all().select_related('user').only('company_name', 'user__email'))
    ).annotate(
        price=F("service__full_price") - F("service__full_price") * F('plan__discount_percent') / 100.00
    )
    serializer_class = SubscriptionSerializer

    # queryset = Subscription.objects.all().select_related('client', 'client__user', 'plan').only('client__user__email',
    #                                                                                             'client__company_name',
    #                                                                                             'plan_id')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)

        response_data = {'result': response.data,
                         'total_price': queryset.aggregate(total_price=Sum('price')).get('total_price')}
        response.data = response_data
        return response
