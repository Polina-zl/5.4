from django_filters import FilterSet, CharFilter, DateFilter
from django.forms import DateInput
from .models import Post


class NewsFilter(FilterSet):
    title = CharFilter(lookup_expr='icontains', label='Название')
    author__user__username = CharFilter(lookup_expr='icontains', label='Автор')
    created_at = DateFilter(
        lookup_expr='date__gte',
        label='Новости позже даты',
        widget=DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Post
        fields = ['title', 'author__user__username', 'created_at']