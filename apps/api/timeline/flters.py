from django_filters import rest_framework as filters

from timeline.models import TimeLine


class TimeLineFilter(filters.FilterSet):
    class Meta:
        model = TimeLine
        fields = ['exact_date']
