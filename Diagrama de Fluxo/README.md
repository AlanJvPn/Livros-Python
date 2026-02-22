
Dockerfile: Este arquivo detalha a construção da imagem Docker, incluindo a instalação do Poetry e das dependências do seu projeto usando o Poetry.

docker-compose.yml: Este arquivo configura o ambiente com Docker Compose, definindo como a imagem será criada e executada.

main.py: O arquivo principal que define a aplicação, com as principais funçoes e rotas de FastAPI.

pyproject.toml: O arquivo de configuração do Poetry que lista as dependências do projeto.

poetry.lock: Este arquivo (gerado pelo Poetry após poetry install) garante a consistência das versões de dependência em diferentes ambientes.

livros.db: O arquivo do banco de dados local onde os registros e informações da aplicação são armazenados.

.env: O arquivo de variáveis de ambiente, utilizado para guardar configurações sensíveis e credenciais de forma segura e separada do código-fonte.

.gitignore: O arquivo de configuração do Git que define quais pastas e arquivos devem ser ignorados e protegidos para não serem enviados acidentalmente para o GitHub.