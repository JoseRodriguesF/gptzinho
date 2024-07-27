# Importando bibliotecas necessárias para a aplicação.
import tiktoken  # Biblioteca para manipulação de tokens.
import sys  # Biblioteca padrão do Python para interagir com o sistema operacional.
import openai  # Biblioteca para interagir com a API da OpenAI.
import requests  # Biblioteca para fazer requisições HTTP.
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QLineEdit
# Importa componentes gráficos do PyQt5 para construir a interface do usuário.
from PyQt5.QtGui import QFont, QTextCursor, QTextBlockFormat
# Importa funcionalidades gráficas adicionais do PyQt5.
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
import os  # Biblioteca para interagir com o sistema de arquivos.
from dotenv import load_dotenv  # Biblioteca para carregar variáveis de ambiente de um arquivo .env.

# Configuração do tokenizador para modelo GPT-4.
nome_modelo = "gpt-4"  # Nome do modelo GPT-4.
tokenizador = tiktoken.encoding_for_model("gpt-4")  # Inicializa o tokenizador para o modelo GPT-4.

# Carregando a chave API do arquivo .env para autenticar requisições à API da OpenAI.
load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env.
openai.api_key = os.getenv('API_KEY')  # Define a chave da API a partir da variável de ambiente.

# Classe Worker para gerenciar solicitações assíncronas usando threads.
class Worker(QThread):  # Define uma classe que herda de QThread.
    terminado = pyqtSignal(str, dict, int)  # Sinal emitido quando a tarefa é concluída.
    def __init__(self, app_chat, mensagem):
        super(Worker, self).__init__()  # Inicializa a classe base.
        self.app_chat = app_chat  # Referência à instância da aplicação de chat.
        self.mensagem = mensagem  # Mensagem a ser enviada à API.

    # Executa a solicitação à API da OpenAI e emite o sinal quando completa.
    def run(self):  # Método que é executado quando o thread inicia.
        resposta, contagem_tokens = self.enviar_solicitacao_openai()  # Envia a solicitação à API.
        if resposta is None:
            resposta = {}  # Garante que a resposta seja um dicionário.
        self.terminado.emit(self.mensagem, resposta, contagem_tokens)  # Emite o sinal com a mensagem, resposta e contagem de tokens.

    # Prepara e envia uma solicitação HTTP para a API da OpenAI.
    def enviar_solicitacao_openai(self):
        link = "https://api.openai.com/v1/chat/completions"  # URL da API.
        cabecalhos = {"Content-Type": "application/json", "Authorization": f"Bearer {openai.api_key}"}  # Cabeçalhos da requisição.
        dados = {  # Dados da requisição.
            "model": self.app_chat.modelo,
            "messages": self.app_chat.historico_conversa,
            "temperature": self.app_chat.temperatura,
            "max_tokens": 4000
        }
        try:
            resposta = requests.post(link, headers=cabecalhos, json=dados)  # Envia a requisição POST.
            if resposta.status_code == 200:  # Verifica se a resposta é bem-sucedida.
                resposta_json = resposta.json()  # Converte a resposta para JSON.
                if 'choices' in resposta_json and resposta_json['choices']:  # Verifica se há respostas válidas.
                    contagem_tokens = resposta_json.get('usage', {}).get('total_tokens', 0)  # Obtém a contagem de tokens.
                    return resposta_json, contagem_tokens  # Retorna a resposta e a contagem de tokens.
                else:
                    print("Resposta da API não contém 'choices'")  # Mensagem de erro.
                    return None, 0
            else:
                print(f"Erro na requisição: {resposta.status_code}")  # Mensagem de erro.
                return None, 0
        except Exception as e:
            print(f"Exceção ao fazer a solicitação: {e}")  # Mensagem de erro em caso de exceção.
            return None, 0

