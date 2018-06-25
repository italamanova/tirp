"""tipr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path, include
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


from decisions.forms import CustomAuthForm


urlpatterns = [
    url(
        r'^$',
        auth_views.login,
        kwargs={
            'authentication_form': CustomAuthForm,
            'template_name': 'registration/login.html'
        },
        name='login'
    ),

    url(
        r'^logout/$',
        auth_views.logout,
        kwargs={'next_page': '/'},
        name='logout'
    ),

    path('admin/', admin.site.urls),
    url(r'decisions/', include('decisions.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Site for decisions"
admin.site.site_title = "TIPR project"