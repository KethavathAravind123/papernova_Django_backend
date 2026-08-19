from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.urls import include

def home(request):
    return JsonResponse({
        "status": "success",
        "message": "PaperNova backend is running"
    })

urlpatterns = [
    path("", home, name="home"),
    path('admin/', admin.site.urls),
    path("api/",include("notifications.urls")),
]
