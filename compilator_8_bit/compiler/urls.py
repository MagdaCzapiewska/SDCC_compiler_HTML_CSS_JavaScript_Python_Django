from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("error", views.error, name="error-page"),
    path("folder/<int:id>/add-folder", login_required(views.AddFolder.as_view()), name="add-folder"),
    path("folder/<int:id>/delete", login_required(views.DeleteFolder.as_view()), name="delete-folder"),
    path("folder/<int:id>/add-file", login_required(views.AddFile.as_view()), name="add-file"),
    path("file/<int:id>/delete-section/<int:start_line>/<int:end_line>", login_required(views.DeleteSection.as_view()), name="delete-section"),
    path("file/<int:id>/create-section/<int:start_line>/<int:end_line>/<str:section_name>", views.create_section, name="create-section"),
    path("file/<int:id>/delete", login_required(views.DeleteFile.as_view()), name="delete-file"),
    path("file/<int:id>/parse", views.parse_file, name="parse-file"),
    path("file/<int:id>", views.view_file, name="file"),
    path("compile", login_required(views.Compile.as_view()), name="compile"),
    path("login", auth_views.LoginView.as_view(template_name="compiler/login.html"), name="login"),
    path("logout", views.logout_view, name="logout")
]