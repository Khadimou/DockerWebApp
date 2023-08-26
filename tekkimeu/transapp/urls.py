from django.urls import path
from transapp import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.accueil, name='accueil'),  # URL pattern pour la page d'accueil
    path('telechargement/', views.telechargement_vue, name='telechargement'),
    path('resultat/', views.resultat, name='resultat'),
    path('link/', views.link, name='link'),
    path('link_result/', views.link_result, name='link_result'),
    path('detect_lang/', views.detect_lang, name='detect_lang'),
    path('resultats_detect_language/<str:resultats>/', views.resultats_detect_language, name='resultats_detect_language'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)