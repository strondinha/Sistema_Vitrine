# Vitrine Virtual do IFPI Campus Corrente

Sistema web para divulgar projetos de ensino, pesquisa e extensão. Implementado a partir do documento **PROJETO VITRINE(1).docx**, de Caio Vieira Vila Nova, Klesly de Souza Rocha e Lucas Maciel da Silva, com orientação do professor Jurandir Cavalcante.

O projeto inclui código do servidor, telas, estilos, banco relacional, validações, testes automatizados e instruções de instalação. Os dados são gravados em SQLite e permanecem salvos depois que o sistema é fechado.

## Comece aqui

Você precisa de **Python 3.10 ou superior**, com `pip` e `venv`. A instalação das dependências exige internet. Depois de instalar os pacotes, a aplicação funciona localmente sem internet; os links externos dependem de conexão.

### Windows

1. Extraia o ZIP. Entre na pasta `vitrine-virtual`.
2. Instale o Python, se necessário, marcando **Add Python to PATH** no instalador.
3. Execute o arquivo **iniciar_windows.bat**.
4. Abra **http://127.0.0.1:5000** no navegador.
5. Clique em **Criar conta**, cadastre-se e entre. Em **Meus projetos**, clique em **Novo projeto**.

O arquivo `.bat` cria um ambiente virtual, instala as dependências e inicia o servidor. Mantenha a janela aberta enquanto estiver usando o sistema. Para encerrar, pressione **Ctrl+C**.

Também é possível executar manualmente no terminal do VS Code, aberto na pasta `vitrine-virtual`:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe run.py
```

Esses comandos não exigem ativar o ambiente virtual, evitando problemas com a política de scripts do PowerShell.

### Linux ou macOS

Na pasta `vitrine-virtual`, execute:

```bash
bash iniciar_linux_mac.sh
```

Ou use os comandos:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run.py
```

Abra **http://127.0.0.1:5000**. Em algumas distribuições Linux, será necessário instalar o pacote `python3-venv` antes de criar o ambiente.

## O que o sistema faz

| Funcionalidade | Como usar |
| --- | --- |
| Cadastro de usuários | Nome, e-mail, senha e perfil de aluno ou professor |
| Login e logout | Acesso à área pessoal e encerramento de sessão |
| Cadastro de projetos | Título, curso, área, ano, tipo, resumo, descrição, resultados e equipe |
| Contatos e links | E-mail público, telefone, repositório e outro link |
| Imagens | Até 6 imagens por projeto, com galeria e primeira imagem como capa |
| Catálogo público | Consulta de projetos publicados sem exigir conta |
| Busca | Por título, resumo ou equipe, ignorando maiúsculas e acentos |
| Filtros combinados | Curso, área do conhecimento, ano e tipo de projeto |
| Rascunhos | Projetos e imagens visíveis somente ao responsável |
| Gerenciamento | Visualizar, editar, publicar, retirar da vitrine e excluir os próprios projetos |
| Paginação | Até 9 projetos por página, mantendo os filtros selecionados |
| Compartilhamento | Copiar o link de um projeto publicado |

Os perfis aluno e professor têm as mesmas permissões de gerenciamento dos próprios projetos. O perfil é informado pelo usuário; não há verificação institucional automática. Cursos e áreas têm sugestões editáveis: elas não representam uma lista oficial de cursos ofertados pelo campus.

## Publicando o primeiro projeto

1. Crie uma conta e faça login.
2. Abra **Meus projetos → Novo projeto**.
3. Preencha os campos obrigatórios identificados com `*`.
4. Adicione a descrição, os resultados, os contatos e os links que desejar divulgar.
5. Selecione imagens JPG, PNG ou WEBP. Cada imagem pode ter até 5 MB; todo o envio pode ter até 16 MB. Imagens acima de 20 megapixels são recusadas.
6. Escolha **Salvar como rascunho** para continuar depois ou **Publicar na vitrine** para tornar o projeto público.
7. Clique em **Salvar projeto**.

Para retirar um projeto do catálogo sem apagar seus dados, edite-o e selecione **Salvar como rascunho**. Para trocar a capa, remova a primeira imagem; a próxima imagem existente passa a ser a capa. Novas imagens são adicionadas ao fim da galeria.

Os contatos preenchidos no formulário ficam públicos ao publicar o projeto. O e-mail da conta não é exibido automaticamente no catálogo, mas é sugerido no campo de contato do novo projeto e pode ser alterado ou apagado.

## Dados de demonstração opcionais

A primeira execução começa com o catálogo vazio. Para carregar **três exemplos fictícios**, use:

**Windows:**

```powershell
.venv\Scripts\python.exe -m flask --app run.py seed-demo
```

**Linux/macOS:**

```bash
.venv/bin/python -m flask --app run.py seed-demo
```

Os exemplos estão identificados como demonstração. Esse comando não cria uma conta com senha compartilhada. Crie sua própria conta para gerenciar projetos reais. Executar novamente não duplica os exemplos.

## Organização das pastas

