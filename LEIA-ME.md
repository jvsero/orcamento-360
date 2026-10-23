# Orçamento 360 — Dashboard de Análise Orçamentária

## O que está incluído
- Menu lateral interativo com Visão geral, Órgãos, Categorias, Grupos de despesa, Fontes e Explorar dados.
- Indicadores de total pago, empenhado, liquidado e quantidade de órgãos (quando as colunas existem).
- Gráficos interativos Plotly: barras, rosca, linha e treemap.
- Filtros por ano e órgão.
- Pesquisa na tabela e download de CSV.
- Tema escuro tecnológico.
- **Não usa Kaleido nem precisa exportar gráficos para PNG.**

## Onde colocar o Excel
- Opção A: `dados_originais/Orcamento.xlsx`
- Opção B: envie o Excel/CSV no menu lateral quando o app estiver aberto.
- Nome de aba preferido no Excel: `Relatório de Despesas com Tecno`. Se não existir, o app usa a primeira aba.
- Colunas reconhecidas: `Ano`, `Órgão`, `Programa`, `Localizador`, `Poder`, `Função`, `Fonte`, `Categoria Econômica`, `Grupo Despesa`, `Elemento Despesa`, `Projeto de Lei`, `Empenhado`, `Liquidado`, `Pago`.

## Rodar no computador
1. Instale Python 3.11 ou 3.12 se possível.
2. Abra o terminal dentro desta pasta.
3. Crie ambiente virtual:
   - Linux/macOS: `python3 -m venv .venv`
   - Ative: `source .venv/bin/activate`
   - Windows: `.venv\Scripts\activate`
4. Instale dependências: `pip install -r requirements.txt`
5. Inicie: `streamlit run app.py`

## Publicar gratuitamente
1. Crie uma conta no GitHub.
2. Crie um repositório público, por exemplo `orcamento-360`.
3. Envie os arquivos desta pasta ao repositório. Inclua `app.py`, `requirements.txt`, `.streamlit/config.toml`, `LEIA-ME.md` e as pastas.
4. Se quiser que o app abra com dados carregados automaticamente, adicione somente um conjunto de dados que seja público e cuja publicação você tenha autorização para fazer. Coloque-o em `dados_originais/Orcamento.xlsx` ou `dados_tratados/orcamento_tratado.csv`.
5. Acesse https://share.streamlit.io/ e entre com GitHub.
6. Clique em **Create app**, selecione o repositório, branch `main` e arquivo principal `app.py`; clique em **Deploy**.
7. Quando o deploy terminar, copie o link `*.streamlit.app` e compartilhe.

## Privacidade e limitações
- O app é público se você o publicar publicamente. Não coloque dados pessoais, senhas, tokens ou dados confidenciais no repositório.
- Se não incluir um arquivo de dados no repositório, qualquer visitante pode carregar um Excel/CSV na sessão do app; o arquivo não vira automaticamente um dado permanente no servidor.
- O Google Drive não é conectado automaticamente ao app publicado. Para dados persistentes e atualizados, o projeto precisará de uma integração própria.
- O Streamlit Community Cloud é gratuito, mas tem limites de recursos e disponibilidade que podem mudar.

## Kaggle: onde entra?
Kaggle é útil para explorar datasets públicos, estudar notebooks e comparar métodos de análise. Ele não é a plataforma recomendada para hospedar o dashboard Streamlit para visitantes. Use Kaggle/Colab para análise e aprendizado, GitHub para guardar o código e Streamlit Community Cloud para publicar o app.
