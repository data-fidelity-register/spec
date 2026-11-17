"""Validate a DFR register folder against the JSON Schemas.
Usage: python3 validate.py <register-folder> [...]"""
import json, sys, pathlib
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
here = pathlib.Path(__file__).parent
schemas = {p.name: json.loads(p.read_text()) for p in here.glob("*.schema.json")}
reg = Registry().with_resources(
    [(s["$id"], Resource.from_contents(s)) for s in schemas.values()] +
    [(n, Resource.from_contents(s)) for n, s in schemas.items()])
def check(name, doc):
    v = Draft202012Validator(schemas[name], registry=reg, format_checker=FormatChecker())
    errs = sorted(v.iter_errors(doc), key=lambda e: list(e.path))
    return errs
bad = 0
for folder in sys.argv[1:]:
    f = pathlib.Path(folder)
    for fname, sname in (("ledger.json", "dfr-ledger.schema.json"), ("release.json", "dfr-release.schema.json")):
        doc = json.loads((f / fname).read_text())
        errs = check(sname, doc)
        n = len(doc) if isinstance(doc, list) else 1
        print(f"{'OK  ' if not errs else 'FAIL'} {f.name}/{fname} ({n} object{'s' if n>1 else ''}){'' if not errs else f': {len(errs)} error(s)'}")
        for e in errs[:5]:
            print("     ", "/".join(map(str, e.path)) or "(root)", "->", e.message[:140])
        bad += bool(errs)
sys.exit(1 if bad else 0)
