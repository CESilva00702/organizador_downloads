import os
import time
import json
import pytest
from organizador_downloads import organizar_downloads, safe_move


def test_safe_move_counter(tmp_path, monkeypatch):
    src = tmp_path / 'src.txt'
    dst_dir = tmp_path / 'dst'
    dst_dir.mkdir()
    src.write_text('x')
    existing = dst_dir / 'src.txt'
    existing.write_text('y')

    # use safe_move to move src into dst where file exists
    safe_move(str(src), str(dst_dir / 'src.txt'), dry_run=False, suffix_mode='counter')

    # after move, expect 'src (1).txt' exists
    assert (dst_dir / 'src (1).txt').exists()


def test_safe_move_timestamp(tmp_path):
    src = tmp_path / 'a.bin'
    dst_dir = tmp_path / 'dst'
    dst_dir.mkdir()
    src.write_text('x')
    existing = dst_dir / 'a.bin'
    existing.write_text('y')

    safe_move(str(src), str(dst_dir / 'a.bin'), dry_run=False, suffix_mode='timestamp')

    # expect either a timestamped file exists
    found = False
    for p in dst_dir.iterdir():
        if p.name.startswith('a_') and p.suffix == '.bin':
            found = True
    assert found


def test_organizar_dry_run_and_backup(tmp_path):
    # setup a fake downloads folder
    downloads = tmp_path / 'Downloads'
    downloads.mkdir()
    f = downloads / 'example_v1.0_setup_x64.pdf'
    f.write_text('content')

    backup = tmp_path / 'backup'
    backup.mkdir()

    organizar_downloads(str(downloads), dry_run=True, verbose=True, backup_dir=str(backup), suffix_mode='counter')

    # since dry-run, file should still be in root
    assert (downloads / 'example_v1.0_setup_x64.pdf').exists()

    # backup operations log should exist and contain one entry
    log = backup / 'operations.log'
    assert log.exists()
    lines = log.read_text(encoding='utf-8').strip().splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec['dry_run'] is True
