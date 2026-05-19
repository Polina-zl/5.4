from django.urls import path
from .views import (
    NewsList, NewsSearch, NewsDetail,
    NewsCreate, NewsUpdate, NewsDelete,
    ArticleCreate, ArticleUpdate, ArticleDelete,
    upgrade_to_author, CategoryDetailView, SubscribeView, UnsubscribeView
)

urlpatterns = [
    path('', NewsList.as_view(), name='news_list'),
    path('search/', NewsSearch.as_view(), name='news_search'),
    path('<int:pk>/', NewsDetail.as_view(), name='news_detail'),
    path('create/', NewsCreate.as_view(), name='news_create'),
    path('<int:pk>/edit/', NewsUpdate.as_view(), name='news_update'),
    path('<int:pk>/delete/', NewsDelete.as_view(), name='news_delete'),
    path('articles/create/', ArticleCreate.as_view(), name='article_create'),
    path('articles/<int:pk>/edit/', ArticleUpdate.as_view(), name='article_update'),
    path('articles/<int:pk>/delete/', ArticleDelete.as_view(), name='article_delete'),
    path('upgrade/', upgrade_to_author, name='upgrade'),
    path('category/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
    path('category/<int:pk>/subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('category/<int:pk>/unsubscribe/', UnsubscribeView.as_view(), name='unsubscribe'),
]