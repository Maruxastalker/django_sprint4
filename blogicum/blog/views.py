"""Файл для обработки запросов."""
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import DetailView, ListView, CreateView
from blog.models import Post, Category
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.urls import reverse_lazy

from .forms import PostForm

User = get_user_model()


class PostCreateView(CreateView):
    form_class=PostForm
    template_name='blog/create.html'
    
    def get_success_url(self):
        return reverse_lazy('profile',kwargs={'username': self.request.user.username})

class ProfileDetailView(DetailView):
    model=User
    template_name='blog/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts_user = Post.objects.filter(author=self.get_object())
        paginator_posts = Paginator(posts_user, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator_posts.get_page(page_number)
        context['profile'] = self.get_object()
        context['page_obj'] = page_obj
        return context


def get_base_request():
    """Базовая функция, возвращающая кверисет."""
    now = timezone.now()
    return Post.objects.select_related(
        'author', 'location', 'category'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=now,
    )


MAX_POSTS_COUNT = 5

def index(request):
    """Функция для запроса главной страницы."""
    template_name = 'blog/index.html'
    post_list = get_base_request().order_by('-pub_date')
    paginator_index = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator_index.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template_name, context)


def post_detail(request, post_id):
    """Функция для запроса страницы с ключом post_id."""
    post = get_object_or_404(get_base_request(), id=post_id)
    template_name = 'blog/detail.html'
    context = {
        'post': post
    }
    return render(request, template_name, context)


def category_posts(request, category_slug):
    """Функция для запроса страницы с ключом category_slug."""
    template_name = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    post_list = get_base_request().filter(
        category__slug=category_slug
    )
    paginator_category = Paginator(post_list,10)
    page_number = request.GET.get('page')
    page_obj = paginator_category.get_page(page_number)
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)
