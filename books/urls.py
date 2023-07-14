# books/urls.py
from django.urls import path, include

from . import views

urlpatterns = [
    path('GetFile/', views.GetFile.as_view()),
    path('ZipFile/', views.ZipFile.as_view()),
    path('DrawFile/', views.DrawFile.as_view()),
    path('ExcelFile/', views.ExcelFile.as_view()),
    path('ExtractFile/', views.ExtractFile.as_view()),
    path('QueryFile/', views.QueryFile.as_view()),
    path('ClearAction/', views.ClearAction.as_view())
]