from django.urls import path

from .views import AboutTemplateView, RulesTemplateView

app_name = 'pages'

urlpatterns = [
    # path('about/', views.about, name='about'),
    # path('rules/', views.rules, name='rules'),
    path('about/', AboutTemplateView.as_view(), name='about'),
    path('rules/', RulesTemplateView.as_view(), name='rules'),
]
