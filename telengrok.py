# Importações necessárias para funcionamento do programa
import os
import json
import psutil  # Para checar processos do sistema
import requests  # Para fazer requisições HTTP
import subprocess  # Para rodar comandos no terminal
from datetime import datetime  # Para checar data/hora
import telebot  # Biblioteca para criar bots no Telegram
import customtkinter as ctk  # Interface moderna baseada no Tkinter
from tkinter import messagebox
from time import sleep
import random  # Para gerar códigos aleatórios
import string  # Para gerar strings aleatórias
import tempfile  # Para usar pastas temporárias do sistema

# Define o caminho onde o config.json será salvo (pasta temporária)
config_dir = os.path.join(tempfile.gettempdir(), "telengrok")
config_file = os.path.join(config_dir, "config.json")

# Cria a pasta caso não exista
if not os.path.exists(config_dir):
    os.makedirs(config_dir)

# Cria um arquivo JSON vazio se ainda não existir
if not os.path.exists(config_file):
    with open(config_file, "w") as f:
        f.write("{}")

# Variáveis globais para controle do código de verificação
verification_code = None
code_status = {"OPEN": True}

# Define aparência do app com CustomTkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Função para salvar token e chat_id no config.json
def save_config(token, chat_id=None):
    data = {"TOKEN": token}
    if chat_id:
        data["CHAT_ID"] = chat_id
    with open(config_file, "w") as f:
        json.dump(data, f)

# Função para carregar dados do config.json
def load_config():
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
            return config.get("TOKEN"), config.get("CHAT_ID")
    return None, None

# Verifica se o ngrok está parado
def is_ngrok_stopped():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'ngrok.exe':
            return False
    return True

# Inicia o ngrok (porta 3389 para RDP)
def start_ngrok():
    ngrok_path = "ngrok.exe"
    args = ["tcp", "3389"]
    try:
        process = subprocess.Popen([ngrok_path] + args, creationflags=subprocess.CREATE_NO_WINDOW)
        print(f"ngrok iniciado com PID {process.pid}")
    except FileNotFoundError:
        print("Caminho do ngrok incorreto.")
    except Exception as e:
        print(f"Erro ao iniciar o ngrok: {e}")

# Reinicia o ngrok
def reset_ngrok():
    subprocess.run(['taskkill', '/f', '/im', 'ngrok.exe'])
    start_ngrok()

# Pega a URL pública do ngrok
def get_public_url():
    while True:
        try:
            r = requests.get('http://127.0.0.1:4040/api/tunnels')
            url = json.loads(r.text)["tunnels"][0]['public_url']
            return url.replace("tcp://", "")
        except:
            sleep(1)

# Remove o chat_id e token salvos
def reset_config():
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
        if "CHAT_ID" in config:
            del config["CHAT_ID"]
            del config["TOKEN"]
            with open(config_file, "w") as f:
                json.dump(config, f)
            return True
    return False

