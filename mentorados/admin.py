from django.contrib import admin
from .models import Mentorados, Navigators, AgendaReunioes, Reuniao, Tarefas

admin.site.register(Mentorados)
admin.site.register(Navigators)
admin.site.register(AgendaReunioes)
admin.site.register(Reuniao)
admin.site.register(Tarefas)

