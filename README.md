Aqui está o README formatado para o GitHub com base na documentação fornecida:

---

# GPTZINHO

GPTZINHO é uma aplicação de chat baseada no ChatGPT usando PyQt5 e a API da OpenAI. Esta aplicação permite ao usuário interagir com modelos de linguagem AI, como GPT-3.5 e GPT-4, simulando uma interação com o ChatGPT.

## Sumário

- [Instalação](#instalação)
- [Configuração](#configuração)
- [Funcionalidades](#funcionalidades)
- [Como Usar](#como-usar)
- [Estilo e Aparência](#estilo-e-aparência)
- [Conclusão](#conclusão)

## Instalação

Para executar esta aplicação, você precisará ter o Python e as seguintes dependências instaladas:

- PyQt5
- requests
- python-dotenv

Use o comando abaixo para instalar as dependências:

```bash
pip install -r requirements.txt
```

## Configuração

Antes de iniciar a aplicação, crie um arquivo `.env` na raiz do projeto e adicione a chave API da OpenAI:

```env
API_KEY=your_openai_api_key
```

## Funcionalidades

### Classes Principais

#### Worker (QThread)
Gerencia solicitações assíncronas à API da OpenAI, evitando bloqueios na interface gráfica.

- **Métodos**:
  - `run()`: Executa a solicitação para a API e emite um sinal quando a resposta é recebida.
  - `enviar_solicitacao_openai()`: Monta e envia a solicitação para a API e retorna os dados relevantes.

#### ChatApp (QWidget)
Classe principal da aplicação, responsável pela interface gráfica do usuário.

- **Atributos**:
  - `modelo`: Armazena o modelo da API utilizado.
  - `temperatura`: Define a temperatura do modelo para geração de texto.
  - `historico_conversa`: Armazena o histórico de conversas.

- **Métodos**:
  - `__init__()`: Inicializa a interface gráfica.
  - `aumentar_temperatura()`, `diminuir_temperatura()`: Ajustam a temperatura do modelo.
  - `mudar_modelo_gpt3()`, `mudar_modelo_gpt4()`: Alteram o modelo da API utilizado.
  - `enviar_mensagem()`: Envia a mensagem do usuário e atualiza a interface.
  - `atualizar_ui()`: Atualiza a interface com a resposta da API.
  - `limpar_campos()`: Limpa os campos de entrada de texto e área de resultados.

### Layout e Widgets

A interface é composta por várias áreas:

- **Área de entrada de texto**: Onde o usuário digita suas mensagens.
- **Área de exibição de resultados**: Onde são exibidas as mensagens e respostas da AI.
- **Contadores de tokens e caracteres**: Mostram a contagem de tokens e caracteres digitados.
- **Botões de ação**: Incluem opções para enviar mensagens, limpar campos, ajustar temperatura e trocar de modelos.

## Como Usar

1. Inicie a aplicação executando o arquivo principal.
2. Digite sua mensagem na área de entrada de texto.
3. Clique em "Enviar" para interagir com o modelo de linguagem.
4. Utilize os botões para ajustar a temperatura e trocar entre modelos GPT-3 e GPT-4.

## Estilo e Aparência

A personalização da aparência dos widgets é realizada através de métodos específicos que definem cores e estilos para diferentes componentes da interface.

## Conclusão

Esta aplicação é um exemplo robusto de como integrar tecnologias de AI em aplicações interativas baseadas em GUI, proporcionando uma plataforma para interações baseadas em texto com modelos de linguagem avançados.

---

Sinta-se à vontade para ajustar e personalizar o README conforme necessário para atender às suas necessidades específicas no GitHub.
