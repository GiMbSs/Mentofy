from django.urls import path
from . import views


urlpatterns = [
    path('', views.mentorados, name='mentorados'),
    path('reunioes/', views.reunioes, name='reunioes'),
    path('auth/', views.auth, name="auth_mentorado"),
    path('escolher_dia/', views.escolher_dia, name='escolher_dia'),
    path('agendar_reuniao/', views.agendar_reuniao, name='agendar_reuniao'),
    path('tarefas/<int:id>/', views.tarefas, name='tarefas'),
    path('upload/<int:id>/', views.upload, name='upload'),
    path('excluir_video/<int:id>/', views.excluir_video, name='excluir_video'),
    path('tarefas_mentorado/', views.tarefas_mentorado, name='tarefas_mentorado'),
    path('tarefa_alterar/<int:id>/', views.tarefa_alterar, name='tarefa_alterar'),
    path('cadastro_navigators/', views.cadastro_navigators, name='cadastro_navigators'),
    path('navigators/', views.navigators, name='navigators'),
    path('enviar_token/<int:mentorado_id>/', views.enviar_token_email, name='enviar_token_email'),
    path('excluir_mentorado/<int:mentorado_id>/', views.excluir_mentorado, name='excluir_mentorado'),
    path('excluir_navigator/<int:navigator_id>/', views.excluir_navigator, name='excluir_navigator'),
]
