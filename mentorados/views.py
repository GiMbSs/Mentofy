from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Mentorados, Navigators, AgendaReunioes, Reuniao, Tarefas, Upload
from django.contrib import messages
from datetime import datetime, timedelta
from .auth import valida_token
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os


@login_required
def mentorados(request):
    
    if request.method == 'GET':
        mentorados = Mentorados.objects.filter(user=request.user)
        navigators = Navigators.objects.filter(user=request.user)

        mentorados_flat = [i[1] for i in Mentorados.estagios]
        qtd_estagios = []
        for i, j in Mentorados.estagios:
            x = Mentorados.objects.filter(estagio=i).filter(user=request.user).count()
            qtd_estagios.append(x)
            
        return render(request, 'mentorados.html', {
            'estagios': Mentorados.estagios,
            'navigators': navigators,
            'mentorados': mentorados,
            'estagios_flat': json.dumps(mentorados_flat),
            'qtd_estagios': json.dumps(qtd_estagios)
        })
    
    else:
        nome = request.POST.get('nome')
        if not nome:
            messages.error(request, 'Nome é obrigatório')
            return redirect('mentorados')
        email = request.POST.get('email')
        if not email:
            messages.error(request, 'Email é obrigatório')
            return redirect('mentorados')
        telefone = request.POST.get('telefone')
        if len(telefone) < 10 or len(telefone) > 15:
            messages.error(request, 'Telefone inválido')
            return redirect('mentorados')
        telefone = ''.join(filter(str.isdigit, telefone))
        foto = request.FILES.get('foto')
        estagio = request.POST.get('estagio')
        navigator = request.POST.get('navigator')

        mentorado = Mentorados(
            nome=nome,
            foto=foto,
            email=email,
            telefone=telefone,
            estagio=estagio,
            navigator_id=navigator,
            user=request.user
        )
        
        # Ensure token is generated by explicitly calling save()
        mentorado.save()

        messages.success(request, 'Mentorado cadastrado com sucesso.')
        return redirect('mentorados')

@login_required
def reunioes(request):
    if request.method == 'GET':
        # Buscar todas as reuniões agendadas pelos mentorados deste mentor
        reunioes = Reuniao.objects.filter(
        data__mentor=request.user
        ).select_related('mentorado', 'data', 'data__mentor')
        
        return render(request, 'reunioes.html', {'reunioes': reunioes})
    elif request.method == 'POST':
        data = request.POST.get('data')
        data = datetime.strptime(data, '%Y-%m-%dT%H:%M')

        disponibilidade = AgendaReunioes.objects.filter(mentor=request.user).filter(data_inicial__gte=(data - timedelta(hours=1))).filter(data_inicial__lte=(data + timedelta(hours=1)))
        if disponibilidade.exists():
            messages.error(request, 'Você já possui reunião agendada nesse horário')
            return redirect('reunioes')
        disponibilidade = AgendaReunioes(
            data_inicial = data,
            mentor = request.user
        )
        disponibilidade.save()
        messages.success(request, 'Reunião agendada com sucesso')
        return redirect('reunioes')
    return render(request, 'reunioes.html')

def auth(request):
    if request.method == 'GET':
        return render(request, 'auth_mentorado.html')
    else:
        token = request.POST.get('token')

        if not Mentorados.objects.filter(token=token).exists():
            messages.error(request, 'Token inválido')
            return redirect('auth_mentorado')
        
        response = redirect('escolher_dia')
        response.set_cookie('auth_token', token, max_age=3600)
        return response


