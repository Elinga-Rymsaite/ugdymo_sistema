"""
URL configuration for jausmukai project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView  # Import RedirectView
from emocijos import views

# jausmukai/urls.py
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from emocijos import views

urlpatterns = [

    path('', RedirectView.as_view(url='pagrindinis', permanent=True)),  # Removed extra single quote
    path('pagrindinis/', views.pagrindinis, name='pagrindinis'),
    path('emociju-atpazinimas/', views.emociju_atpazinimas, name='emociju_atpazinimas'),
    path('valgiu_derinimas/', views.valgiu_derinimas, name='valgiu_derinimas'),
    path('dienos_rezimas/', views.dienos_rezimas, name='dienos_rezimas'),
    path('svaros_zaidimas/', views.svaros_zaidimas, name='svaros_zaidimas'),
    path('veidukas/', views.veidukas, name='veidukas'),
    path('pagrindinis.html', views.pagrindinis, name='pagrindinis_html'),

]