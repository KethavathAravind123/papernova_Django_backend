from django.urls import path
from . import views

urlpatterns = [

    path("test-email/",views.test_email,name="test_email"),
    path("test-firebase/",views.test_firebase , name="test_firebase"),
    path("notify-paper/",views.notify_paper_uploaded,name="notify_users"),

]