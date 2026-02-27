# Livros-Python (API com Redis Cache)

API para gerenciar um catálogo de livros construída com FastAPI, SQLAlchemy (banco de dados) e Redis (cacheamento para alta performance). 

O projeto foi projetado utilizando Arquitetura em Camadas e conteinerização, garantindo escalabilidade e facilidade de implantação.

---

## 🛠️ Arquitetura e Estrutura de Arquivos

* **`Dockerfile`**: Detalha a construção da imagem da aplicação, incluindo a instalação do Poetry e das dependências do projeto de forma isolada.
* **`docker-compose.yml`**: Configura a orquestração do ambiente, definindo como os serviços (API FastAPI, banco de dados PostgreSQL e Redis) se comunicam em uma rede interna.
* **`main.py`**: O coração da aplicação, definindo as rotas (endpoints) do FastAPI, a injeção de dependências e a lógica de negócios.
* **`pyproject.toml`**: Arquivo de configuração do ecossistema Poetry que centraliza e lista as bibliotecas e ferramentas necessárias para o projeto.
* **`poetry.lock`**: Arquivo gerado pelo Poetry que "trava" as versões exatas das dependências, garantindo que o código rode da mesma forma em qualquer computador.
* **`livros.db`**: O arquivo físico do banco de dados local (SQLite) onde os registros são armazenados (geralmente utilizado em ambiente de desenvolvimento local sem contêineres).
* **`.env`**: Arquivo de variáveis de ambiente que guarda senhas, usuários e URLs de conexão de forma segura (não é enviado ao repositório).
* **`.gitignore`**: Define quais pastas e arquivos sensíveis (como o `.env` e pastas de cache) o Git deve ignorar, protegendo o repositório.

---

## ⚙️ Pré-requisitos
- Git instalado
- Python 3.12+ (para desenvolvimento local)
- Podman + podman-compose (ou Docker + docker-compose)
- (Opcional) Poetry

---

## 🚀 Como Executar o Projeto

### 1. Clonar e Configurar
Clone o repositório e entre na pasta:
git clone [https://github.com/AlanJvPn/Livros-Python.git](https://github.com/AlanJvPn/Livros-Python.git)
cd Livros-Python

Crie um arquivo .env na raiz do projeto contendo suas credenciais locais:
Snippet de código

MEU_USUARIO=admin
MINHA_SENHA=admin
DATABASE_URL=sqlite:///./livros.db

2. Rodar com Contêineres (Recomendado)

Para subir a API, o Banco de Dados e o Redis de uma só vez usando o Compose:
podman-compose --env-file .env up --build -d
A API estará disponível em: http://127.0.0.1:8000

3. Rodar Localmente (Desenvolvimento)

Se preferir rodar sem contêineres para debugar o código:

# Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instale as dependências
pip install fastapi uvicorn sqlalchemy pydantic "redis[hiredis]"

# Inicie o servidor
uvicorn main:app --reload

🧪 Testes Manuais (cURL)

Abaixo estão os comandos curl para testar todos os fluxos da API, validando tanto o caminho de sucesso (Happy Path) quanto o tratamento de erros (Edge Cases).

1. Testes de Autenticação
[ERRO 401] Tentar acessar sem credenciais ou com senha errada:
curl -i -u hacker:1234 [http://127.0.0.1:8000/livros](http://127.0.0.1:8000/livros)
# Retorno esperado: HTTP/1.1 401 Unauthorized ("Credenciais inválidas")

2. Adicionar Livros (POST)
[SUCESSO 200] Adicionar um novo livro (aciona a invalidação de cache):
curl -i -u admin:admin -X POST [http://127.0.0.1:8000/adiciona](http://127.0.0.1:8000/adiciona) \
-H "Content-Type: application/json" \
-d '{"titulo_livro": "Duna", "autor_livro": "Frank Herbert", "ano_livro": 1965}'
# Retorno esperado: HTTP/1.1 200 OK ("O livro Duna foi adicionado com sucesso!")

[ERRO 400] Tentar adicionar um livro duplicado:
curl -i -u admin:admin -X POST [http://127.0.0.1:8000/adiciona](http://127.0.0.1:8000/adiciona) \
-H "Content-Type: application/json" \
-d '{"titulo_livro": "Duna", "autor_livro": "Frank Herbert", "ano_livro": 1965}'
# Retorno esperado: HTTP/1.1 400 Bad Request ("Esse Livro já existe no catálogo.")

3. Listar Livros (GET)
[SUCESSO 200] Buscar livros paginados (salva o resultado no Redis):
curl -i -u admin:admin "[http://127.0.0.1:8000/livros?page=1&limit=10](http://127.0.0.1:8000/livros?page=1&limit=10)"
# Retorno esperado: HTTP/1.1 200 OK (Lista JSON com o livro "Duna")
# Nota: Chamadas subsequentes retornarão instantaneamente via Cache.

[ERRO 400] Enviar parâmetros de paginação inválidos:
curl -i -u admin:admin "[http://127.0.0.1:8000/livros?page=0&limit=10](http://127.0.0.1:8000/livros?page=0&limit=10)"
# Retorno esperado: HTTP/1.1 400 Bad Request ("Valores de página e limite devem ser maiores que zero.")

4. Atualizar Livros (PUT)
[SUCESSO 200] Atualizar os dados de um livro existente:
curl -i -u admin:admin -X PUT [http://127.0.0.1:8000/atualiza/1](http://127.0.0.1:8000/atualiza/1) \
-H "Content-Type: application/json" \
-d '{"titulo_livro": "Duna - Messias", "autor_livro": "Frank Herbert", "ano_livro": 1969}'
# Retorno esperado: HTTP/1.1 200 OK ("O livro Duna - Messias foi atualizado com sucesso!")

[ERRO 404] Tentar atualizar um livro que não existe:
curl -i -u admin:admin -X PUT [http://127.0.0.1:8000/atualiza/999](http://127.0.0.1:8000/atualiza/999) \
-H "Content-Type: application/json" \
-d '{"titulo_livro": "Fantasma", "autor_livro": "Ninguem", "ano_livro": 2024}'
# Retorno esperado: HTTP/1.1 404 Not Found ("Esse Livro não foi encontrado no catálogo.")

5. Deletar Livros (DELETE)
[SUCESSO 200] Deletar um livro existente:
curl -i -u admin:admin -X DELETE [http://127.0.0.1:8000/deletar/1](http://127.0.0.1:8000/deletar/1)
# Retorno esperado: HTTP/1.1 200 OK ("O livro Duna - Messias foi deletado com sucesso!")

[ERRO 404] Tentar deletar um ID inexistente:
curl -i -u admin:admin -X DELETE [http://127.0.0.1:8000/deletar/999](http://127.0.0.1:8000/deletar/999)
# Retorno esperado: HTTP/1.1 404 Not Found ("Esse Livro não foi encontrado para ser deletado")
