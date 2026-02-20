# Livros-Python

README

## Pré-requisitos
- Git instalado
- Docker e Docker Compose instalados e funcionando

## Clonar o repositório
1. Clone o repositório:
```
git clone https://github.com/AlanJvPn/Livros-Python.git
```
2. Entre na pasta do projeto:
```
cd Livros-Python
```

## Construir e executar (em segundo plano)
Execute:
```
docker-compose up --build -d
```
- Isso constrói as imagens (se necessário) e inicia os contêineres em segundo plano.

## Verificar status e logs
- Verificar contêineres em execução:
```
docker-compose ps
```
- Acompanhar logs:
```
docker-compose logs -f
```

## Parar e remover contêineres
Para parar e remover os contêineres, redes e volumes associados:
```
docker-compose down
```
