"""Portable handoffs from evidence collection to task use and correction."""
import copy
import json
import shutil
import subprocess
import sys
from argparse import Namespace
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import decision_memory as dm
import principle_library as pl


def write_entry(workspace, *, key='X01', ledger_ids=None, event_ids=None, aliases=None):
    meta = dict(id=key, category='research_and_evidence', summary='Test the useful distinction.',
                updated='2026-10-24', ledger_ids=ledger_ids or [], event_ids=event_ids or [],
                aliases=aliases or [])
    sections = ['## %s. %s\n\n%s' % (n, section, 'Bounded reasoning and a concrete example.')
                for n, section in enumerate(pl.SECTIONS, 1)]
    sections[-1] += '\n\n[External source](https://example.org/source).'
    body = '# Test a useful distinction\n\n' + '\n\n'.join(sections) + '\n'
    path = workspace / 'principles' / f'{key.lower()}-example.md'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('---\n' + '\n'.join(f'{k}: {json.dumps(v)}' for k, v in meta.items()) + '\n---\n' + body)
    return path


def apply_proposal(workspace, proposal, packet=None):
    path = workspace / 'proposal.json'
    path.write_text(json.dumps(proposal))
    args = Namespace(workspace=workspace, proposal=path, packet=packet, validate_only=True)
    dm.apply(args)
    args.validate_only = False
    dm.apply(args)


def event(source, key, quote, supersedes=None):
    return dict(id=key, attribution='attributed_user',
                **{k: 'Not stated beyond the recorded choice.' for k in
                   ('context', 'alternative', 'reason', 'tradeoff', 'scope', 'uncertainty', 'future_test')},
                choice=quote, evidence=[dict(source_id=source['source_id'], quote=quote)],
                **(dict(supersedes_event_ids=supersedes, relation_reason='A recorded correction.') if supersedes else {}))


def collect_note(workspace, note, choice, key, supersedes=None):
    note.write_text('Investigator choice: ' + choice + '\n')
    packet_path = workspace / 'runs' / f'{key}.json'
    dm.collect(Namespace(workspace=workspace, output=packet_path, repo=None, max_sources=24, session_limit=4))
    packet = json.loads(packet_path.read_text())
    assert len(packet['sources']) == 1
    source = packet['sources'][0]
    assert choice in dm.full_source(source)
    proposal = dict(schema_version=1, run_id=packet['run_id'],
                    reviews=[dict(source_id=source['source_id'], disposition='signal', reason='A recorded choice.')],
                    events=[event(source, key, choice, supersedes)])
    apply_proposal(workspace, proposal, packet_path)


def fresh_workspace(tmp_path):
    repo = tmp_path / 'a different project'
    repo.mkdir()
    note = repo / 'NOTES.md'
    registry = tmp_path / 'registry.json'
    registry.write_text(json.dumps(dict(schema_version=1, repos=[dict(name='different', root=str(repo),
                        decision_patterns=['NOTES.md'], maintenance_enabled=False)], dialog_roots=[])))
    workspace = tmp_path / 'a new memory'
    pl.setup(workspace, registry)
    return workspace, note


