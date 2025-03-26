"""Файл для обработки запросов."""
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import (
    DetailView,
    ListView,
    CreateView,
    UpdateView,
)
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserChangeForm
from django.db.models import Count
from django.http import Http404
from django.conf import settings

from blog.models import Post, Category, Comment
from .forms import PostForm, CommentForm

User = get_user_model()


def get_base_request(first_reason=False, second_reason=False):
    """Базовая функция, возвращающая кверисет."""
    now = timezone.now()
    post_set = Post.objects.select_related(
        'author', 'location', 'category'
    )
    if first_reason:
        post_set = post_set.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=now,
        )
    if second_reason:
        post_set = post_set.order_by(
            '-pub_date'
        ).annotate(comment_count=Count('comment'))
    return post_set


class PostCreateView(LoginRequiredMixin, CreateView):
    """CBV-класс, создающий публикацию."""
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class ProfileDetailView(ListView):
    """CBV-класс, показывающий данные пользователя."""
    paginate_by = settings.CONST_PAGINATE
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_object()
        return context

    def get_queryset(self):
        user = self.get_object()
        if self.request.user == user:
            queryset = get_base_request(first_reason=False, second_reason=True)
        else:
            queryset = get_base_request(first_reason=True, second_reason=True)

        queryset = queryset.filter(author=user)
        return queryset


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """CBV-класс, меняющий данные пользователя."""
    model = User
    form_class = UserChangeForm
    template_name = "blog/user.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


@login_required
def add_comment(request, post_id):
    """Функция для добавления комментария."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('blog:post_detail', post_id=post.id)


@login_required
def delete_comment(request, post_id, comment_id):
    """Функция для удаления комментария."""
    comment_obj = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    template_name = 'blog/comment.html'
    if comment_obj.author != request.user:
        return redirect('blog:profile', username=request.user.username)

    context = {
        'comment': comment_obj
    }
    if request.method == 'POST':
        comment_obj.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(request, template_name, context)


@login_required
def edit_comment(request, post_id, comment_id):
    """Функция для редактирования комментария."""
    comment_obj = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    if comment_obj.author != request.user:
        return redirect('blog:profile', username=request.user.username)

    form = CommentForm(request.POST or None, instance=comment_obj)
    context = {'form': form, 'comment': comment_obj}
    if form.is_valid():
        form.save()
    return render(request, 'blog/comment.html', context)


class PostDetailView(DetailView):
    """CBV-класс, показывающий данные публикации."""
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        return super().get_queryset().select_related('author', 'category')

    def get_object(self, queryset=None):
        post = super().get_object(queryset)

        is_author = post.author == self.request.user
        is_published = post.is_published
        is_category_published = post.category and post.category.is_published
        is_future_post = post.pub_date > timezone.now()
        last_part_condition = is_category_published or not is_future_post

        if not (is_author or is_published and (last_part_condition)):
            raise Http404("Вы не можете просматривать этот пост.")

        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm(self.request.GET or None)
        context['comments'] = Comment.objects.select_related(
            'author'
        ).order_by('created_at')
        return context


@login_required
def edit_post(request, post_id):
    """Функция для редактирования публикации."""
    post_obj = get_object_or_404(Post, pk=post_id)
    if post_obj.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    form = PostForm(request.POST or None, instance=post_obj)
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', context)


@login_required
def post_delete(request, post_id):
    """Функция для удаления публикации."""
    post_obj = get_object_or_404(
        Post,
        id=post_id,
    )
    template_name = 'blog/create.html'
    if post_obj.author != request.user:
        return redirect('blog:profile', username=request.user.username)

    form = PostForm(instance=post_obj)
    context = {
        'form': form,
        'post': post_obj
    }

    if request.method == 'POST':
        post_obj.delete()
        return redirect('blog:index')
    return render(request, template_name, context)


def paginate_view(request, some_object):
    """Общая функция для пагинации списка объектов."""
    paginator = Paginator(some_object, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj


def index(request):
    """Функция для запроса главной страницы."""
    template_name = 'blog/index.html'
    post_list = get_base_request(first_reason=True, second_reason=True)
    page_obj = paginate_view(request, post_list)
    context = {
        'page_obj': page_obj,
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
    post_list = get_base_request(first_reason=True, second_reason=True).filter(
        category__slug=category_slug
    )
    page_obj = page_obj = paginate_view(request, post_list)
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)
