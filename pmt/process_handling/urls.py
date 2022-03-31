from django.urls import path
from . import views

app_name = "process_handling"

urlpatterns = [
    # Crud urls
    path("process_model_list/", views.process_model_list, name="process_model_list"),
    path(
        "process_model_create/", views.process_model_create, name="process_model_create"
    ),
    path(
        "process_model_update/<str:pk>/",
        views.process_model_update,
        name="process_model_update",
    ),
    path(
        "process_model_detail/<str:pk>/",
        views.process_model_detail,
        name="process_model_detail",
    ),
    path(
        "process_model_delete/<str:pk>/",
        views.process_model_delete,
        name="process_model_delete",
    ),
    # Discovery urls
    path(
        "process_model_discover/",
        views.process_model_discover,
        name="process_model_discover",
    ),
    # Statistics urls
    path(
        "performance_dashboard/<str:pk>",
        views.performance_dashboard,
        name="performance_dashboard",
    ),
    path(
        "performance_dashboard_select",
        views.performance_dashboard_select,
        name="performance_dashboard_select",
    ),
    path(
        "social_network_analysis/<str:pk>",
        views.social_network_analysis,
        name="social_network_analysis",
    ),
    path(
        "social_network_analysis_select",
        views.social_network_analysis_select,
        name="social_network_analysis_select",
    ),
]