# Classe principal para a aplicação de chat.
class ChatApp(QWidget):  # Define uma classe que herda de QWidget.
    def __init__(self):
        super().__init__()  # Inicializa a classe base.

        self.setWindowTitle("Chat")  # Define o título da janela.
        self.setGeometry(100, 100, 1280, 720)  # Define o tamanho e a posição da janela.
        self.modelo = "gpt-3.5-turbo-16k"  # Modelo inicial da API.
        self.temperatura = 0.5  # Define a criatividade padrão das respostas.
        self.historico_conversa = []  # Armazena o histórico de mensagens para contexto.

        # Configurações de widgets da UI, como botões, entradas de texto e layouts.
        self.label_status = QLabel("Aguardando resposta...", self)  # Texto exibido enquanto aguarda a resposta da API.
        self.label_status.setAlignment(Qt.AlignCenter)  # Alinha o texto no centro.
        self.label_status.setStyleSheet("color: #ffffff;")  # Define a cor do texto.
        self.label_status.hide()  # Esconde o texto após obter a resposta da API.

        self.entrada = QTextEdit(self)  # Área de texto para entrada do usuário.
        self.entrada.textChanged.connect(self.ajustar_altura_entrada)  # Conecta o evento de mudança de texto.

        self.timer_contagem_tokens = QTimer(self)  # Timer para atualizar a contagem de caracteres.
        self.timer_contagem_tokens.setInterval(1000)  # Define o intervalo do timer.
        self.timer_contagem_tokens.timeout.connect(self.atualizar_contador_caracteres)  # Conecta o evento de timeout.
        self.entrada.textChanged.connect(self.timer_contagem_tokens.start)  # Inicia o timer quando o texto muda.

        self.timer_contagem_tokens = QTimer(self)  # Outro timer para atualizar a contagem de tokens.
        self.timer_contagem_tokens.setInterval(1000)  # Define o intervalo do timer.
        self.timer_contagem_tokens.timeout.connect(self.atualizar_contagem_tokens)  # Conecta o evento de timeout.
        self.entrada.textChanged.connect(self.timer_contagem_tokens.start)  # Inicia o timer quando o texto muda.

        self.contador_tokens = QTextEdit(self)  # Área de texto para mostrar a contagem de tokens.
        self.contador_tokens.setReadOnly(True)  # Define como somente leitura.

        self.resultados = QTextEdit(self)  # Área de texto para mostrar as respostas da API.
        self.resultados.setReadOnly(True)  # Define como somente leitura.

        # Layouts para organizar os widgets na janela.
        layout_resultados = QVBoxLayout()  # Layout vertical para os resultados.
        layout_resultados.addStretch(0)  # Adiciona um espaço em cima da área de resultados.
        layout_resultados.addWidget(self.resultados, alignment=Qt.AlignCenter)
        layout_resultados.addWidget(self.label_status)

        layout_entrada = QHBoxLayout()  # Layout horizontal para a entrada de texto.
        layout_entrada.addStretch(2)  # Adiciona um espaço à esquerda do campo de texto.
        layout_entrada.addWidget(self.entrada, alignment=Qt.AlignCenter)

        self.botao_limpar = QPushButton("X", self)  # Botão para limpar campos.
        self.botao_limpar.clicked.connect(self.limpar_campos)  # Conecta o evento de clique.
        layout_entrada.addWidget(self.botao_limpar, alignment=Qt.AlignCenter)

        self.botao_enviar = QPushButton(">>>", self)  # Botão para enviar mensagem.
        self.botao_enviar.clicked.connect(self.enviar_mensagem)  # Conecta o evento de clique.
        layout_entrada.addWidget(self.botao_enviar, alignment=Qt.AlignCenter)
        self.botao_enviar.clicked.connect(self.entrada.clear)  # Limpa a entrada após enviar.
        layout_entrada.addStretch(2)  # Adiciona espaços à direita do enviar.

        layout_contador = QVBoxLayout()  # Layout vertical para o contador de tokens.
        layout_contador.addStretch(1)
        layout_contador.addWidget(self.contador_tokens, alignment=Qt.AlignCenter)

        layout_principal = QVBoxLayout(self)  # Layout principal vertical.
        layout_principal.addLayout(layout_contador)
        layout_principal.addLayout(layout_resultados)
        layout_principal.addLayout(layout_entrada)
        self.setLayout(layout_principal)

        # Outras configurações de UI e inicializações, como botões de modelo e temperatura.
        self.tokens_mensagem = 0
        self.tokens_resposta = 0
        self.contador_caracteres = 0
        self.limite_tokens_msg = 2000
        self.limite_tokens_resposta = 2000

        self.botao_GPT3 = QPushButton("GPT3", self)  # Botão para mudar para GPT-3.
        self.botao_GPT3.clicked.connect(self.mudar_modelo_gpt3)  # Conecta o evento de clique.
        self.botao_GPT4 = QPushButton("GPT4", self)  # Botão para mudar para GPT-4.
        self.botao_GPT4.clicked.connect(self.mudar_modelo_gpt4)  # Conecta o evento de clique.

        self.set_posicao_botao_gpt3(self.botao_GPT3, 35, 10)  # Define a posição do botão GPT3.
        self.set_posicao_botao_gpt4(self.botao_GPT4, 35, 40)  # Define a posição do botão GPT4.

        self.visor_temperatura = QTextEdit(self)  # Área de texto para mostrar a temperatura.
        self.visor_temperatura.setReadOnly(True)  # Define como somente leitura.

        self.set_posicao_visor(self.visor_temperatura, 35, 75)  # Define a posição do visor de temperatura.
        self.visor_temperatura.setText(f"{self.temperatura:.1f}")  # Define o texto inicial do visor.
        self.visor_temperatura.setAlignment(Qt.AlignCenter)  # Alinha o texto no centro.

        self.botao_aumentar_temp = QPushButton("+", self)  # Botão para aumentar a temperatura.
        self.botao_aumentar_temp.clicked.connect(self.aumentar_temperatura)  # Conecta o evento de clique.
        self.botao_diminuir_temp = QPushButton("-", self)  # Botão para diminuir a temperatura.
        self.botao_diminuir_temp.clicked.connect(self.diminuir_temperatura)  # Conecta o evento de clique.

        self.set_posicao_botao_aumentar_temp(self.botao_aumentar_temp, 100, 75)  # Define a posição do botão de aumentar temperatura.
        self.set_posicao_botao_diminuir_temp(self.botao_diminuir_temp, 5, 75)  # Define a posição do botão de diminuir temperatura.

    # Métodos para configurar e ajustar a interface do usuário, como tamanho, cor e posição dos componentes.
    def set_posicao_visor(self, visor_temperatura, x, y):
        visor_temperatura.move(x, y)  # Move o visor de temperatura para a posição especificada.

    def set_posicao_botao_aumentar_temp(self, botao_aumentar_temp, x, y):
        botao_aumentar_temp.move(x, y)  # Move o botão de aumentar temperatura para a posição especificada.

    def set_posicao_botao_diminuir_temp(self, botao_diminuir_temp, x, y):
        botao_diminuir_temp.move(x, y)  # Move o botão de diminuir temperatura para a posição especificada.

    def set_tamanho_botao_aumentar_temp(self, width, height):
        self.botao_aumentar_temp.setFixedSize(width, height)  # Define o tamanho do botão de aumentar temperatura.

    def set_tamanho_botao_diminuir_temp(self, width, height):
        self.botao_diminuir_temp.setFixedSize(width, height)  # Define o tamanho do botão de diminuir temperatura.

    def aumentar_temperatura(self):
        self.temperatura += 0.1  # Aumenta a temperatura.
        self.temperatura = min(self.temperatura, 1.0)  # Limita a temperatura a 1.0.
        self.visor_temperatura.setText(f"{self.temperatura:.1f}")  # Atualiza o visor de temperatura.

    def diminuir_temperatura(self):
        self.temperatura -= 0.1  # Diminui a temperatura.
        self.temperatura = max(self.temperatura, 0.0)  # Limita a temperatura a 0.0.
        self.visor_temperatura.setText(f"{self.temperatura:.1f}")  # Atualiza o visor de temperatura.

    def mudar_modelo_gpt3(self):
        remetente = self.sender()  # Obtém o remetente do sinal.
        if remetente == self.botao_GPT3:
            self.modelo = "gpt-3.5-turbo-16k"  # Altera o modelo para GPT-3.5.
            self.resultados.append("<b>Modelo alterado para:</b> GPT-3.5")

    def mudar_modelo_gpt4(self):
        remetente = self.sender()  # Obtém o remetente do sinal.
        if remetente == self.botao_GPT4:
            self.modelo = "gpt-4-0613"  # Altera o modelo para GPT-4.
            self.resultados.append("<b>Modelo alterado para:</b> GPT-4")

    def set_posicao_botao_gpt3(self, botao_GPT3, x, y):
        botao_GPT3.move(x, y)  # Move o botão GPT3 para a posição especificada.

    def set_posicao_botao_gpt4(self, botao_GPT4, x, y):
        botao_GPT4.move(x, y)  # Move o botão GPT4 para a posição especificada.

    def ajustar_altura_entrada(self):
        altura_maxima = 75  # Altura máxima da entrada de texto.
        altura_documento = self.entrada.document().size().height()  # Obtém a altura do documento.
        nova_altura = min(altura_documento, altura_maxima)  # Calcula a nova altura.
        nova_altura_int = int(nova_altura)  # Converte a nova altura para inteiro.
        self.entrada.setFixedHeight(nova_altura_int)  # Define a altura da entrada de texto.

    def set_tamanho_visor(self, width, height):
        self.visor_temperatura.setFixedSize(width, height)  # Define o tamanho do visor de temperatura.

    def set_tamanho_entrada(self, width, height):
        self.entrada.setFixedSize(width, height)  # Define o tamanho da entrada de texto.

    def set_tamanho_botao_enviar(self, width, height):
        self.botao_enviar.setFixedSize(width, height)  # Define o tamanho do botão de enviar.

    def set_tamanho_botao_gpt3(self, width, height):
        self.botao_GPT3.setFixedSize(width, height)  # Define o tamanho do botão GPT3.

    def set_tamanho_botao_gpt4(self, width, height):
        self.botao_GPT4.setFixedSize(width, height)  # Define o tamanho do botão GPT4.

    def set_tamanho_botao_limpar(self, width, height):
        self.botao_limpar.setFixedSize(width, height)  # Define o tamanho do botão de limpar.

    def set_tamanho_resultados(self, width, height):
        self.resultados.setFixedSize(width, height)  # Define o tamanho da área de resultados.
        self.resultados.setAlignment(Qt.AlignLeft)  # Alinha o texto à esquerda.

    def set_cor_fundo_entrada(self, cor):
        self.entrada.setStyleSheet(f"background-color: {cor}; border: 1px solid #000000; border-radius: 10px; color: #ffffff;")
        # Define a cor de fundo, borda e texto da entrada de texto.
        fonte = QFont()
        fonte.setPointSize(12)  # Define o tamanho da fonte.
        self.entrada.setFont(fonte)  # Aplica a fonte à entrada de texto.

    def set_cor_fundo_botao_enviar(self, cor):
        self.botao_enviar.setStyleSheet(f"background-color: {cor}; border: 1px solid #000000; border-radius: 10px;")
        # Define a cor de fundo e borda do botão de enviar.

    def set_cor_fundo_botao_limpar(self, cor):
        self.botao_limpar.setStyleSheet(f"background-color: {cor}; border: 1px solid #000000; border-radius: 10px;")
        # Define a cor de fundo e borda do botão de limpar.

    def set_cor_fundo_botao_gpt3(self, cor):
        self.botao_GPT3.setStyleSheet(f"background-color: {cor}; border: 1px solid #000000; border-radius: 10px; color: #ffffff;")
        # Define a cor de fundo, borda e texto do botão GPT3.

    def set_cor_fundo_botao_gpt4(self, cor):
        self.botao_GPT4.setStyleSheet(f"background-color: {cor}; border: 1px solid #000000; border-radius: 10px; color: #ffffff;")
        # Define a cor de fundo, borda e texto do botão GPT4.

    def set_cor_fundo_botao_aumentar_temp(self, cor):
        self.botao_aumentar_temp.setStyleSheet(f"background-color: {cor}; border: 1px solid #000000; border-radius: 10px; color: #ffffff;")
        # Define a cor de fundo, borda e texto do botão de aumentar temperatura.

    def set_cor_fundo_botao_diminuir_temp(self, cor):
        self.botao_diminuir_temp.setStyleSheet(f"background-color: {cor}; border: 1px solid #000000; border-radius: 10px; color: #ffffff;")
        # Define a cor de fundo, borda e texto do botão de diminuir temperatura.

    def set_cor_fundo_visor(self, cor):
        self.visor_temperatura.setStyleSheet(f"background-color: {cor}; border: 1px solid #000000; border-radius: 10px; color: #ffffff;")
        # Define a cor de fundo, borda e texto do visor de temperatura.

    def set_cor_fundo_resultados(self, cor):
        self.resultados.setStyleSheet(f"background-color: {cor}; border: 1px solid #000000; border-radius: 10px; color: #ffffff;")
        # Define a cor de fundo, borda e texto da área de resultados.
        fonte = QFont()
        fonte.setPointSize(11)  # Define o tamanho da fonte.
        self.resultados.setFont(fonte)  # Aplica a fonte à área de resultados.

    def set_cor_fundo_app(self, cor):
        self.setStyleSheet(f"background-color: {cor};")  # Define a cor de fundo da aplicação.

    def set_cor_fundo_contador(self, cor):
        self.contador_tokens.setStyleSheet(f"background-color: {cor}; border: 1px solid #3c3c3c; border-radius: 10px; color: #ffffff;")
        # Define a cor de fundo, borda e texto do contador de tokens.
        fonte = QFont()
        fonte.setPointSize(10)  # Define o tamanho da fonte.
        self.contador_tokens.setFont(fonte)  # Aplica a fonte ao contador de tokens.

    # Métodos para enviar mensagens, limpar campos, ajustar temperatura, trocar modelos, e atualizar contadores.
    def enviar_mensagem(self):
        mensagem = self.entrada.toPlainText()  # Obtém a mensagem da entrada de texto.
        self.label_status.setText("Carregando resposta...")  # Define o texto do status.
        self.label_status.show()  # Mostra o status.
        QApplication.processEvents()  # Atualiza a interface do usuário.
        mensagem_usuario = {"role": "user", "content": mensagem}  # Cria um dicionário com a mensagem do usuário.
        self.historico_conversa.append(mensagem_usuario)  # Adiciona a mensagem ao histórico de conversa.
        self.trabalhador = Worker(self, mensagem)  # Cria uma instância da classe Worker.
        self.trabalhador.terminado.connect(self.atualizar_ui)  # Conecta o sinal terminado ao método atualizar_ui.
        self.trabalhador.start()  # Inicia o thread.

    def limpar_campos(self):
        self.entrada.clear()  # Limpa a entrada de texto.
        self.resultados.clear()  # Limpa a área de resultados.

    def set_tamanho_contador(self, width, height):
        self.contador_tokens.setFixedSize(width, height)  # Define o tamanho do contador de tokens.
        self.contador_tokens.setAlignment(Qt.AlignTop)  # Alinha o texto no topo.

    def atualizar_contador_caracteres(self):
        mensagem = self.entrada.toPlainText()  # Obtém a mensagem da entrada de texto.
        self.contador_caracteres = len(mensagem)  # Atualiza a contagem de caracteres.
        self.atualizar_texto_contador()  # Atualiza o texto do contador.

    def atualizar_contagem_tokens(self):
        mensagem = self.entrada.toPlainText()  # Obtém a mensagem da entrada de texto.
        tokens_mensagem = tokenizador.encode(mensagem)  # Codifica a mensagem em tokens.
        self.tokens_mensagem = len(tokens_mensagem)  # Atualiza a contagem de tokens.
        self.atualizar_texto_contador()  # Atualiza o texto do contador.
        self.timer_contagem_tokens.stop()  # Para o timer.

    def atualizar_texto_contador(self):
        texto_contador_tokens = f"Tokens na mensagem: {self.tokens_mensagem}, Tokens na resposta: {self.tokens_resposta}, Caracteres: {self.contador_caracteres}"
        # Texto com a contagem de tokens e caracteres.
        self.contador_tokens.setText(texto_contador_tokens)  # Define o texto no contador de tokens.

    def atualizar_ui(self, mensagem, resposta, contagem_tokens):
        self.label_status.hide()  # Esconde o status.
        QApplication.processEvents()  # Atualiza a interface do usuário.
        if resposta and 'choices' in resposta and len(resposta['choices']) > 0:
            resposta_modelo = resposta['choices'][0]['message']['content']  # Obtém a resposta da API.
            self.adicionar_mensagem_ui("EU", mensagem, Qt.AlignRight)  # Adiciona a mensagem do usuário à UI.
            self.adicionar_mensagem_ui("GPT", resposta_modelo, Qt.AlignLeft)  # Adiciona a resposta da API à UI.
            mensagem_chatbot = {"role": "assistant", "content": resposta_modelo}  # Cria um dicionário com a resposta da API.
            self.historico_conversa.append(mensagem_chatbot)  # Adiciona a resposta ao histórico de conversa.
            self.tokens_resposta = contagem_tokens  # Atualiza a contagem de tokens da resposta.
            self.atualizar_texto_contador()  # Atualiza o texto do contador.
        else:
            self.resultados.append("<b>Erro:</b> Não foi possível obter uma resposta.")  # Mensagem de erro.

    def adicionar_mensagem_ui(self, remetente, mensagem, alinhamento):
        cursor = self.resultados.textCursor()  # Obtém o cursor da área de resultados.
        cursor.movePosition(QTextCursor.End)  # Move o cursor para o final.
        formato_bloco = QTextBlockFormat()  # Cria um formato de bloco de texto.
        formato_bloco.setAlignment(alinhamento)  # Define o alinhamento do bloco.
        cursor.insertBlock(formato_bloco)  # Insere o bloco de texto.
        mensagem_formatada = f"<b>{remetente}:</b><br>{mensagem}<br>"  # Formata a mensagem.
        cursor.insertHtml(mensagem_formatada)  # Insere a mensagem formatada como HTML.
        self.resultados.append(" ")  # Adiciona um espaço após a mensagem.

