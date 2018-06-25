from django import forms
from decisions.models import Alternative
import django_filters

from decisions.models import Alternative, Mark, Vector

class VectorFilter(django_filters.FilterSet):
    class Meta:
        model = Vector
        fields = ['alternative', 'mark', ]