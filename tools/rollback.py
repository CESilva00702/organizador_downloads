import os
import json
import argparse
import time
import logging


def safe_move(src, dst, dry_run=False, logger=None):
    """Move src -> dst, se dst existir adiciona sufixo incremental.
    Em dry_run apenas registra a ação.
    """
    if dry_run:
        if logger:
            logger.info(f"[dry-run] mover: '{src}' -> '{dst}'")
        else:
            print(f"[dry-run] mover: '{src}' -> '{dst}'")
        return True

    dst_dir = os.path.dirname(dst)
    base = os.path.basename(dst)
    name, ext = os.path.splitext(base)
    candidate = dst

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok=True)

    i = 1
    while os.path.exists(candidate):
        candidate = os.path.join(dst_dir, f"{name} ({i}){ext}")
        i += 1

    try:
        os.replace(src, candidate)
        if logger:
            logger.debug(f"safe_move: '{src}' -> '{candidate}'")
        return True
    except Exception as e:
        if logger:
            logger.exception(f"Erro ao mover '{src}' para '{candidate}': {e}")
        else:
            print(f"Erro ao mover '{src}' para '{candidate}': {e}")
        return False


def load_operations(log_path):
    ops = []
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ops.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"Ignorando linha inválida no log: {line}")
    return ops


def perform_rollback(log_path, dry_run=False, verbose=False, out_log=None, logger=None):
    ops = load_operations(log_path)
    # ordenar por moved_at desc (reverter em ordem inversa)
    ops.sort(key=lambda r: r.get('moved_at', 0), reverse=True)

    results = []
    for rec in ops:
        src = rec.get('src')
        dst = rec.get('dst')
        if not dst:
            results.append({'rec': rec, 'result': 'skipped', 'msg': 'dst missing'})
            continue

        if not os.path.exists(dst):
            msg = f"Ignorado: destino não existe: {dst}"
            if logger:
                if verbose:
                    logger.info(msg)
            else:
                if verbose:
                    print(msg)
            results.append({'rec': rec, 'result': 'skipped', 'msg': msg})
            continue

        target = src if src else dst
        if verbose:
            if logger:
                logger.info(f"Tentando reverter: '{dst}' -> '{target}'")
            else:
                print(f"Tentando reverter: '{dst}' -> '{target}'")

        # se target já existir, safe_move aplicará sufixo incremental
        success = safe_move(dst, target, dry_run=dry_run, logger=logger)
        msg = 'ok' if success else 'failed'
        results.append({'rec': rec, 'result': msg, 'msg': None, 'rolled_at': time.time()})

    # grava rollback.log se solicitado
    if out_log:
        with open(out_log, 'w', encoding='utf-8') as f:
            for r in results:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')

    return results


def main():
    parser = argparse.ArgumentParser(description='Rollback de operations.log gerado por organizador_downloads')
    parser.add_argument('--operations-log', '-l', required=True, help='Caminho para operations.log (JSON lines)')
    parser.add_argument('--dry-run', action='store_true', help='Simula sem mover arquivos')
    parser.add_argument('--verbose', action='store_true', help='Imprime mensagens detalhadas')
    parser.add_argument('--out-log', help='Caminho para gravar rollback.log (JSON lines)')
    parser.add_argument('--log-file', help='Arquivo para gravar logs de execução')
    args = parser.parse_args()

    # configurar logger
    logger = logging.getLogger('rollback')
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

    if not os.path.exists(args.operations_log):
        logger.error(f"Arquivo de operações não encontrado: {args.operations_log}")
        return

    results = perform_rollback(args.operations_log, dry_run=args.dry_run, verbose=args.verbose, out_log=args.out_log, logger=logger)
    if args.verbose:
        logger.info(f"Rollback completo. {len(results)} entradas processadas.")


if __name__ == '__main__':
    main()