# Bloco principal para iniciar a aplicação.
if __name__ == "__main__":
    app = QApplication(sys.argv)  # Cria a aplicação Qt.
    app_chat = ChatApp()  # Cria uma instância da aplicação de chat.
    app_chat.show()  # Mostra a janela da aplicação.

    # Configurações adicionais de UI para cor e tamanho.
    app_chat.set_tamanho_visor(65, 30)  # Define o tamanho do visor de temperatura.
    app_chat.set_tamanho_entrada(545, 50)  # Define o tamanho da entrada de texto.
    app_chat.set_tamanho_botao_enviar(50, 50)  # Define o tamanho do botão de enviar.
    app_chat.set_tamanho_botao_limpar(50, 50)  # Define o tamanho do botão de limpar.
    app_chat.set_tamanho_botao_aumentar_temp(30, 30)  # Define o tamanho do botão de aumentar temperatura.
    app_chat.set_tamanho_botao_diminuir_temp(30, 30)  # Define o tamanho do botão de diminuir temperatura.
    app_chat.set_tamanho_botao_gpt3(65, 30)  # Define o tamanho do botão GPT3.
    app_chat.set_tamanho_botao_gpt4(65, 30)  # Define o tamanho do botão GPT4.
    app_chat.set_tamanho_resultados(650, 580)  # Define o tamanho da área de resultados.
    app_chat.set_tamanho_contador(650, 30)  # Define o tamanho do contador de tokens.

    app_chat.set_cor_fundo_visor("#515151")  # Define a cor de fundo do visor de temperatura.
    app_chat.set_cor_fundo_entrada("#515151")  # Define a cor de fundo da entrada de texto.
    app_chat.set_cor_fundo_botao_enviar("#4CAF50")  # Define a cor de fundo do botão de enviar.
    app_chat.set_cor_fundo_botao_limpar("#FF0000")  # Define a cor de fundo do botão de limpar.
    app_chat.set_cor_fundo_resultados("#515151")  # Define a cor de fundo da área de resultados.
    app_chat.set_cor_fundo_botao_gpt3("#515151")  # Define a cor de fundo do botão GPT3.
    app_chat.set_cor_fundo_botao_gpt4("#515151")  # Define a cor de fundo do botão GPT4.
    app_chat.set_cor_fundo_botao_aumentar_temp("#4CAF50")  # Define a cor de fundo do botão de aumentar temperatura.
    app_chat.set_cor_fundo_botao_diminuir_temp("#4CAF50")  # Define a cor de fundo do botão de diminuir temperatura.
    app_chat.set_cor_fundo_contador("#3c3c3c")  # Define a cor de fundo do contador de tokens.
    app_chat.set_cor_fundo_app("#3c3c3c")  # Define a cor de fundo da aplicação.

    sys.exit(app.exec_())  # Executa o loop principal da aplicação.