def test_fresh_workspace_collection_to_use_and_feedback(tmp_path):
    w, note = fresh_workspace(tmp_path)
    collect_note(w, note, 'Retain weak target signal for this measurement.', 'e1')
    candidate = dict(id='candidate-one', status='candidate', support_event_ids=['e1'], counter_event_ids=[],
                     **{k: 'A bounded interpretation of the recorded choice.' for k in
                        ('statement', 'scope', 'boundary', 'predicted_choice', 'cost', 'counterevidence_search', 'review_rationale')})
    apply_proposal(w, dict(run_id='review-one', state_digest=dm.digest(dm.ledger(w)), principles=[candidate]))
    path = write_entry(w, ledger_ids=['candidate-one'], aliases=['old-slug'])
    assert pl.sync(w)['needs_review'] == ['X01']
    with pytest.raises(ValueError, match='changed evidence'):
        pl.task_context(w, ['X01'])
    pl.sync(w, reviewed=['X01'], review_packet=pl.review_packet(w))
    ledger_before = (w / pl.LEDGER).read_bytes()
    packet = pl.task_context(w, ['old-slug'])
    assert all(section in packet for section in pl.SECTIONS)
    assert 'Evidence health' in packet
    assert (w / pl.LEDGER).read_bytes() == ledger_before
    assert dm.ledger(w)['principles'][0]['status'] == 'candidate'  # no recurrence gate for L2
    instructions = tmp_path / 'AGENTS.md'
    instructions.write_text('Keep my existing rule.\n')
    pl.bind(w, instructions)
    bound = instructions.read_bytes()
    assert not pl.bind(w, instructions)['changed']
    assert instructions.read_bytes() == bound
    assert 'Keep my existing rule.' in bound.decode()
    assert str(w) in bound.decode() and 'task-context' in bound.decode()
    # Meaningful task feedback returns through the same registered note and L1 apply.
    collect_note(w, note, 'Correction to X01: reject this signal when it is background.', 'e2', ['e1'])
    assert 'Needs evidence review' in (w / 'principles/INDEX.md').read_text()  # automatic apply handoff
    assert pl.review_packet(w)['events'][-1]['linked_principles'] == ['X01']
    with pytest.raises(ValueError, match='changed evidence'):
        pl.task_context(w, ['X01'])
    # Plain render cannot turn a detected correction into reviewed guidance.
    dm.render(w, dm.ledger(w))
    assert pl.sync(w, check=True)['needs_review'] == ['X01']
    path.write_text(path.read_text().replace('Bounded reasoning', 'Revised limits after the correction; bounded reasoning'))
    pl.sync(w, reviewed=['X01'], review_packet=pl.review_packet(w))
    assert 'Revised limits' in pl.task_context(w, ['X01'])
    assert len(dm.ledger(w)['events']) == 2


def test_borrowed_entry_creates_no_personal_evidence_and_setup_relocates(tmp_path):
    w, _ = fresh_workspace(tmp_path)
    write_entry(w)
    pl.sync(w)
    assert not (w / pl.LEDGER).exists()
    assert 'External source' in pl.task_context(w, ['X01'])
    authored = (w / 'principles/x01-example.md').read_bytes()
    pl.setup(w)
    prompt = (w / 'config/prompts/weekly-review.txt').read_bytes()
    pl.setup(w)
    assert (w / 'config/prompts/weekly-review.txt').read_bytes() == prompt
    assert (w / 'principles/x01-example.md').read_bytes() == authored
    moved = tmp_path / 'moved memory'
    shutil.copytree(w, moved)
    pl.setup(moved)
    assert str(moved) in (moved / 'config/prompts/weekly-review.txt').read_text()
    assert str(w) not in (moved / 'config/prompts/weekly-review.txt').read_text()
    assert (moved / 'principles/x01-example.md').read_bytes() == authored
    assert not (moved / pl.LEDGER).exists()


def test_changed_interpretation_retires_or_invalidates_but_unrelated_event_does_not(tmp_path):
    w, note = fresh_workspace(tmp_path)
    collect_note(w, note, 'Keep this distinction.', 'e1')
    write_entry(w, event_ids=['e1'])
    pl.sync(w, reviewed=['X01'], review_packet=pl.review_packet(w))
    collect_note(w, note, 'An unrelated decision about formatting.', 'e2')
    assert not pl.sync(w)['needs_review']
    state = dm.ledger(w)
    state['events'][0]['scope'] = 'Changed scope'
    assert pl.entries_at(w, state)[0]['needs_review']
    path = w / 'principles/x01-example.md'
    path.write_text(path.read_text().replace('---\n', '---\nstatus: retired\n', 1))
    pl.sync(w)
    with pytest.raises(ValueError, match='retired'):
        pl.task_context(w, ['X01'])
    assert 'Retained history' in (w / 'principles/INDEX.md').read_text()


