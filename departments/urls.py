from django.urls import path
from . import views

urlpatterns = [
    path('', views.department_list, name='department_list'),
    path('<int:pk>/', views.department_detail, name='department_detail'),
    path('api/<int:department_id>/categories/', views.get_categories_api, name='get_categories_api'),
]
