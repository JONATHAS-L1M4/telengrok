# 🖥️ Telengrok - Conecte-se ao seu PC via Telegram + Ngrok

![Texto Alternativo](https://github.com/JONATHAS-L1M4/telengrok/blob/main/Telengrok.png)

Este projeto permite que você **inicie uma conexão RDP (Área de Trabalho Remota)** com seu PC **via Telegram**, utilizando o poder do `ngrok` para expor a porta 3389 de forma segura e prática.

---

## 🚀 Funcionalidades

```
- Integração com **Telegram Bot API**  
- Interface gráfica moderna com **CustomTkinter**  
- Geração automática do link RDP: `mstsc /v:<ip:porta>`  
- Sistema de **código de verificação** para segurança  
- Armazenamento seguro de `TOKEN` e `CHAT_ID`  
- Comandos interativos pelo Telegram  
```
---

## 🧰 Pré-requisitos

```bash
pip install pyTelegramBotAPI psutil requests customtkinter
```

- `ngrok.exe` em `C:\Windows\ngrok.exe`  
- `ngrok.exe` adicionado às variáveis de ambiente do Windows  

---

## ▶️ Como usar

```bash
git clone https://github.com/seu-usuario/telengrok.git
cd telengrok
python telengrok.py
```

1. Insira o **TOKEN do seu bot do Telegram**  
2. Envie `/register` no bot  
3. Envie o código gerado na interface  
4. Use os comandos:

```
/start     → Inicia conexão com seu PC via mstsc  
/reset     → Gera uma nova URL ngrok
/stop      → Encerra o túnel do **ngrok** e fecha a conexão.  
/default   → Apaga configurações salvas (token e ID)  
/help      → Lista os comandos  
/config    → Abre a pasta de configuração  
```

---

## 📁 Estrutura do Projeto

```
📂 Telengrok
 └── telengrok.py
```

Configurações são salvas em:

```
C:\Users\<seu_usuario>\AppData\Local\Temp\telengrok\config.json
```

---

## ⚙️ Sobre o ngrok

Local do `ngrok.exe`:

```
C:\Windows\ngrok.exe
```

### Adicionar token de autenticação:

```bash
ngrok config add-authtoken SEU_AUTHTOKEN
```

---

## ⚡ Inicialização automática com o Windows

### Opção 1: Copiar o executável

```bash
pyinstaller --noconsole --onefile telengrok.py
```

Copiar `telengrok.exe` para:

```
C:\Users\<seu_usuario>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

### Opção 2: Criar atalho

Criar atalho do `telengrok.exe` e mover para:

```
C:\Users\<seu_usuario>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

---

## 🔐 Segurança

- Bot responde apenas ao ID registrado  
- Link do ngrok é temporário e rotativo  

---

## 📦 Empacotar como .exe

```bash
pyinstaller --noconsole --onefile telengrok.py
```

---

## 📃 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais detalhes.