| Caminho | Responsabilidade |
| --- | --- |
| `run.py` | Entrada da aplicação e inicialização do servidor local |
| `vitrine/__init__.py` | Configuração da aplicação, módulos e páginas de erro |
| `vitrine/auth.py` | Cadastro, login, sessão e limite de tentativas |
| `vitrine/projects.py` | Catálogo, busca, filtros, detalhes e gerenciamento |
| `vitrine/db.py` | Conexão com o banco e comandos de inicialização e demonstração |
| `vitrine/schema.sql` | Modelagem SQL das tabelas e índices |
| `vitrine/security.py` | Proteção de formulários e exigência de login |
| `vitrine/validation.py` | Validação de campos, e-mails, links e sugestões |
| `vitrine/uploads.py` | Validação, processamento e armazenamento das imagens |
| `vitrine/pages.py` | Página sobre a plataforma |
| `vitrine/templates/` | Telas HTML com Jinja, separadas por funcionalidade |
| `vitrine/static/css/` | Estilos e regras para celular, tablet e computador |
| `vitrine/static/js/` | Menu, galeria, prévias, contador e cópia de link |
| `vitrine/static/img/` | Ícone da plataforma |
| `instance/` | Banco, imagens enviadas e chave de sessão, gerados ao executar |
| `tests/` | Testes dos fluxos e das permissões com dados temporários |
| `docs/` | Arquitetura, requisitos e roteiro de apresentação |

## Banco de dados

O SQLite vem com o Python; não é necessário instalar MySQL ou configurar usuário de banco. Na primeira execução, o sistema cria automaticamente:

- `instance/vitrine.sqlite3`: usuários, projetos, referências das imagens e tentativas de login.
- `instance/uploads/`: imagens processadas.
- `instance/secret.key`: chave local que protege a sessão.

As tabelas são criadas com `CREATE TABLE IF NOT EXISTS`. Reiniciar a aplicação não apaga os dados. Para recriar apenas tabelas ausentes, use `python -m flask --app run.py init-db` com o Python do ambiente virtual.

Faça backup de **toda a pasta `instance` com o servidor parado**, pois o banco contém as referências dos arquivos de imagem. Não envie essa pasta para um repositório público. O ZIP de código não contém banco preenchido, contas, imagens particulares nem chave de sessão.

## Testes

Os testes usam bancos e diretórios temporários, separados da aplicação:

**Windows:**

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest -q
```

**Linux/macOS:**

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

A suíte cobre cadastro, login, senhas protegidas, duplicidade de e-mail, encerramento de sessão, CRUD, rascunhos privados, controle de propriedade, busca em português, filtros combinados, paginação, uploads, limites de tamanho, limpeza de arquivos, validação de links, escape de HTML, proteção CSRF, limite de login e persistência após reinicialização.

## Apresentação e implantação

O comando `python run.py` escuta apenas no próprio computador e serve para desenvolvimento e apresentação local. Para uma implantação com vários usuários, o servidor WSGI Waitress está incluído nas dependências:

```bash
python -m waitress --listen=127.0.0.1:8000 run:app
```

Execute esse comando com o Python do ambiente virtual. Para disponibilizar na internet, configure uma hospedagem Python com armazenamento persistente, HTTPS e proxy para a aplicação. A pasta `instance` precisa continuar disponível entre reinicializações e novas versões. SQLite é adequado para esta implementação acadêmica; avalie outro banco se houver grande volume de escritas simultâneas.

Variáveis opcionais:

| Variável | Uso |
| --- | --- |
| `PORT` | Porta do servidor iniciado com `run.py`; padrão `5000` |
| `SECRET_KEY` | Chave de sessão fornecida pela hospedagem; se ausente, usa a chave local persistida |
| `COOKIE_SECURE` | Use `1` quando a aplicação estiver acessível por HTTPS; mantenha ausente em HTTP local |

Variáveis de ambiente são lidas pelo processo. O sistema não carrega arquivos `.env` automaticamente. Os scripts de inicialização mantêm o modo de depuração desligado.

## Dúvidas comuns

**“Python não foi encontrado.”** Instale Python 3.10 ou superior com a opção de adicionar ao PATH. Feche e abra novamente o terminal.

**“A porta está em uso.”** Encerre outro processo que use a porta 5000 ou altere `PORT`. No PowerShell: `$env:PORT="5001"`; depois execute `run.py` e abra `http://127.0.0.1:5001`.

**“Meu projeto não aparece na vitrine.”** Verifique se ele está publicado. Rascunhos aparecem somente em **Meus projetos** e nos detalhes acessados pelo responsável.

**“A imagem foi recusada.”** Confira formato, tamanho e resolução. SVG e arquivos que apenas foram renomeados para `.jpg` não são aceitos.

**“Muitas tentativas de acesso.”** Após dez tentativas de login inválidas do mesmo endereço IP, aguarde 15 minutos.

## Escopo desta entrega

Esta implementação cobre as funcionalidades da plataforma descritas no documento. A pesquisa com a comunidade, a capacitação, o acompanhamento por seis meses e a avaliação dos resultados são etapas de execução do projeto acadêmico, conduzidas pela equipe. Não foram transformadas em módulos adicionais de software.

Não há envio de e-mails, recuperação automática de senha, autenticação institucional nem painel de moderação. O catálogo e a galeria funcionam pelo servidor; a busca e os formulários principais também funcionam sem JavaScript. O projeto foi validado por testes automatizados de integração e checagem de sintaxe; a revisão visual em navegador e a execução do iniciador `.bat` no Windows devem ser realizadas no ambiente da apresentação.

Documentação técnica utilizada: [Flask — estrutura da aplicação](https://flask.palletsprojects.com/en/stable/tutorial/factory/), [SQLite e conexão por requisição](https://flask.palletsprojects.com/en/stable/tutorial/database/) e [testes com cliente Flask](https://flask.palletsprojects.com/en/stable/tutorial/tests/).
