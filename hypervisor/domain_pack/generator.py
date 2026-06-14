from pathlib import Path
import yaml

def generate_domain_pack(uri_tree_path, domain_dir):
    uri_tree_path = Path(uri_tree_path); domain_dir = Path(domain_dir)
    tree = yaml.safe_load(uri_tree_path.read_text(encoding="utf-8"))
    domain_dir.mkdir(parents=True, exist_ok=True)
    for d in ["proto", "handlers", "templates", "tests"]: (domain_dir / d).mkdir(exist_ok=True)
    domain_id = tree["domain"]["id"]; agent_id = tree["agent"]["id"]
    (domain_dir / "domain.yaml").write_text(yaml.safe_dump(tree["domain"], sort_keys=False, allow_unicode=True), encoding="utf-8")
    for key in ["resources", "commands", "events", "artifacts"]:
        (domain_dir / f"{key}.yaml").write_text(yaml.safe_dump(tree.get(key, {}), sort_keys=False, allow_unicode=True), encoding="utf-8")
    proto = 'syntax = "proto3";

package app.%s.v1;

message GenericCommand {
  string request_id = 1;
}

message GenericView {
  string uri = 1;
  string mime_type = 2;
}
' % domain_id
    (domain_dir / "proto" / f"{domain_id}.proto").write_text(proto, encoding="utf-8")
    capabilities=[]
    for cap in tree.get("agent", {}).get("capabilities", []):
        name=cap.get("name")
        if not name: continue
        ctype="command" if name.startswith("generate") or name.startswith("create") else "resource_read"
        entry={"name":name,"type":ctype,"description":f"Generated from URI Tree for {domain_id}."}
        if ctype=="command":
            entry.update({"command":"".join(part.capitalize() for part in name.split("_")),"input_schema":f"app.{domain_id}.v1.GenericCommand","emits":[]})
        else:
            res=next(iter((tree.get("resources") or {}).values()), {})
            entry.update({"uri":res.get("uri_template", f"resource://{domain_id}/{{id}}"),"output_schema":f"app.{domain_id}.v1.GenericView","renderer":res.get("renderer_ref", "json")})
        capabilities.append(entry)
    agent_yaml={"agent":{"name":agent_id,"python_package":agent_id.replace("-","_"),"version":"0.1.0","description":tree["domain"].get("description","")},"capabilities":capabilities}
    contracts_dir=Path("contracts/agents"); contracts_dir.mkdir(parents=True, exist_ok=True)
    (contracts_dir / f"{agent_id.replace('-', '_')}.yaml").write_text(yaml.safe_dump(agent_yaml, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return domain_dir
