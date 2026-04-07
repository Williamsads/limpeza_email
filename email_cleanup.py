import imaplib
import email
from email.header import decode_header
import datetime
import getpass
import math
import sys
import re

def format_size(size_bytes):
    """Formata o tamanho de bytes para um formato amigável (B, KB, MB, GB)."""
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def get_decoded_subject(msg):
    """Obtém o assunto do e-mail decodificado adequadamente."""
    subject = msg.get("Subject", "")
    if not subject:
        return "Sem Assunto"
    
    decoded_list = decode_header(subject)
    subject_str = ""
    for decoded_part, encoding in decoded_list:
        if isinstance(decoded_part, bytes):
            subject_str += decoded_part.decode(encoding if encoding else "utf-8", errors="ignore")
        else:
            subject_str += str(decoded_part)
    return subject_str

def main():
    print("=== Limpeza de E-mail via IMAP ===\n")

    # 1. Configurações interativas do servidor e conta
    imap_server = input("Servidor IMAP (ex: imap.gmail.com): ").strip() or "imap.gmail.com"
    email_user = input("Seu e-mail: ").strip()
    
    print("\n[Nota: Para Gmail e accounts com 2FA, use uma 'Senha de App' (App Password)]")
    email_pass = getpass.getpass("Senha ou Token: ")
    
    mailbox = input("\nCaixa de entrada (padrão: INBOX, Gmail geralmente é suporte a '[Gmail]/Trash' para lixeira. Deixe vazio para INBOX.): ").strip() or "INBOX"

    # Configuração dos filtros de forma interativa
    try:
        min_size_mb = float(input("\nTamanho mínimo em MB (aperte ENTER para 5): ").strip() or "5")
    except ValueError:
        min_size_mb = 5.0

    try:
        older_than_years = int(input("Mais antigo que quantos anos? (aperte ENTER para 1): ").strip() or "1")
    except ValueError:
        older_than_years = 1

    # 2. Conectando e Autenticando
    print(f"\nConectando a {imap_server}...")
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_user, email_pass)
        print("✅ Login realizado com sucesso!\n")
    except Exception as e:
        print(f"❌ Erro ao conectar ou autenticar: {e}")
        sys.exit(1)

    # Tenta acessar a caixa de e-mail escolhida
    status, messages = mail.select(f'"{mailbox}"')
    if status != "OK":
        print(f"❌ Não foi possível acessar a caixa '{mailbox}'. Listando caixas disponíveis:")
        typ, data = mail.list()
        for box in data:
            print(box.decode())
        mail.logout()
        sys.exit(1)

    print(f"Buscando e-mails maiores que {min_size_mb}MB OU mais antigos que {older_than_years} ano(s) em '{mailbox}'...\n")

    # 3. Preparando formatacao de dados para pesquisa IMAP
    hoje = datetime.date.today()
    data_limite = hoje - datetime.timedelta(days=365 * older_than_years)
    # Servidor IMAP espera datas no formato DD-Mon-YYYY
    data_imap = data_limite.strftime("%d-%b-%Y")
    
    tamanho_bytes = int(min_size_mb * 1024 * 1024)

    # 4. Busca
    print(f"⏳ Procurando e-mails pesados ( > {min_size_mb}MB )...")
    status, data_size = mail.search(None, f'LARGER {tamanho_bytes}')
    ids_size = set(data_size[0].split()) if status == 'OK' and data_size[0] else set()

    print(f"⏳ Procurando e-mails antigos ( Anteriores a {data_imap} )...")
    status, data_date = mail.search(None, f'BEFORE "{data_imap}"')
    ids_date = set(data_date[0].split()) if status == 'OK' and data_date[0] else set()

    # Únião dos conjuntos (OU)
    ids_encontrados = ids_size.union(ids_date)

    if not ids_encontrados:
        print("✅ Nenhum e-mail bate com os critérios de busca. Nada a fazer.")
        mail.close()
        mail.logout()
        return

    print(f"\n✅ Foram encontrados {len(ids_encontrados)} e-mail(s).")
    print("📥 Extraindo detalhes (isso pode demorar uns segundos dependendo da quantidade)...\n")

    emails_para_apagar = []
    espaco_total_bytes = 0

    # 5. Listando os detalhes sem marcar o email como lido (usando BODY.PEEK)
    for e_id in list(ids_encontrados):
        status, msg_data = mail.fetch(e_id, '(RFC822.SIZE BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)])')
        
        if status != 'OK':
            continue

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                resposta_str = response_part[0].decode(errors='ignore')
                
                # Coleta o tamanho via regex direto do response server
                size_str = 0
                match = re.search(r'RFC822\.SIZE\s+(\d+)', resposta_str)
                if match:
                    size_str = int(match.group(1))

                # Pega as informações do Header
                msg = email.message_from_bytes(response_part[1])
                assunto = get_decoded_subject(msg)
                remetente = msg.get("From", "Desconhecido")
                data_email = msg.get("Date", "Desconhecida")

                emails_para_apagar.append({
                    "id": e_id,
                    "subject": assunto,
                    "from": remetente,
                    "date": data_email,
                    "size": size_str
                })
                espaco_total_bytes += size_str

    # 6. Exibir os resultados para o usuário analisar
    print("-" * 50)
    for i, e in enumerate(emails_para_apagar, 1):
        print(f"{i}. [Tamanho: {format_size(e['size'])}] - Data: {e['date']}")
        print(f"   De: {e['from']}")
        print(f"   Ass: {e['subject']}\n")
    print("-" * 50)

    print(f"Total de e-mails para deletar: {len(emails_para_apagar)}")
    print(f"Espaço estimado a ser liberado: {format_size(espaco_total_bytes)}")

    # 7. Solicita confirmação antes de destruir
    print("\n⚠️  ATENÇÃO: A operação de expurgo os apaga da caixa selecionada.")
    confirmacao = input("Você deseja REALMENTE apagar DEFINITIVAMENTE estes e-mails? (S/N): ").strip().upper()

    if confirmacao == 'S':
        print("\n🗑️ Marcando e-mails para exclusão...")
        for e in emails_para_apagar:
            mail.store(e["id"], '+FLAGS', '\\Deleted')
        
        # 8. Remover fisicamente da pasta atual
        print("🧹 Removendo permanentemente (Expunge)...")
        mail.expunge()
        
        # Lidar com e-mails da Lixeira do provedor... 
        # (Expunging do INBOX às vezes move pro trash em alguns emails (ex. Gmail com configuração default), 
        # às vezes apaga de vez. De qualquer forma o expunge libera do Inbox.
        print(f"✅ Sucesso! {format_size(espaco_total_bytes)} de espaço liberado.")
        print("Nota: Se estiver no Gmail, confirme se eles não foram copiados para a Lixeira.")
    else:
        print("\n❌ Operação cancelada pelo usuário. Os e-mails foram mantidos intactos.")

    # 9. Cleanup final
    print("\nFechando conexão...")
    mail.close()
    mail.logout()
    print("Concluído!")

if __name__ == "__main__":
    main()
