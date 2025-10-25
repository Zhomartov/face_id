from django.urls import path
from .views import Home_view , Video_stream , check_recognition, Add_view , Class_view

urlpatterns = [
    path('' , Home_view.as_view() , name='home'),
    path('video' , Video_stream.as_view() , name='video'),
    path('verifyed' , check_recognition , name='check'),
    path('class' , Class_view.as_view() , name='class'),
    path('add' , Add_view.as_view() , name='add'),
]
