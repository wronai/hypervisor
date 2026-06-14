import json
from pathlib import Path

from hypervisor.contract_registry.registry_builder import build_registry_manifest, write_registry_manifest
from hypervisor.contract_registry.registry_exporter import export_markdown


def test_registry_manifest_contains_contract_hash():
    manifest = build_registry_manifest('.')
    assert manifest['contract_hash'].startswith('sha256:')
    assert manifest['counts']['resources'] >= 2
    assert manifest['counts']['capabilities'] >= 2


def test_registry_exports(tmp_path: Path):
    json_path = write_registry_manifest('.', tmp_path / 'registry.json')
    md_path = export_markdown('.', tmp_path / 'registry.md')
    data = json.loads(json_path.read_text())
    assert data['contract_hash'].startswith('sha256:')
    assert 'Contract Registry Export' in md_path.read_text()
