from django.urls import path

from .views import bbs, comments, BbDetailView, rubrics

urlpatterns = [
    path('bbs/<int:pk>/comments/', comments),
    path('bbs/<int:pk>', BbDetailView.as_view()),
    path('bbs/', bbs),
    path('rubrics/', rubrics)
]
