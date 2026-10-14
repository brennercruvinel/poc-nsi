"""Build every model call from the frozen gold file. Output: runs/calls.jsonl (model independent).

usage: python prompts.py <gold.csv> <out.jsonl>
"""
import csv
import json
import sys

INSTR = ("Respond only with JSON. Use status \"answer\" if you can identify what the code refers to, "
         "\"ambiguous\" if it could refer to different things and the question does not settle which, "
         "or \"unknown\" if you do not know. In \"readings\", list each interpretation you give, "
         "with the coding system and the full name of the entity.")
SCHEMA = {"type": "object", "required": ["status", "readings"], "properties": {
    "status": {"type": "string", "enum": ["answer", "ambiguous", "unknown"]},
    "readings": {"type": "array", "items": {"type": "object", "required": ["system", "entity"], "properties": {
        "system": {"type": "string"}, "entity": {"type": "string"}}}}}}
P1_SCHEMA = {"type": "object", "required": ["status", "code"], "properties": {
    "status": {"type": "string", "enum": ["answer", "unknown"]}, "code": {"type": "string"}}}
P2_SCHEMA = {"type": "object", "required": ["answer"], "properties": {"answer": {"type": "string", "enum": ["yes", "no", "unknown"]}}}

C1 = ['What does the code "{X}" refer to?', 'What is "{X}"?', 'What does "{X}" stand for?']
C2 = ['In the {NS}, what does the code "{X}" refer to?', '"{X}" is a code in the {NS}. What does it denote?',
      'Within the {NS}, which entity has the code "{X}"?']
C3Q = ['In this text, what does "{X}" refer to?', 'What is "{X}" in the text above?', 'Identify what "{X}" denotes in this text.']
C3 = {
    "trp/iata": ["Boarding pass: Flight 2417, Gate 12, From: LHR, To: {X}, Seat 14C.",
                 "Itinerary: depart {X} at 07:15, arrive FRA at 09:40.",
                 "Baggage tag printed at check-in: {X}, connecting via CDG."],
    "trp/ica2": ["ATC transcript: \"{X}482, climb and maintain flight level 340.\"",
                 "Flight plan filed: aircraft identification {X}1207, type A320, departure EGLL.",
                 "ADS-B tracker shows flight {X}55 cruising at 36,000 ft."],
    "lng/i31": ["Passport machine-readable zone: P<{X}SMITH<<JOHN<<<<<<<<<<<<<<<<<<<<<",
                "Visa application form. Nationality: {X}. Date of birth: 1988-04-12.",
                "Shipping manifest. Country of origin: {X}. HS code: 8471.30."],
    "lng/ioc": ["Olympic medal table: 4. {X} - 7 gold, 9 silver, 5 bronze.",
                "Athletics results, men's 400 m final: 3rd place, {X}, 44.12 s.",
                "Opening ceremony parade order: the delegation of {X} entered after the previous team."],
    "fin/i42": ["Invoice total: 1,250.00 {X}.", "Exchange board: 1 USD = 3.87 {X}.",
                "Hotel bill: room rate 420 {X} per night, taxes included."],
    "fin/tck": ["Market close: shares of {X} fell 2.3% to $48.17.", "Portfolio holdings: 150 shares of {X}, average cost $31.20.",
                "Earnings preview: analysts expect {X} to report EPS of $1.12 this quarter."],
    "cmp/dns": ["Zone file line: example.com. 3600 IN {X} <record data>",
                "dig output, ANSWER SECTION: example.org. 300 IN {X} <record data>",
                "The zone administrator added a new {X} entry for example.net."],
}
C4 = ["Reference record from the {NS}: code {X} = {L}.\n" + C1[0], "Registry entry ({NS}): {X} -> {L}.\n" + C1[1],
      "Authoritative record: in the {NS}, {X} is {L}.\n" + C1[2]]
P1 = 'What is the code for {D} in the {NS}? Use status "unknown" if you do not know.'
P2 = 'In the {NS}, does the code "{X}" denote {D}? Answer yes, no, or unknown.'


def call(cid, item, cond, var, text, schema):
    return {"call_id": cid, "item": item, "cond": cond, "var": var, "schema": schema, "prompt": text}


def main(gold, out):
    rows = list(csv.DictReader(open(gold, encoding="utf-8")))
    calls, seen_lit = [], set()
    for g in rows:
        X, NS, L, D = g["literal"], g["namespace"], g["label"], g["desc"]
        if (g["role"], X) not in seen_lit:
            seen_lit.add((g["role"], X))
            for v, t in enumerate(C1):
                calls.append(call(f"C1|{g['role']}|{X}|{v}", f"{g['role']}|{X}", "C1", v, f"{t.format(X=X)}\n\n{INSTR}", SCHEMA))
        for v, t in enumerate(C2):
            calls.append(call(f"C2|{g['id']}|{v}", g["id"], "C2", v, f"{t.format(X=X, NS=NS)}\n\n{INSTR}", SCHEMA))
        for v, (ctx, q) in enumerate(zip(C3[g["system_id"]], C3Q)):
            calls.append(call(f"C3|{g['id']}|{v}", g["id"], "C3", v, f"{ctx.format(X=X)}\n{q.format(X=X)}\n\n{INSTR}", SCHEMA))
        for v, t in enumerate(C4):
            calls.append(call(f"C4|{g['id']}|{v}", g["id"], "C4", v, f"{t.format(X=X, NS=NS, L=L)}\n\n{INSTR}", SCHEMA))
        calls.append(call(f"P1|{g['id']}|0", g["id"], "P1", 0, P1.format(D=D, NS=NS) + " Respond only with JSON.", P1_SCHEMA))
        calls.append(call(f"P2T|{g['id']}|0", g["id"], "P2T", 0, P2.format(X=X, D=D, NS=NS) + " Respond only with JSON.", P2_SCHEMA))
        calls.append(call(f"P2F|{g['id']}|0", g["id"], "P2F", 0, P2.format(X=X, D=g["foil_desc"], NS=NS) + " Respond only with JSON.", P2_SCHEMA))
    with open(out, "w", encoding="utf-8") as fh:
        for c in calls: fh.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(len(calls), "calls")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