# Inicia o bot do Telegram
def start_telegram_bot(token):
    bot = telebot.TeleBot(token)
    _, saved_chat_id = load_config()

    @bot.message_handler(commands=['start'])
    def cmd_start(message):
        chat_id = message.chat.id
        _, saved_chat_id = load_config()
        if str(chat_id) != str(saved_chat_id):
            return
        if not is_ngrok_stopped():
            bot.send_message(chat_id, f'💻 Conecte-se ao seu PC:\nmstsc /v:{get_public_url()}')
        else:
            start_telebot_loop(bot, chat_id)

    @bot.message_handler(commands=['reset'])
    def cmd_reset(message):
        chat_id = message.chat.id
        _, saved_chat_id = load_config()
        if str(chat_id) != str(saved_chat_id):
            return
        reset_ngrok()
        bot.send_message(chat_id, f'🔄 Nova conexão gerada:\nmstsc /v:{get_public_url()}')

    @bot.message_handler(commands=['default'])
    def cmd_delete_id(message):
        chat_id = message.chat.id
        _, saved_chat_id = load_config()
        if str(chat_id) != str(saved_chat_id):
            return
        if reset_config():
            bot.send_message(chat_id, "⚠ Todos os dados foram apagados (TOKEN e ID). Reinicie o app para configurar novamente.")
            initial_window()

    @bot.message_handler(commands=['help'])
    def cmd_help(message):
        help_text = (
            "👋 Olá! Aqui estão os comandos disponíveis:\n\n"
            "/register - Registrar seu ID do Telegram para conectar ao PC.\n"
            "/start - Iniciar a conexão com seu PC via mstsc.\n"
            "/reset - Reiniciar a conexão e gerar uma nova URL do ngrok.\n"
            "/default - Apaga todos os dados salvos (TOKEN e ID).\n"
            "/config - Abre a pasta de configuração (config.json).\n"
            "/help - Mostrar esta mensagem de ajuda."
        )
        bot.send_message(message.chat.id, help_text)

    @bot.message_handler(commands=['config'])
    def cmd_config(message):
        _, local_saved_chat_id = load_config()
        if local_saved_chat_id:
            subprocess.run(['explorer', config_dir])

    @bot.message_handler(func=lambda message: True)
    def respond_to_message(message):
        global verification_code
        received_text = message.text.strip()
        chat_id = message.chat.id
        if received_text == "/register":
            _, local_saved_chat_id = load_config()
            if local_saved_chat_id:
                pass
            else:
                if code_status["OPEN"] == True:
                    bot.send_message(chat_id, f"📱 Digite o código recebido no seu computador!")
                    generate_verification_code()
        elif received_text.upper() == verification_code:
            _, local_saved_chat_id = load_config()
            if local_saved_chat_id:
                bot.send_message(chat_id, f"⚠ O ID {chat_id} já está registrado!")
                return
            save_config(token, chat_id)
            sleep(1)
            bot.send_message(chat_id, f"✅ ID {chat_id} registrado com sucesso!")
            verification_window.destroy()

    # Loop que atualiza a URL e envia se ela mudar
    def start_telebot_loop(bot, chat_id):
        public_url = None
        while True:
            sleep(5)
            if not is_ngrok_stopped():
                reset_ngrok()
            if datetime.now().strftime('%H%M') == "0000":
                reset_ngrok()
            current_url = get_public_url()
            if current_url != public_url:
                bot.send_message(chat_id, f'⚠ Conecte-se ao seu PC:\nmstsc /v:{current_url}')
                public_url = current_url

    # Reinicia o ngrok e o bot
    reset_ngrok()
    while True:
        try:
            bot.polling(none_stop=True)
        except:
            pass

# Testa se o token do Telegram é válido
def test_token(token):
    try:
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe")
        return response.json().get("ok", False)
    except Exception as e:
        print(f"Erro ao testar TOKEN: {e}")
        return False

# Carrega o token salvo, se existir
saved_token, _ = load_config()

# Gera a janela com o código de verificação
def generate_verification_code():
    if code_status["OPEN"] == True:
        pass
    else:
        return

    global verification_code, verification_window
    verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6)).upper()

    verification_window = ctk.CTk()
    verification_window.title("Código de Verificação")
    verification_window.geometry("250x110")
    verification_window.resizable(False, False)
    verification_window.attributes("-topmost", True)

    ctk.CTkLabel(verification_window, text="Código de verificação", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5, 5))
    ctk.CTkLabel(verification_window, text=verification_code, font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(1, 5))
    countdown_label = ctk.CTkLabel(verification_window, text="Fechando em 30 segundos...", font=ctk.CTkFont(size=12))
    countdown_label.pack(pady=(1, 5))

    def update_timer(time_remaining):
        if time_remaining > 0:
            countdown_label.configure(text=f"Fechando em {time_remaining} segundos...")
            verification_window.after(1000, update_timer, time_remaining - 1)
            code_status.update({"OPEN": False})
        else:
            code_status.update({"OPEN": True})
            verification_window.destroy()

    update_timer(30)
    verification_window.mainloop()

# Interface inicial para inserir o TOKEN do bot
def initial_window():
    window = ctk.CTk()
    window.title("Configurar Bot")
    window.geometry("280x120")
    window.resizable(False, False)
    window.attributes("-topmost", True)

    token_label = ctk.CTkLabel(window, text="TELEGRAM_BOT_TOKEN:")
    token_label.pack(pady=0)

    token_entry = ctk.CTkEntry(window, width=240)
    token_entry.pack(pady=5)

    def on_save():
        token = token_entry.get().strip()
        if token:
            if test_token(token):
                save_config(token)
                messagebox.showinfo("Salvo", "TOKEN salvo com sucesso.\nUse /register no Telegram.")
                window.destroy()
                start_telegram_bot(token)
            else:
                messagebox.showerror("Erro", "TOKEN inválido! Por favor, insira um TOKEN válido.")
        else:
            messagebox.showerror("Erro", "Digite o TOKEN para continuar.")

    save_button = ctk.CTkButton(window, width=240, text="Salvar e Iniciar", command=on_save)
    save_button.pack(pady=5)

    window.mainloop()

# Início do programa principal
if saved_token:
    start_telegram_bot(saved_token)
else:
    initial_window()
