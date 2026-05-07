from __future__ import annotations

from donebench.core.schema import CriterionAtom


def match_atoms(gold: list[CriterionAtom], predicted: list[CriterionAtom]) -> tuple[set[str], set[str]]:
    gold_keys = {atom.canonical_key: atom.id for atom in gold if atom.criticality == "hard"}
    pred_keys = {atom.canonical_key: atom.id for atom in predicted if atom.criticality == "hard"}
    matched_keys = set(gold_keys).intersection(pred_keys)
    return {gold_keys[key] for key in matched_keys}, {pred_keys[key] for key in matched_keys}


def normalize_freeform_criteria(texts: list[str], gold_hint: list[CriterionAtom] | None = None) -> list[CriterionAtom]:
    if not gold_hint:
        return []
    normalized: list[CriterionAtom] = []
    lowered = " ".join(texts).lower()
    for atom in gold_hint:
        important_terms = [part for part in atom.text.lower().replace(".", "").split() if len(part) > 4]
        if important_terms and sum(term in lowered for term in important_terms) >= min(2, len(important_terms)):
            normalized.append(atom)
    return normalized
