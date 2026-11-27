# MicroBlog — Clone do Twitter (Projeto Final EBAC)

Aplicação web estilo microblog (clone do Twitter/X) desenvolvida com **Python**, **Django**, **Django REST Framework** e interface responsiva integrada.

## Funcionalidades
- Cadastro de conta, login e logout com autenticação segura.
- Edição opcional de perfil (foto, nome de exibição, bio e senha).
- Sistema de seguir e deixar de seguir usuários com contagem e listas de seguidores/seguindo.
- Feed dinâmico exibindo apenas publicações próprias e dos usuários seguidos.
- Criação e exclusão de postagens, curtidas e comentários em tempo real via API REST.

## Como executar localmente

1. Clone o repositório:
   ```bash
   git clone https://github.com
   cd twitter-clone-ebac
   ```

2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Aplique as migrações e inicie o servidor:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

4. Acesse `http://127.0.0.1:8000` no navegador.
