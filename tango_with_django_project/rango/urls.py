from django.conf.urls import url
from rango import views
from django.conf.urls import include

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'about/', views.about, name='about'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),  # Новая строка!
    url(r'^add_category/$', views.add_category, name='add_category'), # НОВОЕ СОПОСТАВЛЕНИЕ!
    url(r'^category/(?P<category_name_slug>[\w\-]+)/add_page/$', views.add_page, name='add_page'),
    #url(r'^register/$', views.register, name='register'), # ДОБАВЛЯЕМ НОВЫЙ ШАБЛОН!
    #url(r'^login/$', views.user_login, name='login'),
    url(r'^restricted/', views.restricted, name='restricted'),
    #url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^accounts/', include('registration.backends.simple.urls'))
]
