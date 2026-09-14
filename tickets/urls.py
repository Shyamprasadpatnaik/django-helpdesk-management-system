from django.urls import path
from . import views

urlpatterns = [
    path('', views.ticket_list, name='ticket_list'),
    path('create/', views.ticket_create, name='ticket_create'),
    path('<str:ticket_number>/', views.ticket_detail, name='ticket_detail'),
    path('<str:ticket_number>/assign/', views.ticket_assign, name='ticket_assign'),
    path('<str:ticket_number>/accept/', views.ticket_accept, name='ticket_accept'),
    path('<str:ticket_number>/resolve/', views.ticket_resolve, name='ticket_resolve'),
    path('<str:ticket_number>/confirm/', views.ticket_confirm, name='ticket_confirm'),
    path('<str:ticket_number>/reopen/', views.ticket_reopen, name='ticket_reopen'),
    path('<str:ticket_number>/comment/', views.ticket_comment_add, name='ticket_comment_add'),
]
