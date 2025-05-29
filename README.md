# GPTZINHO - Interface Gráfica para ChatGPT

GPTZINHO é uma aplicação desktop que permite interagir com os modelos de linguagem da OpenAI (GPT-3.5 e GPT-4) através de uma interface gráfica amigável e intuitiva, desenvolvida com PyQt5.

## 🚀 Funcionalidades

- 💬 Interface de chat intuitiva e responsiva
- 🤖 Suporte para dois modelos de IA:
  - GPT-3.5 Turbo (16K)
  - GPT-4
- ⚙️ Controle de temperatura para ajustar a criatividade das respostas
- 📊 Contagem de tokens e caracteres em tempo real
- 🔄 Histórico de conversas mantido para contexto
- 🎨 Interface personalizável com cores e estilos

## 📋 Pré-requisitos

- Python 3.x
- Chave de API da OpenAI
- Conexão com a internet

## 🔧 Instalação

1. Clone este repositório:
```bash
git clone [URL_DO_REPOSITÓRIO]
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Crie um arquivo `.env` na raiz do projeto e adicione sua chave API:
```
API_KEY=sua_chave_api_aqui
```

## 🎮 Como Usar

1. Execute o aplicativo:
```bash
python app.py
```

2. Na interface:
   - Digite sua mensagem na área de texto
   - Use os botões GPT3/GPT4 para alternar entre modelos
   - Ajuste a temperatura usando os botões + e -
   - Clique em ">>>" para enviar sua mensagem
   - Use "X" para limpar os campos

## ⚙️ Configurações

- **Temperatura**: Controla a criatividade das respostas (0.0 a 1.0)
- **Modelos disponíveis**:
  - GPT-3.5 Turbo (16K): Mais rápido e econômico
  - GPT-4: Mais preciso e avançado

## 🛠️ Tecnologias Utilizadas

- Python
- PyQt5 (Interface gráfica)
- OpenAI API
- Requests (Comunicação HTTP)
- Python-dotenv (Gerenciamento de variáveis de ambiente)
- Tiktoken (Contagem de tokens)

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📧 Contato

Para sugestões, dúvidas ou problemas, abra uma issue no repositório.
