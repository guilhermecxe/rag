# RAG
Um pacote Python que oferece um assistente capaz de utilizar técnicas de Retrieval-Augmented Generation (RAG) para responder a comandos do usuário, fornecendo respostas baseadas em informações contextuais previamente consultadas.

## Instalação

```console
$ pip install git+https://github.com/guilhermecxe/rag
```

## Exemplo

> Lembre-se de ter um arquivo `.env` com a chave `OPENAI_API_KEY` no diretório do seu projeto.

```py
from rag import Assistant

question = 'Faça um breve resumo do contexto fornecido'

ai = Assistant()
answear = ai.ask(question)

print(question)
print(answear)

```

## Configurações

```py
from rag.settings import SETTINGS

SETTINGS['VECTORS_DATABASE_PATH'] = 'database'
SETTINGS['CONTENTS_PATH'] = 'contents'
SETTINGS['GPT_MODEL'] = 'gpt-4o-mini',

# Para ver outros valores modificáveis:
print(SETTINGS.items())

```