@pytest.mark.parametrize('failure', ['duplicate', 'unknown_event', 'unknown_ledger', 'missing_section', 'symlink'])
def test_invalid_library_never_replaces_index(tmp_path, failure):
    w, _ = fresh_workspace(tmp_path)
    path = write_entry(w)
    pl.sync(w)
    original = (w / 'principles/INDEX.md').read_bytes()
    if failure == 'duplicate':
        write_entry(w, key='X02', aliases=['X01'])
    elif failure == 'unknown_event':
        write_entry(w, event_ids=['missing'])
    elif failure == 'unknown_ledger':
        write_entry(w, ledger_ids=['missing'])
    elif failure == 'missing_section':
        path.write_text(path.read_text().replace('## 4. Limits and pitfalls', '## 4. Missing'))
    else:
        outside = tmp_path / 'outside.md'
        path.rename(outside)
        path.symlink_to(outside)
    with pytest.raises(ValueError):
        pl.sync(w)
    assert (w / 'principles/INDEX.md').read_bytes() == original


def test_check_detects_hand_edited_index_and_bounds_task_selection(tmp_path):
    w, _ = fresh_workspace(tmp_path)
    write_entry(w)
    pl.sync(w)
    (w / 'principles/INDEX.md').write_text('Hand-edited output')
    with pytest.raises(ValueError, match='index is stale'):
        pl.sync(w, check=True)
    pl.sync(w)
    for ids in ([], ['missing'], ['X01', 'X01'], ['X01'] * 4):
        with pytest.raises(ValueError):
            pl.task_context(w, ids)
    with pytest.raises(ValueError, match='Unknown reviewed'):
        pl.sync(w, reviewed=['missing'])


def test_setup_preserves_registry_and_rejects_replacement(tmp_path):
    w, _ = fresh_workspace(tmp_path)
    before = (w / 'config/repos.json').read_bytes()
    replacement = tmp_path / 'replacement.json'
    replacement.write_text(json.dumps({'schema_version': 1, 'repos': []}))
    with pytest.raises(ValueError, match='reconcile'):
        pl.setup(w, replacement)
    assert (w / 'config/repos.json').read_bytes() == before


def test_setup_maintenance_prompts_follow_registry_without_enabling_jobs(tmp_path):
    w, _ = fresh_workspace(tmp_path)
    config = w / 'config/repos.json'
    data = json.loads(config.read_text())
    data['repos'].append(dict(name='active-repo', root=str(tmp_path / 'active'), maintenance_enabled=True))
    config.write_text(json.dumps(data))
    result = pl.setup(w)
    prompt = (w / 'config/prompts/maintenance-active-repo.txt').read_text()
    assert 'Automation context:' in prompt and str(tmp_path / 'active') in prompt
    assert str(pl.ROOT) in prompt and '{{' not in prompt
    assert not (w / 'config/prompts/maintenance-different.txt').exists()
    assert result['scheduler_changed'] is False
    instructions = (w / 'config/prompts/task-instructions.md').read_text()
    assert 'observed result or remaining limit' in instructions


def test_unsafe_maintenance_name_fails_before_writes(tmp_path):
    registry = tmp_path / 'bad.json'
    registry.write_text(json.dumps(dict(schema_version=1, repos=[
        dict(name='../escape', root=str(tmp_path), maintenance_enabled=True)])))
    w = tmp_path / 'new-hub'
    with pytest.raises(ValueError, match='safe repository short name'):
        pl.setup(w, registry)
    assert not (w / 'config/repos.json').exists()


