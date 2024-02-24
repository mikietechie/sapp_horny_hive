from django.urls import path

from sapp_horny_hive.views import space

urlpatterns = [
    path("", space.index_view)
]