from django.urls import path
from . import views

app_name = "process_handling"

urlpatterns = [
    path("process_model_list/", views.process_model_list, name="process_model_list"),
    path("process_model_create/", views.process_model_create, name="process_model_create"),
    path("process_model_update/<str:pk>/", views.process_model_update, name="process_model_update"),
    path("process_model_detail/<str:pk>/", views.process_model_detail, name="process_model_detail"),
    path("process_model_delete/<str:pk>/", views.process_model_delete, name="process_model_delete")

]
