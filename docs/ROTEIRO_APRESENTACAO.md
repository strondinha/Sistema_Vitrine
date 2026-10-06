# Roteiro de apresentação da Vitrine Virtual

## Preparação

Inicie o sistema seguindo o README e abra o endereço local. Crie duas contas de teste, com e-mails diferentes. Separe uma imagem JPG ou PNG de até 5 MB e os dados de um projeto. Os três exemplos fictícios podem ser carregados pelo comando `seed-demo`.

## Demonstração

1. **Catálogo público:** mostre a página inicial sem estar autenticado. Explique que qualquer pessoa pode conhecer os projetos do campus.
2. **Cadastro:** crie uma conta e apresente os campos nome, e-mail, senha e perfil.
3. **Novo projeto:** preencha título, curso, área, ano, tipo, resumo, equipe, descrição e resultados.
4. **Contatos e links:** mostre os campos públicos e o link para repositório.
5. **Imagens:** adicione uma imagem e mostre a prévia antes de salvar.
6. **Rascunho:** salve como rascunho. Em uma janela anônima, confira que o projeto e suas imagens não aparecem.
7. **Publicação:** edite o projeto e selecione publicar. Abra a página pública e apresente os resultados, equipe e contatos.
8. **Busca e filtros:** procure pelo título e combine curso, área e ano. Mostre a mensagem quando nenhum resultado é encontrado.
9. **Atualização:** altere os resultados e confira a atualização nos detalhes.
10. **Permissões:** faça login com a segunda conta. Ela pode consultar o projeto publicado, mas não pode editá-lo.
11. **Persistência:** pare e reinicie o servidor. Mostre que o projeto permanece salvo.
12. **Exclusão:** usando um projeto de teste e a conta responsável, apresente a confirmação de exclusão.

## Explicação do código

Comece por `run.py`, que cria a aplicação. Apresente `vitrine/__init__.py` e os módulos `auth.py` e `projects.py`. Mostre `schema.sql` para explicar as relações entre usuários, projetos e imagens. Em seguida, abra uma página em `templates/`, os estilos em `static/css/` e as melhorias de interação em `static/js/`.

Execute os testes automatizados seguindo o README. Explique que eles verificam regras de acesso, persistência e validação com dados temporários. A apresentação no navegador permite avaliar legibilidade, navegação e uso em telas menores.
