import os
import json
import pytest
from tools.rollback import perform_rollback


def write_ops(log_path, entries):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'w', encoding='utf-8') as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + '\n')


def test_rollback_dry_run(fs):
    base = 'C:\\pyfakefs_test1'
    ops_dir = os.path.join(base, 'backup')
    os.makedirs(ops_dir)

    dst = os.path.join(base, 'PDF', 'Example', 'file.pdf')
    os.makedirs(os.path.dirname(dst))
    with open(dst, 'w', encoding='utf-8') as f:
        f.write('dst')

    src = os.path.join(base, 'file.pdf')
    ops_log = os.path.join(ops_dir, 'operations.log')
    entry = {'src': src, 'dst': dst, 'moved_at': 1, 'dry_run': False}
    write_ops(ops_log, [entry])

    results = perform_rollback(ops_log, dry_run=True, verbose=True)

    # dry-run should not move files
    assert os.path.exists(dst)
    assert not os.path.exists(src)
    assert len(results) == 1
    assert results[0]['result'] == 'ok'


def test_rollback_move_creates_src(fs):
    base = 'C:\\pyfakefs_test2'
    ops_dir = os.path.join(base, 'backup')
    os.makedirs(ops_dir)

    dst = os.path.join(base, 'PDF', 'Example', 'a.txt')
    os.makedirs(os.path.dirname(dst))
    with open(dst, 'w', encoding='utf-8') as f:
        f.write('dst')

    src = os.path.join(base, 'a.txt')
    ops_log = os.path.join(ops_dir, 'operations.log')
    entry = {'src': src, 'dst': dst, 'moved_at': 1, 'dry_run': False}
    write_ops(ops_log, [entry])

    results = perform_rollback(ops_log, dry_run=False, verbose=True)

    # after real rollback, src should exist and dst should not
    assert os.path.exists(src)
    assert not os.path.exists(dst)
    assert len(results) == 1
    assert results[0]['result'] == 'ok'


def test_rollback_conflict_when_src_exists(fs):
    base = 'C:\\pyfakefs_test3'
    ops_dir = os.path.join(base, 'backup')
    os.makedirs(ops_dir)

    dst = os.path.join(base, 'PDF', 'Example', 'b.txt')
    os.makedirs(os.path.dirname(dst))
    with open(dst, 'w', encoding='utf-8') as f:
        f.write('dst')

    src = os.path.join(base, 'b.txt')
    # create existing src to force conflict
    with open(src, 'w', encoding='utf-8') as f:
        f.write('orig')

    ops_log = os.path.join(ops_dir, 'operations.log')
    entry = {'src': src, 'dst': dst, 'moved_at': 1, 'dry_run': False}
    write_ops(ops_log, [entry])

    results = perform_rollback(ops_log, dry_run=False, verbose=True)

    # original src should still exist and a new file with suffix should exist
    assert os.path.exists(src)
    # find a file that starts with 'b (' or 'b_' depending on implementation
    found = False
    for name in os.listdir(os.path.dirname(src)):
        if name.startswith('b (') and name.endswith('.txt'):
            found = True
    assert found
    assert len(results) == 1
    assert results[0]['result'] == 'ok'


def test_rollback_writes_out_log(fs):
    base = 'C:\\pyfakefs_test4'
    ops_dir = os.path.join(base, 'backup')
    os.makedirs(ops_dir)

    dst = os.path.join(base, 'PDF', 'Example', 'c.txt')
    os.makedirs(os.path.dirname(dst))
    with open(dst, 'w', encoding='utf-8') as f:
        f.write('dst')

    src = os.path.join(base, 'c.txt')
    ops_log = os.path.join(ops_dir, 'operations.log')
    entry = {'src': src, 'dst': dst, 'moved_at': 1, 'dry_run': False}
    write_ops(ops_log, [entry])

    out_log = os.path.join(ops_dir, 'rollback.log')
    results = perform_rollback(ops_log, dry_run=False, verbose=True, out_log=out_log)

    assert os.path.exists(out_log)
    with open(out_log, 'r', encoding='utf-8') as f:
        lines = [l for l in f.read().splitlines() if l.strip()]
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec['result'] == 'ok'