def escolher_dia(request):
    if not valida_token(request.COOKIES.get('auth_token')):
        return redirect('auth_mentorado')
    mentorado = valida_token(request.COOKIES.get('auth_token'))
    if request.method == 'GET':
        disponibilidades = AgendaReunioes.objects.filter(
            data_inicial__gte=datetime.now(),
            agendado=False
        ).values_list('data_inicial', flat=True)
        
        # Dicionários para tradução de dias e meses
        dias_semana = {
            0: 'Segunda-feira',
            1: 'Terça-feira',
            2: 'Quarta-feira',
            3: 'Quinta-feira',
            4: 'Sexta-feira',
            5: 'Sábado',
            6: 'Domingo'
        }
        
        meses = {
            1: 'Janeiro',
            2: 'Fevereiro',
            3: 'Março',
            4: 'Abril',
            5: 'Maio',
            6: 'Junho',
            7: 'Julho',
            8: 'Agosto',
            9: 'Setembro',
            10: 'Outubro',
            11: 'Novembro',
            12: 'Dezembro'
        }
        # Usar um dicionário para agrupar datas iguais
        datas_formatadas_dict = {}
        
        #Caso não haja datas disponíveis, exibir mensagem informativa
        if not disponibilidades.exists():
            return render(request, 'escolher_dia.html', {'datas': [], 'mentorado': mentorado})

        for data in disponibilidades:
            # Converter para data (ignorando o horário)
            data_sem_hora = data.date()
            
            # Se a data já não existe no dicionário, adiciona
            if data_sem_hora not in datas_formatadas_dict:
                dia_semana = dias_semana[data.weekday()]
                mes = meses[data.month]
                dia = data.day
                ano = data.year
                
                # Formato: "Segunda-feira, 15 de Abril de 2024"
                data_formatada = f"{dia_semana}, {dia} de {mes} de {ano}"
                datas_formatadas_dict[data_sem_hora] = {
                    'data_formatada': data_formatada,
                    'data_original': data_sem_hora.strftime('%d-%m-%Y')
                }
        
        # Converter o dicionário para lista e ordenar
        datas_formatadas = list(datas_formatadas_dict.values())
        datas_formatadas.sort(key=lambda x: x['data_original'])
        print(mentorado)
        return render(request, 'escolher_dia.html', {'datas': datas_formatadas, 'mentorado': mentorado})

def agendar_reuniao(request):
    if not valida_token(request.COOKIES.get('auth_token')):
        return redirect('auth_mentorado')
    mentorado = valida_token(request.COOKIES.get('auth_token'))

    if request.method == 'GET':
        data = request.GET.get("data")
        try:
            data = datetime.strptime(data, '%d-%m-%Y')
        except ValueError:
            messages.error(request, 'Formato de data inválido!')
            return redirect('escolher_dia')
        horarios = AgendaReunioes.objects.filter(
            data_inicial__gte=data,
            data_inicial__lt=data + timedelta(days=1),
            agendado=False
        )
        
        return render(request, 'agendar_reuniao.html', {'horarios': horarios, 'tags': Reuniao.tag_choices, 'reunioes': reunioes})
    elif request.method == 'POST':
        horario_id = request.POST.get('horario')
        tag = request.POST.get('tag')
        descricao = request.POST.get('descricao')
        
        # Obter o objeto AgendaReunioes
        horario = AgendaReunioes.objects.get(id=horario_id)
        
        reuniao = Reuniao(
            mentorado = mentorado,
            data = horario,
            tag = tag,
            descricao = descricao
        )
        
        # Marcar o horário como agendado
        horario.agendado = True
        horario.save()
        
        reuniao.save()
        messages.success(request, 'Reunião agendada com sucesso')
        return redirect('escolher_dia')


@login_required
def tarefas(request, id):
    mentorado = Mentorados.objects.get(id=id)
    if mentorado.user != request.user:
        raise Http404()
    
    if request.method == 'GET':
        tarefas = Tarefas.objects.filter(mentorado=mentorado)
        videos = Upload.objects.filter(mentorado=mentorado)
        return render(request, 'tarefas.html', {'mentorado': mentorado, 'tarefas': tarefas, 'videos': videos})
    
    else:
        tarefa = request.POST.get('tarefa')
        if tarefa:
            t = Tarefas(
                mentorado=mentorado,
                tarefa=tarefa,
            )
            t.save()
            messages.success(request, 'Tarefa adicionada com sucesso')
            return redirect(f'/mentorados/tarefas/{mentorado.id}')
        
        return redirect(f'/mentorados/tarefas/{mentorado.id}')

@login_required
def upload(request, id):
    mentorado = Mentorados.objects.get(id=id)
    if mentorado.user != request.user:
        raise Http404()
    
    video = request.FILES.get('video')
    upload = Upload(
        mentorado=mentorado,
        video=video
    )
    upload.save()
    messages.success(request, 'Vídeo enviado com sucesso')
    return redirect(f'/mentorados/tarefas/{mentorado.id}')

@login_required
def excluir_video(request, id):
    try:
        video = Upload.objects.get(id=id)
    except Upload.DoesNotExist:
        raise Http404()
    mentorado = video.mentorado
    
    # Verificar se o usuário tem permissão para excluir o vídeo
    if mentorado.user != request.user:
        raise Http404()
    
    # Excluir o arquivo físico
    if video.video:
        if os.path.isfile(video.video.path):
            os.remove(video.video.path)
    
    # Excluir o registro do banco de dados
    video.delete()
    
    messages.success(request, 'Vídeo excluído com sucesso')
    return redirect(f'/mentorados/tarefas/{mentorado.id}')
    
    
