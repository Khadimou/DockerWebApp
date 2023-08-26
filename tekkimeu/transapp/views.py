from django.shortcuts import render
from .forms import FichierForm, VideoForm, LinkForm
from .models import Fichier
from .utils import transcribe, translate_txt, generate_audio, generate_video, detect_language, transcribe_ytb, translate_txt_ytb, generate_video_ytb
from django.shortcuts import redirect
from django.db.models import Q
import os
from urllib.parse import quote
from pytube import YouTube
from django.http import QueryDict
from django.urls import reverse
from django.conf import settings
import shutil

def link(request):
    if request.method == 'POST':
        #print("Inside POST block")  # Temporary print statement
        form = LinkForm(request.POST, request.FILES)
        if form.is_valid():
            fichier_url = form.cleaned_data['fichier_url']
            choix = form.cleaned_data['choix_link']
            langue = form.cleaned_data['langue_traduction']
            # print("fichier_url:", fichier_url)
            # print("choix:", choix)
            # print("langue:", langue)

            if choix == 'audio':
                print("Inside audio condition", fichier_url)
                yt = YouTube(fichier_url)
                stream = yt.streams.filter(only_audio=True).first()
                # Enregistrer le fichier audio temporaire sur le système de fichiers
                fichier_path = stream.download(output_path='.', filename='tempfile')
                # Traitement pour l'audio à partir du lien YouTube
                texte_traduit = transcribe_ytb(fichier_path)
                text = translate_txt_ytb(texte_traduit, langue)
                audio = generate_audio(text, langue, "translated_audio.mp3")
                fichier_obj = Fichier.objects.create(fichier_audio=audio)
                fichier_obj.save()
                audio_url = fichier_obj.fichier_audio.url

                query_string = QueryDict(mutable=True)
                query_string['audio_url'] = audio_url
                redirect_url = reverse('link_result') + '?' + query_string.urlencode()

                return redirect(redirect_url)

            elif choix == 'video':
                # Supprimer le contenu du répertoire 'media' avant de générer la nouvelle vidéo
                media_path = settings.MEDIA_ROOT
                for filename in os.listdir(media_path):
                    file_path = os.path.join(media_path, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                yt = YouTube(fichier_url)
                stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
                # Enregistrer le fichier audio temporaire sur le système de fichiers
                fichier_path = stream.download(output_path='.', filename='tempfile')
                # Traitement pour la vidéo à partir du lien YouTube
                texte_traduit = transcribe_ytb(fichier_path)
                text = translate_txt_ytb(texte_traduit, langue)

                video = generate_video_ytb(text, langue, fichier_url, "generated_video.mp4")
                fichier_obj = Fichier.objects.create(fichier_video=video)
                fichier_obj.save()
                video_url = fichier_obj.fichier_video.url
                query_string = QueryDict(mutable=True)
                query_string['video_url'] = video_url
                redirect_url = reverse('link_result') + '?' + query_string.urlencode()
                # Déplacer le fichier vidéo généré vers le répertoire MEDIA_ROOT
                shutil.move(video, os.path.join(settings.MEDIA_ROOT))
                return redirect(redirect_url)

            elif choix == 'texte':
                print("Inside texte condition", fichier_url)
                yt = YouTube(fichier_url)
                stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
                # Enregistrer le fichier audio temporaire sur le système de fichiers
                fichier_path = stream.download(output_path='.', filename='tempfile')
                # Traitement pour le texte à partir du lien YouTube
                texte_traduit = transcribe_ytb(fichier_path)
                text = translate_txt_ytb(texte_traduit, langue)
                text_encoded = quote(text)
                redirect_url = reverse('link_result') + f'?texte={text_encoded}'
                return redirect(redirect_url)
        else:
            print("Form errors:", form.errors)
    else:
        form = LinkForm()

    fichier_url = request.POST.get('fichier_url')
    if fichier_url is None:
        fichier_url = ''
    return render(request, 'link.html', {'form': form, 'fichier_url': fichier_url})  # Modification de cette ligne


def link_result(request):
    audio_url = request.GET.get('audio_url')
    video_url = request.GET.get('video_url')
    texte = request.GET.get('texte')

    context = {
        'audio_url': audio_url,
        'video_url': video_url,
        'texte': texte
    }

    return render(request, 'link_result.html', context)

def accueil(request):
    return render(request, 'accueil.html')

def resultat(request):
# Récupérer le texte traduit depuis les paramètres de requête
    texte_traduit = request.GET.get('texte')
    audio_fichiers = Fichier.objects.filter(fichier_audio__isnull=False)
    video_fichiers = Fichier.objects.filter(fichier_video__isnull=False)
    return render(request, 'resultat.html', {'audio_fichiers': audio_fichiers, 'video_fichiers': video_fichiers, 'texte_traduit': texte_traduit})

from django.shortcuts import render

import os
from pytube import YouTube

def detect_lang(request):
    if request.method == 'POST':
        input_type = request.POST.get('input_type')  # Récupérer le type d'entrée choisi

        if input_type == 'file':
            # Récupérer le fichier envoyé par le formulaire
            fichier = request.FILES['fichier']
            # Enregistrer le fichier temporaire sur le système de fichiers
            with open('tempfile', 'wb') as temp_file:
                for chunk in fichier.chunks():
                    temp_file.write(chunk)
            # Obtenir le chemin du fichier temporaire
            fichier_path = os.path.abspath('tempfile')
            langue_detectee = detect_language(fichier_path)
        elif input_type == 'url':
            fichier_url = request.POST.get('fichier_url')  # Récupérer l'URL du fichier

            try:
                yt = YouTube(fichier_url)
                stream = yt.streams.filter(only_audio=True).first()
                # Enregistrer le fichier audio temporaire sur le système de fichiers
                fichier_path = stream.download(output_path='.', filename='tempfile')
                langue_detectee = detect_language(fichier_path)
            except:
                # Gérer le cas où l'URL de la vidéo YouTube est invalide ou le téléchargement échoue
                return render(request, 'invalid_url.html')
        else:
            # Gérer le cas où le type d'entrée n'est pas spécifié ou inconnu
            return render(request, 'invalid_input_type.html')

        # Retourner les résultats ou effectuer une redirection
        return render(request, 'resultats_detect_language.html', {'langue_detectee': langue_detectee})

    return render(request, 'detect_language.html')




def resultats_detect_language(request, resultats):
    return render(request, 'resultats_detect_language.html', {'resultats': resultats})

from django.http import QueryDict
from django.urls import reverse
from django.conf import settings

def delete_old_audio():
    # Chemin complet de l'ancien fichier audio dans le dossier "media"
    file_path = os.path.join(settings.MEDIA_ROOT, "translated_audio.mp3")

    if os.path.exists(file_path):
        os.remove(file_path)

def telechargement_vue(request):
    if request.method == 'POST':
        form = FichierForm(request.POST, request.FILES)
        if form.is_valid():
            fichier = request.FILES['fichier']
            choix = form.cleaned_data['choix']
            langue = form.cleaned_data['langue']  # Récupérer la langue sélectionnée


            if choix == 'audio':
                # Supprimer l'ancien fichier audio s'il existe
                delete_old_audio()
                # Traitement pour le fichier audio
                texte_traduit = transcribe(fichier)
                text = translate_txt(texte_traduit, langue)

                audio = generate_audio(text, langue, "translated_audio.mp3")

                fichier_obj = Fichier.objects.create(fichier_audio=audio)
                fichier_obj.save()

                audio_url = fichier_obj.fichier_audio.url

                query_string = QueryDict(mutable=True)
                query_string['audio_url'] = audio_url
                redirect_url = reverse('resultat') + '?' + query_string.urlencode()

                return redirect(redirect_url)

            elif choix == 'video':

                # Supprimer le contenu du répertoire 'media' avant de générer la nouvelle vidéo
                media_path = settings.MEDIA_ROOT
                for filename in os.listdir(media_path):
                    file_path = os.path.join(media_path, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                # Traitement pour le fichier vidéo
                texte_traduit = transcribe(fichier)
                text = translate_txt(texte_traduit, langue)

                # Enregistrer le fichier vidéo sur le disque
                fichier_video = os.path.join(settings.MEDIA_ROOT,fichier.name)  # Chemin complet du fichier vidéo
                handle_uploaded_file(fichier, fichier_video)  # Utilisez le chemin complet du fichier vidéo


                video = generate_video(text, langue, fichier_video, "generated_video.mp4")

                fichier_obj = Fichier.objects.create(fichier_video=video)
                fichier_obj.save()

                video_url = fichier_obj.fichier_video.url

                query_string = QueryDict(mutable=True)
                query_string['video_url'] = video_url
                redirect_url = reverse('resultat') + '?' + query_string.urlencode()
                # Déplacer le fichier vidéo généré vers le répertoire MEDIA_ROOT
                shutil.move(video, os.path.join(settings.MEDIA_ROOT))

                return redirect(redirect_url)

            elif choix=='texte':
                # Traitement pour le fichier texte
                texte_traduit = transcribe(fichier)
                text = translate_txt(texte_traduit, langue)

                # Passer le texte traduit à la vue resultat en utilisant une redirection
                text_encoded = quote(text)  # Encoder le texte traduit
                redirect_url = reverse('resultat') + f'?texte={text_encoded}'

                return redirect(redirect_url)
    else:
        form = FichierForm()

    return render(request, 'telechargement.html', {'form': form})

def handle_uploaded_file(file, file_path):
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)