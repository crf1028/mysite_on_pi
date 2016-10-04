"""ourcase URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import view


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^hello/$', view.hello),
    url(r'^$', view.home),
    url(r'^home/$', view.home),
    url(r'^mcq_home/$',view.mcq_home),
    url(r'^mcq/(\d{1,3})/$', view.mcqs),
    url(r'^test_mcq/(\d{1,3})/$', view.test_mcqs),
    url(r'^pdo/', view.pdo),
    url(r'^json_r/', view.json_receive),
    url(r'^wechat/test/$', view.wechat_test),
]

if settings.DEBUG and settings.STATIC_ROOT:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