def tarefas_mentorado(request):
    mentorado = valida_token(request.COOKIES.get('auth_token'))
    if not mentorado:
        return redirect('auth_mentorado')
    
    if request.method == 'GET':
        videos = Upload.objects.filter(mentorado=mentorado)
        tarefas = Tarefas.objects.filter(mentorado=mentorado)
        return render(request, 'tarefas_mentorado.html', {'mentorado': mentorado, 'videos': videos, 'tarefas': tarefas})

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

@csrf_exempt
def tarefa_alterar(request, id):
    mentorado = valida_token(request.COOKIES.get('auth_token'))
    if not mentorado:
        return redirect('auth_mentorado')

    tarefa = Tarefas.objects.get(id=id)
    if mentorado != tarefa.mentorado:
        raise Http404()
    tarefa.realizada = not tarefa.realizada
    tarefa.save()
    return HttpResponse('teste')

@login_required
def cadastro_navigators(request):
    if request.method == 'GET':
        return render(request, 'cadastro_nav.html')
    
    elif request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        if not email:
            email = None
        telefone = request.POST.get('telefone')
        if telefone:
            if len(telefone) < 10 or len(telefone) > 15:
                messages.error(request, 'Telefone inválido')
                return redirect('cadastro_navigators')
            telefone = ''.join(filter(str.isdigit, telefone))
        else:
            telefone = None

        if not nome:
            messages.error(request, 'O nome é obrigatório')
            return redirect('cadastro_navigators')
        
        try:
            navigator = Navigators.objects.create(
                nome=nome,
                email=email,
                telefone=telefone,
                user=request.user
            )
            messages.success(request, 'Navigator cadastrado com sucesso!')
            return redirect('mentorados')
        except Exception as e:
            messages.error(request, 'Erro ao cadastrar navigator')
            return redirect('cadastro_navigators')

@login_required
def navigators(request):
        
    navigators = Navigators.objects.filter(user=request.user)
    # For each navigator, fetch the associated mentorados
    navigators_data = []
    for navigator in navigators:
        mentorados = Mentorados.objects.filter(navigator=navigator)
        navigators_data.append({
            'navigator': navigator,
            'mentorados': mentorados
        })
    print(navigators_data)
    return render(request, 'navigators.html', {'navigators_data': navigators_data})

from django.core.mail import send_mail
from django.conf import settings

@login_required
def excluir_mentorado(request, mentorado_id):
    try:
        mentorado = Mentorados.objects.get(id=mentorado_id, user=request.user)
    except Mentorados.DoesNotExist:
        raise Http404()

    # Excluir tarefas relacionadas
    Tarefas.objects.filter(mentorado=mentorado).delete()
    
    # Excluir vídeos e arquivos físicos
    videos = Upload.objects.filter(mentorado=mentorado)
    for video in videos:
        if video.video and os.path.isfile(video.video.path):
            os.remove(video.video.path)
    videos.delete()
    
    # Excluir reuniões agendadas
    Reuniao.objects.filter(mentorado=mentorado).delete()
    
    # Excluir mentorado
    mentorado.delete()
    
    messages.success(request, 'Mentorado e todos os dados relacionados foram excluídos com sucesso')
    return redirect('mentorados')

@login_required
def excluir_navigator(request, navigator_id):
    try:
        navigator = Navigators.objects.get(id=navigator_id, user=request.user)
    except Navigators.DoesNotExist:
        raise Http404()

    # Verificar se há mentorados associados
    if Mentorados.objects.filter(navigator=navigator).exists():
        messages.error(request, 'Não é possível excluir um Navigator com mentorados associados')
        return redirect('navigators')

    # Excluir navigator
    navigator.delete()
    
    messages.success(request, 'Navigator excluído com sucesso')
    return redirect('navigators')

@login_required
def enviar_token_email(request, mentorado_id):
    
    try:
        mentorado = Mentorados.objects.get(id=mentorado_id, user=request.user)
    except Mentorados.DoesNotExist:
        raise Http404()
    
    subject = f'Seu token de acesso - {mentorado.nome}'
    message = f'''
    Olá {mentorado.nome},
    
    Seu token de acesso para a plataforma de mentoria é:
    {mentorado.token}
    
    Utilize este token para acessar sua área de mentorado.
    
    Atenciosamente,
    Equipe de Mentoria
    '''
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [mentorado.email]
    
    send_mail(subject, message, email_from, recipient_list)
    
    messages.success(request, f'Token enviado com sucesso para {mentorado.email}')
    return redirect('mentorados')
