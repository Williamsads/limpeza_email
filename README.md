# 🧹 Limpeza de E-mail via IMAP (Python)

Este é um script Python interativo de linha de comando que se conecta à sua conta de e-mail através do protocolo IMAP para encontrar, listar e apagar em massa e-mails que possuam anexos muito pesados (grandes) ou que sejam muito antigos.  
Sua finalidade principal é ajudar a resgatar espaço de armazenamento valioso no seu provedor de e-mail de maneira automatizada e segura, sem depender do uso lento dos aplicativos e sites padrão dos provedores.

## 🚀 Principais Funcionalidades

- **Busca por Tamanho (Anexos Pesados):** Permite configurar e encontrar e-mails que excedam um certo limite em Megabytes (ex: > 5MB).
- **Busca por Idade:** Filtre mensagens que já possuem vários anos de antiguidade e não são mais necessárias.
- **Rápido e Otimizado:** Utiliza os operadores nativos de busca no servidor (`SEARCH LARGER` e `BEFORE`), economizando sua banda de internet ao baixar apenas os metadados (cabeçalhos) para listar.
- **Proteção e Listagem:** Antes da deleção, o aplicativo exibe em formato tabular/lista na tela quais foram os e-mails encontrados em seus filtros (Assunto, Data e Remetente) informando também a estimativa total do espaço a ser economizado.
- **Expurgo Físico:** Utiliza o sub-comando `EXPUNGE` do protocolo IMAP para destruir as marcações que estavam na sinalização de lixeira.
- **Stand-alone Nativo:** Todo o código foi escrito utilizando puramente as bibliotecas internas do Python (Módulos `imaplib`, `email`, `re`, `datetime`). Não precisa de nenhum `pip install`.

## ⚙️ Pré-requisitos

1. **Python 3.x** instalado em seu computador (Windows/Linux/Mac).
2. **Acesso IMAP Habilitado** na sua conta de e-mail. (Alguns provedores exigem que seja marcado um "check", no site via web, para usar IMAP).
3. **Senha de Aplicativo (2FA):** 
   - Hoje em dia o Gmail, Outlook, Yahoo e Apple não permitem o uso da senha normal da conta no código.  
   - Entre nas configurações de segurança do provedor habilitado para login de dois fatores (2FA) e gere uma "[Senha de App](https://support.google.com/accounts/answer/185833?hl=pt-BR)". É basicamente um código geralmente de 16 letras que você colará no script.

## 💻 Como instalar e rodar

Abra o Terminal/Prompt de Comando de sua preferência:

```bash
# 1. Clone ou baixe este repositório
git clone https://github.com/Williamsads/limpeza_email.git
cd limpeza_email

# 2. Inicie o script Python
python email_cleanup.py
```

O ambiente será inteiramente interativo na língua portuguesa. Você apenas preencherá por linha:
1. O Servidor (ex: `imap.gmail.com` ou `imap.mail.yahoo.com`).
2. O Email e a Senha.
3. Os filtros (`TamanhoMB` e `AnosAntigos`).

Caso encontre itens, confirme usando (S) quando solicitado a destruir.

## ⚠️ Sobre o "Apagamento Permanente" (Expunge) e Comportamentos (Gmail)

Na maioria dos provedores puramente IMAP, quando enviamos um `/Deleted` junto de um `.expunge()`, o provedor detona o arquivo.
Mas o Gmail implementa IMAP de modo particular. A configuração padrão do Gmail pode sobrepor o comando e invés de apagar fisicamente de forma instantânea, mandar a mensagem recém excluída do `INBOX` para uma pasta de label "Lixeira", que auto limpa a cada 30 dias.  
Se após o expurgo o seu espaço em disco continuar baixo ou inalterado, é necessário acessar o Gmail pela web (site), ir em **"Lixeira"** e clicar no botão **"Esvaziar a lixeira agora"**.

---
*Escrito e documentado para facilitar rotinas de limpezas pesadas.*
