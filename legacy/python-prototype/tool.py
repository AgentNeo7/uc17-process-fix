"""Standalone deterministic synthetic prototype. No runtime integration or domain authority."""
import argparse
import copy
import datetime
import hashlib
import json
import math
from pathlib import Path
import sys


def obj(x, keys):
    if not isinstance(x, dict) or set(x) != set(keys.split()):
        raise ValueError("object fields must be: " + keys)
    return x


def text(x):
    if not isinstance(x, str) or not x or len(x) > 2048:
        raise ValueError("expected nonempty bounded string")
    return x


def arr(x):
    if not isinstance(x, list) or len(x) > 500:
        raise ValueError("expected list of at most 500 elements")
    return x


def names(x):
    values = [text(v) for v in arr(x)]
    if len(values) != len(set(values)):
        raise ValueError("duplicate identifiers")
    return values


def num(x, minimum=0):
    if type(x) not in (int, float) or not math.isfinite(x) or x < minimum or x > 1e12:
        raise ValueError("invalid bounded number")
    return x


def integer(x, minimum=0):
    if type(x) is not int:
        raise ValueError("expected integer")
    return num(x, minimum)


def boolean(x):
    if type(x) is not bool:
        raise ValueError("expected boolean")
    return x


def unique(rows):
    ids = [text(x["id"]) for x in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate record ID")


def scalar(x):
    if x is not None and type(x) not in (str, int, float, bool):
        raise ValueError("expected scalar value")
    if type(x) in (int,float) and not math.isfinite(x):
        raise ValueError("nonfinite number")
    return x


def result(**kw):
    return {"evidence_class": "simulated", "analysis_completed": True, **kw}


def analyze(payload):
    obj(payload, "spec_version evidence_class data")
    if type(payload["spec_version"]) is not int or payload["spec_version"] != 1 or payload["evidence_class"] != "simulated":
        raise ValueError("only spec_version 1 synthetic evidence_class simulated supported")
    return run(copy.deepcopy(payload["data"]))


def matches(actual, expected):
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(k in actual and matches(actual[k], v) for k,v in expected.items())
    return actual == expected


def read_json(path):
    if path.stat().st_size > 1000000:
        raise ValueError("input exceeds 1000000 bytes")
    return json.loads(path.read_text())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--expect", type=Path, help="optional recursive subset oracle; mismatch exits 1")
    a=p.parse_args()
    try:
        if a.input.resolve() == a.output.resolve() or (a.expect and a.expect.resolve() == a.output.resolve()):
            raise ValueError("output must not overwrite input or oracle")
        output=analyze(read_json(a.input))
        expected=read_json(a.expect) if a.expect else None
        a.output.write_text(json.dumps(output,indent=2,sort_keys=True,allow_nan=False)+"\n")
        return 0 if expected is None or matches(output,expected) else 1
    except (ValueError, KeyError, TypeError, OSError, RecursionError, OverflowError) as e:
        print("invalid input: "+str(e),file=sys.stderr)
        return 2

def run(d):
    obj(d,'events owners before after other_changes');events=arr(d['events']);unique(events);changes=names(d['other_changes'])
    if not isinstance(d['owners'],dict):raise ValueError('owners must be map')
    for k,v in d['owners'].items():text(k);text(v)
    allowed=['data','knowledge','integration','workflow','agent','unknown']
    grouped={};unlinked=[]
    for e in events:
        obj(e,'id case component category signature source')
        for k in ['component','signature','source']:text(e[k])
        if e['category'] not in allowed:raise ValueError('unsupported category; use unknown')
        if e['case'] is None:unlinked.append(e['id']);continue
        text(e['case']);key=(e['component'],e['category'],e['signature']);grouped.setdefault(key,[]).append(e)
    hypotheses=[]
    for (component,category,signature),es in grouped.items():
        hypotheses.append({'component':component,'category':category,'signature':signature,'owner':d['owners'].get(component),'case_count':len({e['case'] for e in es}),'evidence_ids':sorted(e['id'] for e in es),'sources':sorted({e['source'] for e in es}),'claim_status':'proposed','alternative':'Shared downstream symptom or incomplete instrumentation; causal direction unverified.'})
    hypotheses.sort(key=lambda h:(-h['case_count'],h['component'],h['signature']))
    rates=[]
    for key in ['before','after']:
        c=obj(d[key],'exposure failures');n=integer(c['exposure']);errors=integer(c['failures'])
        if errors>n:raise ValueError('failures exceed exposure')
        rates.append(errors/n if n else None)
    recurrence={'before_rate':rates[0],'after_rate':rates[1],'difference':round(rates[1]-rates[0],12) if None not in rates else None,'causal_claim':False,'confounders':changes}
    return result(status='hypotheses_for_review' if hypotheses else 'insufficient_linkage',unlinked_event_ids=sorted(unlinked),hypotheses=hypotheses,recurrence=recurrence,external_submission=False)

if __name__ == "__main__":
    sys.exit(main())
