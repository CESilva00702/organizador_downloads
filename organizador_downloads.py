import os
import shutil
import re
import argparse
import json
import time
import logging

# --- CONFIGURAÇÃO ---
# ATENÇÃO: Altere o caminho abaixo para o caminho da sua pasta de Downloads.
# Exemplos:
# Windows: "D:\\Downloads"
# macOS: "/Users/SeuUsuario/Downloads"
# Linux: "/home/SeuUsuario/Downloads"
# Default to the user's standard Downloads folder in their home directory (cross-platform)
PASTA_DOWNLOADS = os.path.join(os.path.expanduser('~'), 'Downloads')

# --- LÓGICA DO SCRIPT ---

def extrair_nome_programa(nome_arquivo):
    """Tenta extrair um nome de programa do nome do arquivo."""
    # Remove a extensão do arquivo
    nome_base = os.path.splitext(nome_arquivo)[0]

    # Remove versões (ex: nome-2.3.1, nome_v1.0) e outros padrões comuns
    nome_limpo = re.sub(r'[\s._-]?v?\d+(\.\d+)*', '', nome_base, flags=re.IGNORECASE)
    nome_limpo = re.sub(r'[\s._-]?(x86|x64|win32|win64|setup|installer)', '', nome_limpo, flags=re.IGNORECASE)
    nome_limpo = nome_limpo.replace('_', ' ').replace('-', ' ').strip()

    # Pega a primeira palavra como um candidato a nome de programa
    if nome_limpo:
        return nome_limpo.split()[0].capitalize()
    return "Outros"


def safe_move(src, dst, dry_run=False, suffix_mode='counter', logger=None):
    """Move src para dst; se dst existir, adiciona um sufixo incremental ou timestamp antes da extensão.

    Parâmetros:
    - dry_run: se True, apenas imprime ação.
    - suffix_mode: 'counter' (ex: name (1).ext) ou 'timestamp' (ex: name_20251017T132500.ext)
    """
    if dry_run:
        if logger:
            logger.info(f"[dry-run] mover: '{src}' -> '{dst}'")
        else:
            print(f"[dry-run] mover: '{src}' -> '{dst}'")
        return

    dst_dir = os.path.dirname(dst)
    base = os.path.basename(dst)
    name, ext = os.path.splitext(base)
    candidate = dst

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok=True)

    if suffix_mode == 'counter':
        i = 1
        while os.path.exists(candidate):
            candidate = os.path.join(dst_dir, f"{name} ({i}){ext}")
            i += 1
    else:  # timestamp
        if os.path.exists(candidate):
            ts = time.strftime('%Y%m%dT%H%M%S')
            candidate = os.path.join(dst_dir, f"{name}_{ts}{ext}")

    shutil.move(src, candidate)
    if logger:
        logger.debug(f"safe_move: '{src}' -> '{candidate}'")


def organizar_downloads(pasta_alvo, dry_run=False, verbose=False, backup_dir=None, suffix_mode='counter', logger=None):
    """
    Organiza os arquivos na pasta de downloads em subpastas por tipo e nome.
    """
    if not os.path.isdir(pasta_alvo):
        if verbose:
            if logger:
                logger.error(f"Erro: O diretório '{pasta_alvo}' não foi encontrado.")
            else:
                print(f"Erro: O diretório '{pasta_alvo}' não foi encontrado.")
        return

    if verbose:
        if logger:
            logger.info(f"Iniciando a organização da pasta: {pasta_alvo}")
        else:
            print(f"Iniciando a organização da pasta: {pasta_alvo}")

    # Itera sobre cada item no diretório de downloads
    for nome_arquivo in os.listdir(pasta_alvo):
        caminho_arquivo_origem = os.path.join(pasta_alvo, nome_arquivo)

        # Pula se for uma pasta ou se o script estiver tentando mover a si mesmo
        if os.path.isdir(caminho_arquivo_origem) or nome_arquivo == os.path.basename(__file__):
            continue

        # Obtém a extensão do arquivo
        _, extensao = os.path.splitext(nome_arquivo)
        extensao = extensao[1:].lower() if extensao else 'Sem_Extensao'

        # Cria o caminho para a pasta da extensão (ex: Downloads/PDF)
        pasta_extensao = os.path.join(pasta_alvo, extensao.upper())
        if not os.path.exists(pasta_extensao):
            os.makedirs(pasta_extensao)
            if verbose:
                if logger:
                    logger.info(f"Pasta criada: {pasta_extensao}")
                else:
                    print(f"Pasta criada: {pasta_extensao}")

        # Extrai o nome do programa e cria a subpasta (ex: Downloads/PDF/AdobeReader)
        nome_subpasta = extrair_nome_programa(nome_arquivo)
        pasta_programa = os.path.join(pasta_extensao, nome_subpasta)
        if not os.path.exists(pasta_programa):
            os.makedirs(pasta_programa)
            if verbose:
                if logger:
                    logger.info(f"Subpasta criada: {pasta_programa}")
                else:
                    print(f"Subpasta criada: {pasta_programa}")

        # Move o arquivo usando renomeação segura em caso de conflito
        caminho_arquivo_destino = os.path.join(pasta_programa, nome_arquivo)
        try:
            safe_move(caminho_arquivo_origem, caminho_arquivo_destino, dry_run=dry_run, suffix_mode=suffix_mode, logger=logger)
            if verbose or dry_run:
                if logger:
                    logger.info(f"Movido: '{nome_arquivo}' -> '{os.path.relpath(caminho_arquivo_destino, pasta_alvo)}'")
                else:
                    print(f"Movido: '{nome_arquivo}' -> '{os.path.relpath(caminho_arquivo_destino, pasta_alvo)}'")
            # registra no backup se solicitado
            if backup_dir:
                record = {
                    'src': caminho_arquivo_origem,
                    'dst': caminho_arquivo_destino,
                    'moved_at': time.time(),
                    'dry_run': dry_run
                }
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir, exist_ok=True)
                with open(os.path.join(backup_dir, 'operations.log'), 'a', encoding='utf-8') as f:
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
        except Exception as e:
            if verbose:
                if logger:
                    logger.exception(f"Erro ao mover '{nome_arquivo}': {e}")
                else:
                    print(f"Erro ao mover '{nome_arquivo}': {e}")

    if verbose:
        if logger:
            logger.info("\nOrganização concluída!")
        else:
            print("\nOrganização concluída!")


# --- EXECUÇÃO ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Organiza a pasta de Downloads.')
    parser.add_argument('--path', '-p', default=PASTA_DOWNLOADS, help='Pasta alvo a ser organizada')
    parser.add_argument('--dry-run', action='store_true', help='Não move arquivos, apenas mostra o que seria feito')
    parser.add_argument('--verbose', action='store_true', help='Mostra mensagens detalhadas durante a execução')
    parser.add_argument('--backup-dir', help='Diretório para gravar log de operações (JSON lines) para possível rollback')
    parser.add_argument('--suffix-mode', choices=['counter', 'timestamp'], default='counter', help='Modo de sufixo quando há conflito: counter ou timestamp')
    parser.add_argument('--log-file', help='Arquivo para gravar logs (adiciona FileHandler ao logger)')
    args = parser.parse_args()

    # configurar logger
    logger = logging.getLogger('organizador')
    logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    fmt = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    if args.log_file:
        fh = logging.FileHandler(args.log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    organizar_downloads(args.path, dry_run=args.dry_run, verbose=args.verbose, backup_dir=args.backup_dir, suffix_mode=args.suffix_mode, logger=logger)