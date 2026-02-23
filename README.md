# Livros-Python

README

## Pré-requisitos
- Git instalado
```markdown
# Livros-Python

API simples para gerenciar um catálogo de livros (FastAPI + SQLAlchemy).

Este README contém instruções rápidas para rodar a aplicação localmente (dev) e com containers (podman/docker).

## Pré-requisitos
- Python 3.12 (para desenvolvimento local)
- Podman + podman-compose (ou Docker + docker-compose)
- (opcional) Poetry, se você seguir o fluxo com `pyproject.toml`/`poetry.lock`

## Clonar o repositório

1. Clone o repositório:
```bash
git clone https://github.com/AlanJvPn/Livros-Python.git
```
2. Entre na pasta do projeto:
```bash
cd Livros-Python
```

## Arquivo de ambiente (.env)
Crie um arquivo `.env` na raiz com pelo menos as variáveis abaixo (exemplo):
```env
MEU_USUARIO=seu_usuario
MINHA_SENHA=sua_senha
DATABASE_URL=sqlite:///./livros.db
```

Observação: ao usar volumes (por exemplo `.:/app`) com sqlite, o arquivo `livros.db` será criado no host.

## Rodar em desenvolvimento (virtualenv, rápido)
1. Criar e ativar um virtualenv:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
2. Instalar dependências mínimas para desenvolvimento (sem build de extensões nativas):
```bash
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy aiosqlite pydantic
```
3. Exportar variáveis de ambiente (ou use o `.env`):
```bash
export DATABASE_URL="sqlite:///./livros.db"
export MEU_USUARIO="seu_usuario"
export MINHA_SENHA="sua_senha"
```

Abra http://127.0.0.1:8000 para acessar a API.

## Rodar com podman-compose
Se estiver usando Podman, o comando abaixo lê o `.env` e (re)builda a imagem:
```bash
podman-compose --env-file .env up --build -d
```
Para ver logs em tempo real (útil se algo falhar durante o start):
```bash
podman-compose logs -f
```
Para parar e remover os containers:
```bash
podman-compose down
```