def test_installed_package_uses_its_own_location(tmp_path):
    installed = tmp_path / 'a second skill installation'
    installed.mkdir()
    for directory in ('scripts', 'templates', 'references'):
        shutil.copytree(pl.ROOT / directory, installed / directory,
                        ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy2(pl.ROOT / 'SKILL.md', installed / 'SKILL.md')
    registry = tmp_path / 'registry.json'
    registry.write_text(json.dumps({'schema_version': 1, 'repos': [], 'dialog_roots': []}))
    workspace = tmp_path / 'separate workspace'
    command = [sys.executable, str(installed / 'scripts/principle_library.py'), 'setup',
               '--workspace', str(workspace), '--registry', str(registry)]
    subprocess.run(command, check=True, capture_output=True, text=True)
    for path in (workspace / 'config/prompts').glob('*'):
        content = path.read_text()
        assert str(installed) in content
        assert str(pl.ROOT) not in content
        assert '{{' not in content


@pytest.mark.parametrize('provider', ['codex', 'claude_code'])
def test_generated_prompts_cannot_be_direct_user_evidence(tmp_path, provider):
    w, _ = fresh_workspace(tmp_path)
    for name in ('daily-observer.txt', 'weekly-review.txt'):
        prompt = (w / 'config/prompts' / name).read_text()
        path = tmp_path / (name + '.jsonl')
        if provider == 'codex':
            rows = [dict(type='session_meta', payload=dict(id='auto', cwd=str(w), source='cli')),
                    dict(type='response_item', timestamp='2026-10-24T00:00:00Z',
                         payload=dict(role='user', id=name, content=[dict(type='input_text', text=prompt)])),
                    dict(type='event_msg', payload=dict(type='task_complete'))]
        else:
            rows = [dict(type='user', sessionId='auto', cwd=str(w), uuid=name, parentUuid=None,
                         timestamp='2026-10-24T00:00:00Z', message=dict(role='user', content=prompt)),
                    dict(type='assistant', sessionId='auto', cwd=str(w), uuid=name+'-done', parentUuid=name,
                         message=dict(role='assistant', content='Done', stop_reason='end_turn'))]
        path.write_text(''.join(json.dumps(row)+'\n' for row in rows))
        records = dm.session_records(path, 'test')
        assert len(records) == 1
        assert records[0]['origin'] == 'automation'


def test_dialog_only_registry_excludes_generated_documents(tmp_path):
    w, note = fresh_workspace(tmp_path)
    note.write_text('Generated prose must not become evidence.')
    sessions = tmp_path / 'sessions'
    sessions.mkdir()
    rows = [dict(type='session_meta', payload=dict(id='human', cwd=str(note.parent), source='cli')),
            dict(type='response_item', timestamp='2026-10-24T00:00:00Z',
                 payload=dict(role='user', id='real-choice', content=[dict(type='input_text',
                              text='Change the shared method so another dataset can reproduce the result.')])),
            dict(type='event_msg', payload=dict(type='task_complete'))]
    (sessions/'human.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in rows))
    records, _, coverage = dm.inventory_repo(dict(name='different', root=str(note.parent), decision_patterns=[]),
                                           [str(sessions)], dm.ledger(w), 4)
    assert len(records) == 1 and records[0]['kind'] == 'user_message'
    assert records[0]['origin'] == 'human_or_unverified'
    assert coverage['documents_discovered'] == 0


def library_bytes(workspace):
    return {str(path.relative_to(workspace)): path.read_bytes()
            for path in [workspace / pl.LEDGER, *(workspace / 'principles').glob('*.md')]}


def test_review_requires_saved_packet_and_does_not_bless_unseen_daily_correction(tmp_path):
    w, note = fresh_workspace(tmp_path)
    collect_note(w, note, 'Keep this distinction.', 'e1')
    write_entry(w, event_ids=['e1'])
    pl.sync(w)
    started_review = pl.review_packet(w)
    collect_note(w, note, 'Correction: reject the earlier distinction.', 'e2', ['e1'])
    before = library_bytes(w)
    for packet in (None, started_review):
        with pytest.raises(ValueError, match='requires a saved|Stale or missing'):
            pl.sync(w, reviewed=['X01'], review_packet=packet)
        assert library_bytes(w) == before
        with pytest.raises(ValueError, match='changed evidence'):
            pl.task_context(w, ['X01'])
    assert pl.sync(w, check=True)['needs_review'] == ['X01']


def test_review_rejects_correction_to_correction_before_any_selected_write(tmp_path):
    w, note = fresh_workspace(tmp_path)
    collect_note(w, note, 'Keep this distinction.', 'e1')
    write_entry(w, event_ids=['e1'])
    collect_note(w, note, 'A separate decision.', 'e2')
    write_entry(w, key='X02', event_ids=['e2'])
    collect_note(w, note, 'Correction to the separate decision.', 'e3', ['e2'])
    pl.sync(w)
    started_review = pl.review_packet(w)
    collect_note(w, note, 'Correction to that correction.', 'e4', ['e3'])
    before = library_bytes(w)
    with pytest.raises(ValueError, match="Stale or missing reviewed evidence for \\['X02'\\]"):
        pl.sync(w, reviewed=['X01', 'X02'], review_packet=started_review)
    # X01 is valid, but may not be partially acknowledged before X02 is rejected.
    assert library_bytes(w) == before
    assert pl.sync(w, check=True)['needs_review'] == ['X01', 'X02']


def test_saved_review_allows_unrelated_daily_evidence_and_preserves_authored_body(tmp_path):
    w, note = fresh_workspace(tmp_path)
    collect_note(w, note, 'Keep this distinction.', 'e1')
    authored = write_entry(w, event_ids=['e1'])
    other = write_entry(w, key='X02')
    pl.sync(w)
    started_review = pl.review_packet(w)
    # A reviewer can improve authored guidance without changing its evidence links.
    authored.write_text(authored.read_text().replace('Bounded reasoning', 'Manual correction: bounded reasoning'))
    body = pl.parse(authored)['body']
    other_before = other.read_bytes()
    packet_before = copy.deepcopy(started_review)
    collect_note(w, note, 'An unrelated formatting choice.', 'e2')
    ledger_before = (w / pl.LEDGER).read_bytes()
    assert started_review['state_digest'] != pl.review_packet(w)['state_digest']
    assert not pl.sync(w, reviewed=['X01'], review_packet=started_review)['needs_review']
    assert pl.parse(authored)['body'] == body
    assert other.read_bytes() == other_before
    assert started_review == packet_before
    assert (w / pl.LEDGER).read_bytes() == ledger_before
    assert 'Manual correction' in pl.task_context(w, ['X01'])


@pytest.mark.parametrize('change', ['event_content', 'document_links'])
def test_saved_review_rejects_changed_evidence_without_new_event_count(tmp_path, change):
    w, note = fresh_workspace(tmp_path)
    collect_note(w, note, 'Keep this distinction.', 'e1')
    collect_note(w, note, 'A different distinction.', 'e2')
    authored = write_entry(w, event_ids=['e1'])
    pl.sync(w)
    started_review = pl.review_packet(w)
    if change == 'event_content':
        state = dm.ledger(w)
        state['events'][0]['scope'] = 'A revised interpretation'
        (w / pl.LEDGER).write_text(json.dumps(state))
    else:
        authored.write_text(authored.read_text().replace('event_ids: ["e1"]', 'event_ids: ["e2"]'))
    before = library_bytes(w)
    with pytest.raises(ValueError, match='Stale or missing'):
        pl.sync(w, reviewed=['X01'], review_packet=started_review)
    assert library_bytes(w) == before


@pytest.mark.parametrize('kind', ['legacy_packet', 'duplicate_id', 'missing_id', 'invalid_packet', 'stale_state'])
def test_review_packet_errors_do_not_write(tmp_path, kind):
    w, note = fresh_workspace(tmp_path)
    collect_note(w, note, 'Keep this distinction.', 'e1')
    write_entry(w, event_ids=['e1'])
    pl.sync(w)
    packet = pl.review_packet(w)
    kwargs = {}
    if kind == 'legacy_packet':
        del packet['principles'][0]['evidence_digest']
    elif kind == 'duplicate_id':
        packet['principles'].append(copy.deepcopy(packet['principles'][0]))
    elif kind == 'missing_id':
        packet['principles'] = []
    elif kind == 'invalid_packet':
        packet = []
    else:
        kwargs['state'] = dm.ledger(w)
    before = library_bytes(w)
    with pytest.raises(ValueError):
        pl.sync(w, reviewed=['X01'], review_packet=packet, **kwargs)
    assert library_bytes(w) == before


def test_cli_stale_packet_rejected_and_rereview_accepted(tmp_path):
    w, note = fresh_workspace(tmp_path)
    collect_note(w, note, 'Keep this distinction.', 'e1')
    authored = write_entry(w, event_ids=['e1'])
    pl.sync(w)
    command = [sys.executable, str(pl.ROOT / 'scripts/principle_library.py')]
    review = subprocess.run(command + ['review', '--workspace', str(w)],
                            check=True, capture_output=True, text=True)
    packet_path = w / 'runs/weekly-review.json'
    packet_path.write_text(review.stdout)
    collect_note(w, note, 'Correction: reject the earlier distinction.', 'e2', ['e1'])
    before = library_bytes(w)
    sync = command + ['sync', '--workspace', str(w), '--reviewed', 'X01', '--review-packet', str(packet_path)]
    result = subprocess.run(sync, capture_output=True, text=True)
    assert result.returncode == 1
    assert 'Stale or missing' in result.stderr
    assert library_bytes(w) == before
    # Re-read the new evidence, update guidance, and acknowledge that saved packet.
    review = subprocess.run(command + ['review', '--workspace', str(w)],
                            check=True, capture_output=True, text=True)
    packet_path.write_text(review.stdout)
    authored.write_text(authored.read_text().replace('Bounded reasoning', 'Revised after the correction; bounded reasoning'))
    result = subprocess.run(sync, check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)['needs_review'] == []
    assert 'Revised after the correction' in pl.task_context(w, ['X01'])
    assert (w / pl.LEDGER).read_bytes() == before[pl.LEDGER]
    checked = subprocess.run(sync + ['--check'], capture_output=True, text=True)
    assert checked.returncode == 1
    assert '--check cannot acknowledge' in checked.stderr


def test_cli_checks_packet_after_acquiring_workspace_lock(tmp_path, monkeypatch):
    from contextlib import contextmanager

    w, note = fresh_workspace(tmp_path)
    collect_note(w, note, 'Keep this distinction.', 'e1')
    write_entry(w, event_ids=['e1'])
    pl.sync(w)
    packet_path = w / 'runs/weekly-review.json'
    packet_path.write_text(json.dumps(pl.review_packet(w)))
    real_lock = pl.workspace_lock
    after_daily = {}

    @contextmanager
    def collect_before_lock(workspace):
        collect_note(w, note, 'A late correction.', 'e2', ['e1'])
        after_daily.update(library_bytes(w))
        with real_lock(workspace):
            yield

    monkeypatch.setattr(pl, 'workspace_lock', collect_before_lock)
    monkeypatch.setattr(sys, 'argv', ['principle_library.py', 'sync', '--workspace', str(w),
                                     '--reviewed', 'X01', '--review-packet', str(packet_path)])
    with pytest.raises(SystemExit) as error:
        pl.main()
    assert error.value.code == 1
    assert library_bytes(w) == after_daily
    with pytest.raises(ValueError, match='changed evidence'):
        pl.task_context(w, ['X01'])
