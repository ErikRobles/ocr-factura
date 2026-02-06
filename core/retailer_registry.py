import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

@dataclass
class RetailerDef:
    id: str
    display_name: str
    aliases: List[str]
    rfc_prefixes: List[str]
    keywords: List[str]
    priority: int = 0

def load_registry(path: Path) -> List[RetailerDef]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out: List[RetailerDef] = []
    for r in data.get("retailers", []):
        out.append(RetailerDef(
            id=r["id"],
            display_name=r["display_name"],
            aliases=r.get("aliases", []),
            rfc_prefixes=r.get("rfc_prefixes", []),
            keywords=r.get("keywords", []),
            priority=int(r.get("priority", 0)),
        ))
    # highest priority first
    out.sort(key=lambda x: x.priority, reverse=True)
    return out
