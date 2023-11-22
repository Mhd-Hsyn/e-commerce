from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Create a router for the viewset
router = DefaultRouter()
router.register(r"adminauth", AdminAuthViewset, basename="adminauth")
router.register(r"admin", AdminViewset, basename="admin")

urlpatterns = [
    # Include the router-generated URLs
    path("adminapi/", include(router.urls)),
]
