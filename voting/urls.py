from django.urls import path
from .views import vote_view

urlpatterns = [
    path('vote/', vote_view, name='vote'),
]
