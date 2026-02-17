from django.urls import path
from . import views

# This is so i can referecne this function in other templates using 'journals:home'
app_name = 'journals'

urlpatterns = [
    # This calls the home function in views.py in journals app when the root URL is accessed (' ')
    path('', views.home, name='home'), 
    path('listJournals/', views.listJournals, name='listJournals'),
    path('createJournal/', views.createJournal, name='createJournal'),
    path('journal/<int:journal_id>/', views.openJournal, name='openJournal'),
    path('deleteJournal/<int:journal_id>/', views.deleteJournal, name='deleteJournal'),
]