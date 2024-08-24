from django_filters import rest_framework as filters
from .models import Car


class CarFilter(filters.FilterSet):
    price_min = filters.NumberFilter(field_name="price_day", lookup_expr='gte')
    price_max = filters.NumberFilter(field_name="price_day", lookup_expr='lte')
    fuel_type = filters.ChoiceFilter(choices=Car._meta.get_field('fuel_type').choices)
    gearbox = filters.ChoiceFilter(choices=Car._meta.get_field('gearbox').choices)
    year = filters.NumberFilter()

    class Meta:
        model = Car
        fields = ['price_day', 'fuel_type', 'gearbox', 'year']
