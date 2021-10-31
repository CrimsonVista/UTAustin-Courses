from django.urls import path
# Import our views
from . import views
# When we request home/index url it use index view logic
urlpatterns = [
    path('',views.index,name='index')
]
