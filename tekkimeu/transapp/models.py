from django.db import models
from asgiref.sync import sync_to_async

# Create your models here.

class Fichier(models.Model):
    fichier_audio = models.FileField(upload_to='media/', null=True, blank=True)
    fichier_video = models.FileField(upload_to='media/', null=True, blank=True)
    texte = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Fichier #{self.id}"

