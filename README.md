# Mentorados - Sistema de Mentoria

![Logo do Projeto](templates/static/logo.png)

Um sistema completo para gerenciamento de mentorias, permitindo o cadastro de mentores e mentorados, agendamento de reuniões, atribuição de tarefas e acompanhamento do progresso.

## 🚀 Funcionalidades Principais

- **Autenticação de Usuários**: Cadastro e login para mentores e mentorados
- **Agendamento de Reuniões**: Interface para marcar encontros entre mentor e mentorado
- **Gerenciamento de Tarefas**: Criação e acompanhamento de atividades
- **Upload de Arquivos**: Envio de materiais e trabalhos
- **Painel Administrativo**: Área para gestão do sistema

## 💻 Tecnologias Utilizadas

- **Backend**: Django 4.x
- **Frontend**: HTML5, CSS3, JavaScript
- **Banco de Dados**: SQLite (padrão) - pode ser configurado para PostgreSQL/MySQL
- **Outras Bibliotecas**: 
  - Django Allauth para autenticação
  - Django Crispy Forms para formulários

## ⚙️ Como Configurar

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/mentorados.git
cd mentorados
```

2. Crie um ambiente virtual e ative:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute as migrações:
```bash
python manage.py migrate
```

5. Crie um superusuário:
```bash
python manage.py createsuperuser
```

6. Inicie o servidor:
```bash
python manage.py runserver
```

## 📂 Estrutura de Diretórios

```
mentorados/
├── core/              # Configurações principais do Django
├── mentorados/        # App principal para funcionalidades de mentoria
│   ├── migrations/    # Migrações do banco de dados
│   ├── templates/     # Templates específicos do app
├── usuarios/          # App para gestão de usuários
│   ├── templates/     # Templates de autenticação
├── templates/         # Templates base e globais
```

## 📸 Screenshots

_(Adicione screenshots das principais telas do sistema aqui)_

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Contribuição

Contribuições são bem-vindas! Siga estes passos:
1. Faça um fork do projeto
2. Crie sua branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request
