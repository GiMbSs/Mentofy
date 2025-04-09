from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
import secrets

class Navigators(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, null=True, blank=True)
    telefone = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome

class Mentorados(models.Model):
    estagios = [
        ('E1', '10k-50k'),
        ('E2', '50k-100k'),
        ('E3', '100k-200k'),
        ('E4', '200k-500k'),
        ('E5', '500k-1M'),
    ]
    nome = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    telefone = models.CharField(max_length=255, null=True, blank=True)
    estagio = models.CharField(max_length=3, choices=estagios)
    foto = models.ImageField(upload_to='fotos', null=True, blank=True)
    navigator = models.ForeignKey(Navigators, null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=16)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.gerar_token()
        super().save(*args, **kwargs)

    def gerar_token(self):
        while True:
            token = secrets.token_urlsafe(8)
            if not Mentorados.objects.filter(token=token).exists():
                return token

    def __str__(self):
        return self.nome


class AgendaReunioes(models.Model):
    data_inicial = models.DateTimeField(null=True, blank=True)
    mentor = models.ForeignKey(User, on_delete=models.CASCADE)
    agendado = models.BooleanField(default=False)

    @property
    def data_final(self):
        return self.data_inicial + timedelta(minutes=50)
    
class Reuniao(models.Model):
    tag_choices = (
        ('G', 'Gestão'),
        ('M', 'Marketing'),
        ('RH', 'Gestão de pessoas'),
        ('I', 'Impostos')
    )

    data = models.ForeignKey(AgendaReunioes, on_delete=models.CASCADE)
    mentorado = models.ForeignKey(Mentorados, on_delete=models.CASCADE)
    tag = models.CharField(max_length=2, choices=tag_choices)
    descricao = models.TextField()

class Tarefas(models.Model):
    mentorado = models.ForeignKey(Mentorados, on_delete=models.DO_NOTHING)
    tarefa = models.CharField(max_length=255)
    realizada = models.BooleanField(default=False)


class Upload(models.Model):
    mentorado = models.ForeignKey(Mentorados, on_delete=models.DO_NOTHING)
    video = models.FileField(upload_to='video')
    data_upload = models.DateTimeField(auto_now_add=True)
