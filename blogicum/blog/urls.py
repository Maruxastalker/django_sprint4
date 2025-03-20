from django.urls import path, include, reverse_lazy
from django.views.generic import CreateView,  DetailView
from django.contrib.auth import get_user_model

from . import views
from .models import Post
from .views import ProfileDetailView, PostCreateView

app_name = 'blog'

User = get_user_model()

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'
    ),
    path('posts/create/', PostCreateView.as_view(), name='create_post'),
    path('profile/<str:username>/',
        ProfileDetailView.as_view(),
        name='profile'
    ),
    
]
