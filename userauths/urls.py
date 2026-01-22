from django.urls import path
from userauths import views

app_name = "userauths"

urlpatterns = [
    path("register_page/",views.register_page, name= "register_page"),
    path("login_page/", views.login_page,name ="login_page"),
    path("logout/", views.logout_page,name ="logout"),
]
