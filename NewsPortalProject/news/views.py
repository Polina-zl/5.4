from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from datetime import date
from .models import Post, Category
from .filters import NewsFilter
from .forms import PostForm


class NewsList(ListView):
    model = Post
    ordering = '-created_at'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(post_type='NW').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_count'] = self.get_queryset().count()
        return context


class NewsSearch(ListView):
    model = Post
    ordering = '-created_at'
    template_name = 'news_search.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.filter(post_type='NW').order_by('-created_at')
        self.filterset = NewsFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class NewsDetail(DetailView):
    model = Post
    template_name = 'news_detail.html'
    context_object_name = 'news_item'


class NewsCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'
    permission_required = ('news.add_post',)

    def form_valid(self, form):
        today_posts = Post.objects.filter(
            author=self.request.user.author,
            post_type='NW',
            created_at__date=date.today()
        ).count()

        if today_posts >= 3:
            form.add_error(None, 'Вы не можете публиковать более 3 новостей в сутки')
            return self.form_invalid(form)

        post = form.save(commit=False)
        post.post_type = 'NW'
        post.author = self.request.user.author
        return super().form_valid(form)


class NewsUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'
    permission_required = ('news.change_post',)


class NewsDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'news_delete.html'
    success_url = reverse_lazy('news_list')
    permission_required = ('news.delete_post',)


class ArticleCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'
    permission_required = ('news.add_post',)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'AR'
        post.author = self.request.user.author
        return super().form_valid(form)


class ArticleUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'
    permission_required = ('news.change_post',)


class ArticleDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'news_delete.html'
    success_url = reverse_lazy('news_list')
    permission_required = ('news.delete_post',)


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'category_detail.html'
    context_object_name = 'category'


class SubscribeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        category = get_object_or_404(Category, id=pk)
        if request.user not in category.subscribers.all():
            category.subscribers.add(request.user)
        return redirect('category_detail', pk=pk)


class UnsubscribeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        category = get_object_or_404(Category, id=pk)
        if request.user in category.subscribers.all():
            category.subscribers.remove(request.user)
        return redirect('category_detail', pk=pk)


@login_required
def upgrade_to_author(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
    return redirect('news_list')