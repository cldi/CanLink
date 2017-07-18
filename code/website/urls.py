from django.conf.urls import url, include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
        url(r'^submit/$', views.index, name="index"),
        # url(r'^submit/$', views.index, name="index"),
        url(r'^thesisSubmission/$', views.thesisSubmission, name="thesisSubmission"),
]

        
