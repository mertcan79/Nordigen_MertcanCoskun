
from django.contrib import admin
from django.urls import path, include
from nordigen_project import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name=''),
    path('agreements/<institution_id>', views.agreements, name='agreements'),
    path('results/', views.results, name='results')
]

