# RAG
Um pacote Python que oferece um assistente capaz de utilizar técnicas de Retrieval-Augmented Generation (RAG) para responder a comandos do usuário, fornecendo respostas baseadas em informações contextuais previamente consultadas.

## Instalação

```console
$ pip install git+https://github.com/guilhermecxe/rag
```

## Exemplos

> Lembre-se de ter um arquivo `.env` com a chave `OPENAI_API_KEY` no diretório do seu projeto.

### Exemplo simples

Utilizando `ai.ask(..)`, o modelo não terá qualquer memória de interações prévias.

```py
from rag import Assistant

content_path = "sample_contents\\People.xlsx" # use um arquivo seu

ai = Assistant()
ai.add_contents([content_path]) # adicionando o conteúdo à aplicação

print(ai.ask('Can you bring me some rows of people with age around 50?'))
# Here are some individuals from the retrieved context who are around the age of 50:

# 1. Nereida Magwood
#    - Female
#    - United States
#    - Age: 58
#    - Date: 16/08/2016
#    - ID: 2468

# 2. Holly Eudy
#    - Female
#    - United States
#    - Age: 52
#    - Date: 16/08/2016
#    - ID: 8561

# 3. Etta Hurn
#    - Female
#    - Age: 56
#    - Date: 15/10/2017
#    - ID: 3598

# 4. Many Cuccia
#    - Female
#    - Great Britain
#    - Age: 46
#    - Date: 21/05/2015
#    - ID: 5489

# These individuals are around the age of 50.
```
### Exemplo com chat

Utilizando `ai.ask_chat(..)`, o modelo terá acesso às últimas mensagens da sessão de bate-papo especificada. O número de últimas mensagens que ele tem acesso para entender o contexto da conversa é limitado por `SETTINGS['MAX_CHAT_MESSAGES_VISIBLE']`.

```py
from rag import Assistant

content_path = "sample_contents\\People.xlsx" # use um arquivo seu
chat_session_id = 'first chat'

ai = Assistant()
ai.add_contents([content_path]) # adicionando o conteúdo à aplicação

ai.create_chat_session(session_id)
ai.add_session_contents(session_id, [content_path]) # adicionando o conteúdo à sessão de bate-papo

print(ai.ask_chat('Can you bring me some rows of people with age around 50?', session_id))
# Here are some individuals from the retrieved context who are around the age of 50:

# 1. Nereida Magwood
#    - Female
#    - United States
#    - Age: 58
#    - Date: 16/08/2016
#    - ID: 2468

# 2. Holly Eudy
#    - Female
#    - United States
#    - Age: 52
#    - Date: 16/08/2016
#    - ID: 8561

# 3. Etta Hurn
#    - Female
#    - Age: 56
#    - Date: 15/10/2017
#    - ID: 3598

# 4. Many Cuccia
#    - Female
#    - Great Britain
#    - Age: 46
#    - Date: 21/05/2015
#    - ID: 5489

# These individuals are around the age of 50.

print(ai.ask_chat('From this list, tell me how many were woman?', session_id))
# All the individuals listed in the last response are women. Therefore, the total number of women in that list is four.

print(ai.ask_chat('There are males around the same age on the spreadsheet?', session_id))
# No, there are no males listed in the retrieved context that are around the age of 50. All the entries for individuals around that age are female.

```

## Configurações

```py
from rag import Assistant
from rag.settings import SETTINGS

new_settings = { # as únicas configurações modificáveis por enquanto
    'openai_api_key': '...',
    'gpt_model': 'gpt-4o-mini',
}

ai.update_settings(**new_settings)

print(SETTINGS) # para ver todas as configurações
```
