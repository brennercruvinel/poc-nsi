"""Deterministic tests for the v3 scorer. Run: python -I -m unittest discover -s tests"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import score_v3 as S  # noqa: E402

CANON = os.path.join(os.path.dirname(__file__), "..", "data", "namespace_canon.json")
A = lambda *names: [S.norm(n) for n in names]
# OMA: target IOC Oman; competitors ICAO Oman Air, IATA Eppley Airfield
OMA = {"OMA|lng/ioc": A("Oman", "Sultanate of Oman", "Uman"), "OMA|trp/ica2": A("Oman Air", "Oman Airline"), "OMA|trp/iata": A("Eppley Airfield", "Omaha Eppley Airfield")}
ARU = {"ARU|lng/ioc": A("Aruba", "Country of Aruba", "Island of Aruba"), "ARU|trp/iata": A("Araçatuba Airport"), "ARU|trp/ica2": A("Aruba Airlines")}
BRU = {"BRU|lng/ioc": A("Brunei Darussalam", "Brunei", "Negara Brunei Darussalam"), "BRU|trp/iata": A("Brussels Airport", "Brussels National", "Zaventem Airport"),
       "BRU|trp/ica2": A("Belavia Belarusian Airlines", "Belavia")}
ALL = {"ALL|fin/i42": S.active_aliases(["ALL", "Albanian lek", "Lek"], "Lek", "ALL"), "ALL|fin/tck": A("Allstate", "Allstate Insurance", "The Allstate Corporation")}
VAN = {"VAN|lng/ioc": S.active_aliases(["Republic of Vanuatu", "VAN", "VUT", "Vanuatu", "van", "vu", "vut"], "Vanuatu", "VAN"),
       "VAN|trp/iata": S.active_aliases(["Ferit Melen Airport", "LTCI", "VAN", "Van Ferit Melen", "Van Ferit Melen Airport"], "Van Ferit Melen Airport", "VAN")}


class Entity(unittest.TestCase):
    def ev(self, text, rs, lit, tgt): return S.entity_eval(text, rs, lit, tgt)[:2]

    def test_exact_and_wrappers(self):
        self.assertEqual(self.ev("Oman", OMA, "OMA", "OMA|lng/ioc"), ("CORRECT", "exact"))
        self.assertEqual(self.ev("Sultanate of Oman", OMA, "OMA", "OMA|lng/ioc"), ("CORRECT", "exact"))
        self.assertEqual(self.ev("Oman (country)", OMA, "OMA", "OMA|lng/ioc"), ("CORRECT", "phrase"))
        self.assertEqual(self.ev("Aruba (ARU)", ARU, "ARU", "ARU|lng/ioc"), ("CORRECT", "phrase"))

    def test_competitor_is_not_target(self):
        # the known v1 defect: 'Oman Air' contains 'Oman'
        self.assertEqual(self.ev("Oman Air", OMA, "OMA", "OMA|lng/ioc"), ("COMPETITOR", "exact"))
        self.assertEqual(self.ev("Aruba Airlines", ARU, "ARU", "ARU|lng/ioc"), ("COMPETITOR", "exact"))
        self.assertEqual(self.ev("Oman", OMA, "OMA", "OMA|trp/ica2"), ("COMPETITOR", "exact"))
        self.assertEqual(self.ev("Brussels Airport", BRU, "BRU", "BRU|lng/ioc"), ("COMPETITOR", "exact"))

    def test_no_subset_matching(self):
        # city name alone is neither the airport nor the country
        self.assertEqual(self.ev("Brussels", BRU, "BRU", "BRU|trp/iata"), ("UNRESOLVED", "partial_target"))
        self.assertEqual(self.ev("Brussels", BRU, "BRU", "BRU|lng/ioc"), ("UNRESOLVED", "partial_competitor"))
        self.assertEqual(self.ev("Belgium", BRU, "BRU", "BRU|lng/ioc"), ("OTHER", "none"))
        self.assertEqual(self.ev("Oman Airport", OMA, "OMA", "OMA|lng/ioc"), ("UNRESOLVED", "partial_both"))  # oman is in Oman and in Oman Air
        self.assertEqual(self.ev("Aruba Airline", ARU, "ARU", "ARU|lng/ioc"), ("UNRESOLVED", "partial_both"))
        self.assertEqual(self.ev("Aruba Airport", ARU, "ARU", "ARU|trp/iata"), ("UNRESOLVED", "partial_competitor"))

    def test_short_real_names_and_codes(self):
        self.assertIn("lek", ALL["ALL|fin/i42"]); self.assertNotIn("all", ALL["ALL|fin/i42"])
        self.assertEqual(self.ev("Lek", ALL, "ALL", "ALL|fin/i42"), ("CORRECT", "exact"))
        self.assertEqual(self.ev("Albanian lek (ALL)", ALL, "ALL", "ALL|fin/i42"), ("CORRECT", "phrase"))
        self.assertEqual(self.ev("ALL", ALL, "ALL", "ALL|fin/i42"), ("UNRESOLVED", "no_entity"))
        self.assertEqual(self.ev("Allstate Corporation", ALL, "ALL", "ALL|fin/i42"), ("COMPETITOR", "phrase"))
        self.assertNotIn("van", VAN["VAN|lng/ioc"])  # lowercase ISO alias must not make 'Van' match Vanuatu
        self.assertEqual(self.ev("Van", VAN, "VAN", "VAN|lng/ioc"), ("UNRESOLVED", "no_entity"))
        self.assertEqual(self.ev("Van Airport", VAN, "VAN", "VAN|trp/iata"), ("UNRESOLVED", "partial_target"))

    def test_both_sides_strong_is_unresolved(self):
        self.assertEqual(self.ev("Oman Air, Sultanate of Oman", OMA, "OMA", "OMA|lng/ioc"), ("UNRESOLVED", "both"))

    def test_bag_equality(self):
        self.assertEqual(self.ev("Airport Brussels", BRU, "BRU", "BRU|trp/iata"), ("CORRECT", "exact"))

    def test_c1_no_target(self):
        self.assertEqual(S.entity_eval("Oman Air", OMA, "OMA")[0:3], ("CORRECT", "exact", "OMA|trp/ica2"))
        self.assertEqual(S.entity_eval("Omaha", OMA, "OMA")[:2], ("UNRESOLVED", "partial"))


class Namespace(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.c = S.Canon(CANON)

    def ev(self, asked, s): return self.c.evaluate(asked, self.c.canon(s))

    def test_related_systems_never_merge(self):
        self.assertEqual(self.ev("lng/ioc", "ISO 3166-1 alpha-3"), "INCORRECT")
        self.assertEqual(self.ev("lng/i31", "ISO 3166-1 alpha-2"), "INCORRECT")
        self.assertEqual(self.ev("trp/iata", "ICAO"), "INCORRECT")
        self.assertEqual(self.ev("trp/ica2", "IATA"), "INCORRECT")
        self.assertEqual(self.ev("trp/iata", "IATA airline code"), "INCORRECT")
        self.assertEqual(self.ev("lng/ioc", "FIFA country code"), "INCORRECT")

    def test_aliases_of_same_system(self):
        self.assertEqual(self.ev("trp/iata", "IATA airport code system"), "CORRECT")
        self.assertEqual(self.ev("trp/iata", "IATA"), "EQUIVALENT")
        self.assertEqual(self.ev("trp/ica2", "ICAO"), "EQUIVALENT")
        self.assertEqual(self.ev("trp/ica2", "ICAO airline designator"), "EQUIVALENT")
        self.assertEqual(self.ev("lng/ioc", "IOC"), "CORRECT")
        self.assertEqual(self.ev("fin/i42", "ISO 4217"), "CORRECT")
        self.assertEqual(self.ev("fin/tck", "NYSE"), "EQUIVALENT")
        self.assertEqual(self.ev("cmp/dns", "DNS resource record types"), "CORRECT")

    def test_unresolved(self):
        for s in ("acronym", "unknown", "HTG", "", None, "aviation"): self.assertEqual(self.ev("fin/i42", s), "UNRESOLVED")

    def test_raw_preserved(self):
        s, canon, rule, conf = self.c.canon("Iata Airport Code")
        self.assertEqual((s, canon), ("iata airport code", "trp/iata")); self.assertTrue(rule and conf)


class Behaviour(unittest.TestCase):
    def test_failures(self):
        self.assertEqual(S.behaviour({"finish": "length"}, None), ("FAILURE", "TRUNCATED"))
        self.assertEqual(S.behaviour({"finish": "stop"}, None), ("FAILURE", "INVALID_JSON"))
        self.assertEqual(S.behaviour({}, {"status": "maybe", "readings": []}), ("FAILURE", "SCHEMA"))
        self.assertEqual(S.behaviour({}, {"status": "answer", "readings": "x"}), ("FAILURE", "SCHEMA"))
        self.assertEqual(S.behaviour({}, {"status": "answer", "readings": []}), ("FAILURE", "SCHEMA"))

    def test_kinds(self):
        self.assertEqual(S.behaviour({}, {"status": "unknown", "readings": []})[0], "ABSTAIN")
        self.assertEqual(S.behaviour({}, {"status": "ambiguous", "readings": [{}]})[0], "AMBIGUOUS")
        self.assertEqual(S.behaviour({}, {"status": "answer", "readings": [{}]})[0], "SINGLE")
        self.assertEqual(S.behaviour({}, {"status": "answer", "readings": [{}, {}]})[0], "MULTI")

    def test_parse_truncated_is_none(self):
        self.assertIsNone(S.parse('{"status": "answer", "readings": [{"system": "IATA", "entity": "X"}, {"system": "IA'))


class Derived(unittest.TestCase):
    R = lambda self, *ents: [{"entity": e, "evidence": "exact", "matched": "m" + str(i), "ns_eval": ""} for i, e in enumerate(ents)]

    def test_c234(self):
        self.assertEqual(S.derive_c234("SINGLE", self.R("CORRECT")), "CORRECT")
        self.assertEqual(S.derive_c234("MULTI", self.R("CORRECT", "OTHER")), "MIXED")       # wrong claim is not discarded
        self.assertEqual(S.derive_c234("MULTI", self.R("CORRECT", "COMPETITOR")), "MIXED")
        self.assertEqual(S.derive_c234("SINGLE", self.R("COMPETITOR")), "COMPETING")
        self.assertEqual(S.derive_c234("MULTI", self.R("OTHER", "UNRESOLVED")), "UNRESOLVED")
        self.assertEqual(S.derive_c234("SINGLE", self.R("OTHER")), "OTHER_WRONG")
        self.assertEqual(S.derive_c234("AMBIGUOUS", self.R("CORRECT")), "AMBIG_FLAG")
        self.assertEqual(S.derive_c234("ABSTAIN", []), "UNKNOWN")
        self.assertEqual(S.derive_c234("FAILURE", []), "FORMAT")

    def test_c1(self):
        self.assertEqual(S.derive_c1("MULTI", self.R("CORRECT", "CORRECT"), False, "m0"), ("MULTI", ""))
        self.assertEqual(S.derive_c1("AMBIGUOUS", self.R("CORRECT"), False, "m0"), ("PARTIAL", "with_one"))
        self.assertEqual(S.derive_c1("SINGLE", self.R("CORRECT"), False, "m0"), ("SINGLE", "top"))
        self.assertEqual(S.derive_c1("SINGLE", self.R("CORRECT"), False, "zz"), ("SINGLE", "other"))
        self.assertEqual(S.derive_c1("SINGLE", self.R("OTHER"), False, "m0"), ("WRONG", ""))
        self.assertEqual(S.derive_c1("AMBIGUOUS", self.R("OTHER"), True, "m0"), ("AMBIG_DECLARED", "without_target"))
        self.assertEqual(S.derive_c1("SINGLE", self.R("CORRECT"), True, "m0"), ("SINGLE_CORRECT", ""))
        self.assertEqual(S.derive_c1("FAILURE", [], True, "m0"), ("FORMAT", ""))

    def test_ns_of_correct_prefers_best(self):
        reads = [{"entity": "CORRECT", "ns_eval": "INCORRECT"}, {"entity": "CORRECT", "ns_eval": "EQUIVALENT"}, {"entity": "OTHER", "ns_eval": "CORRECT"}]
        self.assertEqual(S.ns_of_correct(reads), "EQUIVALENT")


class AliasPolicy(unittest.TestCase):
    def test_rules(self):
        self.assertEqual(S.alias_policy("ARU", "ARU"), "equals_literal")
        self.assertEqual(S.alias_policy("ABW", "ARU"), "code_like_short")
        self.assertEqual(S.alias_policy("aw", "ARU"), "code_like_short")
        self.assertEqual(S.alias_policy("SBAU", "ARU"), "code_like_upper")
        self.assertEqual(S.alias_policy("CO $", "COP"), "code_like_short")
        self.assertEqual(S.alias_policy("$", "COP"), "empty_after_normalisation")
        self.assertEqual(S.alias_policy("null", "PSD"), "generic_or_null")
        self.assertEqual(S.alias_policy("peso", "COP"), "generic_or_null")
        for ok in ("Lek", "Jay", "Viti", "MORUYA", "IMPEX", "Holland", "Oman Air"): self.assertEqual(S.alias_policy(ok, "XXX"), "", ok)


if __name__ == "__main__":
    unittest.main()
