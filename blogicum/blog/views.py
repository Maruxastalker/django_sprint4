"""Файл для обработки запросов."""
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from blog.models import Post, Category, Comment
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import PostForm, CommentForm
from django.contrib.auth.forms import UserChangeForm
from django.db.models import Count
from django.http import Http404
from django.views.generic.detail import SingleObjectMixin


User = get_user_model()

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

class PostCreateView(LoginRequiredMixin, CreateView):
    form_class=PostForm
    template_name='blog/create.html'
    
    def get_success_url(self):
        return reverse_lazy('blog:profile',kwargs={'username': self.request.user.username})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_count'] = Comment.objects.count()
        return context
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    
    
class ProfileDetailView(SingleObjectMixin, ListView):
    paginate_by = 10
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'

    def get(self, requerst, *args, **kwargs):
        self.object = self.get_object(queryset=User.objects.all())
        return super().get(requerst, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.object
        return context

    def get_queryset(self):
        return Post.objects.filter(
            author=self.object
        ).order_by('-pub_date').annotate(comment_count=Count('comment'))


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserChangeForm
    template_name = "blog/user.html"
    
    def test_func(self):
        object = self.get_object()
        return object == self.request.user

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_obj"] = Post.objects.filter(author=self.get_object())
        return context
    

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment=form.save(commit=False)
        comment.author = request.user
        comment.post=post
        comment.save()
    
    return redirect('blog:post_detail', post_id=post.id)

@login_required
def delete_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    instance = get_object_or_404(Comment, id=comment_id, post=post)
    comment = get_object_or_404(get_base_request(), id=comment_id)
    template_name = 'blog/comment.html'
    if instance.author != request.user:
        return redirect('blog:profile', username=instance.post.author)
    form=CommentForm(instance=instance)
    context = {
        #'form': form,
        'comment': instance
    }
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:profile', username=post.author.username)
    return render(request, template_name, context)
    
@login_required
def edit_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    instance = get_object_or_404(Comment, pk=comment_id, post=post)
    if instance.author != request.user:
        #return redirect('blog:post_detail', post_id=post_id)
        return redirect('blog:profile', username=instance.post.author)

    form = CommentForm(request.POST or None, instance=instance)
    context = {'form': form, 'comment':instance}
    if form.is_valid():
        form.save()
    return render(request, 'blog/comment.html', context)



def index(request):
    """Функция для запроса главной страницы."""
    template_name = 'blog/index.html'
    post_list = get_base_request().annotate(comment_count=Count('comment')).order_by('-pub_date')
    paginator_index = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator_index.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template_name, context)

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post = super().get_object(queryset)

        if not post.is_published and post.author != self.request.user:
            raise Http404("Вы не можете просматривать этот пост.")
        
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm(self.request.POST or None)
        context['comments'] = Comment.objects.filter(post=self.object).order_by('created_at')
        return context

def edit_post(request, post_id):
    instance = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=instance)
    context = {'form': form}
    if instance.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=instance.author.username)
    return render(request, 'blog/create.html', context)

@login_required
def post_delete(request, post_id):
    instance = get_object_or_404(Post, id=post_id, is_published=True, category__is_published=True)
    post = get_object_or_404(get_base_request(), id=post_id)
    template_name = 'blog/create.html'
    form=PostForm(instance=instance)
    context = {
        'form': form,
        'post': instance
    }
    if instance.author != request.user:
        return redirect('blog:profile', username=instance.author.username)

    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')
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
    ).annotate(comment_count=Count('comment')).order_by('-pub_date')
    paginator_category = Paginator(post_list,10)
    page_number = request.GET.get('page')
    page_obj = paginator_category.get_page(page_number)
    context = {
        'category': category,
        'page_obj': page_obj,   
    }
    return render(request, template_name, context)
