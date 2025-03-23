from django.urls import path, include, reverse_lazy
from django.views.generic import CreateView,  DetailView
from django.contrib.auth import get_user_model
from django.conf.urls.static import static
from django.conf import settings

from . import views
from .models import Post
from .views import ProfileDetailView, PostCreateView, ProfileUpdateView, PostDetailView


app_name = 'blog'

User = get_user_model()

urlpatterns = [
    path('', views.index, name='index'),
    # PostDetailView.as_view()
    #views.post_detail
    path('posts/<int:post_id>/',PostDetailView.as_view() , name='post_detail'),
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
    path('edit_profile/',
        ProfileUpdateView.as_view(),
        name='edit_profile'
    ),
    path('posts/<int:post_id>/comment/',views.add_comment, name='add_comment'),
    path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:post_id>/delete/', views.post_delete, name='delete_post'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment')
]
