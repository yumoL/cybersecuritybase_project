from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login_user'),
	path('logout/', LogoutView.as_view(next_page='/login/')),
    path('sendmail/',views.send_mail, name='send_mail'),
    path('admin/', views.admin_view, name='admin'),
    path('remove/', views.remove_user, name='remove_user')
]