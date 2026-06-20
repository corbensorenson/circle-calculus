"""Parameterized Circle AI contract receipts.

The generated contract pack is the fixture/audit artifact. This module is the
runtime-facing layer: a downstream project supplies parameters, and receives a
small theorem-linked receipt with explicit proof boundaries.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .circle_ai import (
    certify_kv_cache_adapter_request_trace,
    certify_kv_cache_batch,
    certify_kv_cache_live_window,
    certify_kv_cache_live_window_request,
    certify_kv_cache_sink_window,
    certify_kv_cache_window,
    certify_stride_family_coverage,
)
from .circle_ai_contract_consumer import (
    FINGERPRINT_ALGORITHM,
    contract_recommendations,
    readiness_summary,
    require_ready_contract,
    validate_consumer_pack,
)
from .circle_ai_contracts import build_contract_pack, build_recurrence_schedule_contract
from .rope_certifier import (
    RoPEConfig,
    certify_rope_positions,
    certify_standard_channel0_d19_range_request_margin_bracket,
)


REQUEST_SCHEMA_ID = "circle_calculus.ai_contract_request.v0"
RECEIPT_SCHEMA_ID = "circle_calculus.ai_contract_receipt.v0"
REQUEST_SCHEMA_PATH = "site/data/generated/circle_ai_contract_request.schema.json"
RECEIPT_SCHEMA_PATH = "site/data/generated/circle_ai_contract_receipt.schema.json"

SUPPORTED_CONTRACT_KINDS = (
    "rope_position_distinguishability",
    "kv_cache_ring_buffer",
    "sparse_attention_coverage",
    "recurrence_schedule",
)
KIND_ALIASES = {
    "rope": "rope_position_distinguishability",
    "rope_position_distinguishability": "rope_position_distinguishability",
    "kv": "kv_cache_ring_buffer",
    "kv-cache": "kv_cache_ring_buffer",
    "kv_cache": "kv_cache_ring_buffer",
    "kv_cache_ring_buffer": "kv_cache_ring_buffer",
    "sparse": "sparse_attention_coverage",
    "sparse-attention": "sparse_attention_coverage",
    "sparse_attention": "sparse_attention_coverage",
    "sparse_attention_coverage": "sparse_attention_coverage",
    "recurrence": "recurrence_schedule",
    "recurrence-schedule": "recurrence_schedule",
    "recurrence_schedule": "recurrence_schedule",
}
STATUS_VALUES = (
    "proved",
    "impossible",
    "undecided",
    "numerical_only",
    "outside_scope",
)
ROPE_DIRICHLET_GUARDRAIL_THEOREM_IDS = (
    "AIRA-T0239",
    "AIRA-T0240",
    "AIRA-T0241",
)


def canonical_contract_kind(kind: str) -> str:
    """Return the canonical contract kind, accepting CLI-friendly aliases."""

    canonical = KIND_ALIASES.get(kind)
    if canonical is None:
        supported = ", ".join(sorted(KIND_ALIASES))
        raise ValueError(f"unsupported contract kind {kind!r}; expected one of {supported}")
    return canonical


def parse_fraction(value: str | Fraction | None) -> Fraction | None:
    """Parse a human margin like ``1/328459`` or ``0.001`` into a Fraction."""

    if value is None or isinstance(value, Fraction):
        return value
    text = str(value).strip()
    if not text:
        raise ValueError("fraction value must be non-empty")
    return Fraction(text)


def _strip_fingerprint_fields(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_fingerprint_fields(child)
            for key, child in value.items()
            if key != "receipt_content_fingerprint"
        }
    if isinstance(value, list):
        return [_strip_fingerprint_fields(child) for child in value]
    if isinstance(value, tuple):
        return [_strip_fingerprint_fields(child) for child in value]
    return value


def _json_fingerprint(value: Any) -> str:
    payload = json.dumps(
        _strip_fingerprint_fields(value),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _unique_strings(values: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return tuple(ordered)


def _default_pack(pack: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(pack) if pack is not None else build_contract_pack()


def _support_block(pack: dict[str, Any], kind: str) -> dict[str, Any]:
    failures = validate_consumer_pack(pack)
    if failures:
        raise ValueError("invalid Circle AI contract pack: " + "; ".join(failures))
    contract = require_ready_contract(pack, kind)
    summary = readiness_summary(pack, kind)
    fingerprint_index = pack.get("contract_fingerprint_index", {})
    contract_fingerprint = {}
    if isinstance(fingerprint_index, dict):
        value = fingerprint_index.get(kind, {})
        if isinstance(value, dict):
            contract_fingerprint = value
    manifest_info = _manifest_proved_theorem_ids(pack)
    return {
        "schema_id": pack.get("schema_id"),
        "contract_id": summary.contract_id,
        "kind": kind,
        "fixture_status": contract.get("status"),
        "ready_for_downstream_fixture_use": summary.ready,
        "contract_pack_fingerprint": pack.get("pack_content_fingerprint"),
        "contract_content_fingerprint": contract_fingerprint.get(
            "content_fingerprint"
        ),
        "content_fingerprint_algorithm": pack.get("content_fingerprint_algorithm"),
        "quickstart_docs": list(summary.quickstart_docs),
        "living_book_pages": list(summary.living_book_pages),
        "entrypoints": list(summary.entrypoints),
        "validation_commands": list(summary.validation_commands),
        "source_paper": summary.source_paper,
        "planner_recommendations": [
            {
                "id": recommendation.get("id"),
                "action_kind": recommendation.get("action_kind"),
                "status": recommendation.get("status"),
                "coverage_scope": recommendation.get("coverage_scope"),
                "theorem_ids": list(recommendation.get("theorem_ids", [])),
            }
            for recommendation in contract_recommendations(pack, kind)
        ],
        "not_claimed": summary.not_claimed,
        "contract_theorem_count": summary.theorem_count,
        "contract_theorem_ids": list(summary.theorem_ids),
        "contract_dictionary_ids": list(summary.dictionary_ids),
        "theorem_index_path": manifest_info["path"],
        "theorem_index_available": manifest_info["available"],
        "theorem_index_proved_count": len(manifest_info["proved_ids"]),
    }


def _manifest_proved_theorem_ids(pack: Mapping[str, Any]) -> dict[str, Any]:
    proof_indexes = pack.get("proof_indexes", {})
    theorem_index = None
    if isinstance(proof_indexes, Mapping):
        value = proof_indexes.get("theorem_index")
        if isinstance(value, str):
            theorem_index = value
    if theorem_index is None:
        return {"path": None, "available": False, "proved_ids": set()}
    candidates = [Path(theorem_index)]
    repo_root = Path(__file__).resolve().parents[2]
    candidates.append(repo_root / theorem_index)
    for candidate in candidates:
        if not candidate.exists():
            continue
        data = json.loads(candidate.read_text(encoding="utf-8"))
        records = data.get("theorems", []) if isinstance(data, dict) else []
        proved_ids = {
            record["id"]
            for record in records
            if isinstance(record, dict)
            and isinstance(record.get("id"), str)
            and record.get("canonical_status", record.get("status"))
            in {"proved", "lean_proved"}
        }
        return {
            "path": theorem_index,
            "available": True,
            "proved_ids": proved_ids,
        }
    return {"path": theorem_index, "available": False, "proved_ids": set()}


def _proof_status(
    *,
    theorem_ids: Sequence[str],
    support: Mapping[str, Any],
    pack: Mapping[str, Any],
) -> dict[str, Any]:
    ordered_ids = _unique_strings(theorem_ids)
    contract_ids = set(support.get("contract_theorem_ids", []))
    manifest_info = _manifest_proved_theorem_ids(pack)
    manifest_proved_ids = set(manifest_info["proved_ids"])
    proved_ids = set(contract_ids)
    if support.get("ready_for_downstream_fixture_use"):
        proved_ids |= contract_ids
    proved_ids |= manifest_proved_ids
    resolved_ids = contract_ids | manifest_proved_ids
    unresolved = tuple(
        theorem_id for theorem_id in ordered_ids if theorem_id not in resolved_ids
    )
    unproved = tuple(
        theorem_id
        for theorem_id in ordered_ids
        if theorem_id in resolved_ids and theorem_id not in proved_ids
    )
    all_resolved = not unresolved
    all_proved = all_resolved and not unproved
    return {
        "theorem_ids": list(ordered_ids),
        "theorem_count": len(ordered_ids),
        "all_theorem_ids_resolved": all_resolved,
        "all_theorem_ids_proved": all_proved,
        "unresolved_theorem_ids": list(unresolved),
        "unproved_theorem_ids": list(unproved),
        "theorem_index_path": manifest_info["path"],
        "theorem_index_available": manifest_info["available"],
        "proof_source": (
            "The generated contract pack resolves theorem ids to proved "
            "manifest entries and compiled Lean declarations. For custom "
            "parameter receipts, the generated theorem manifest is also used "
            "when available. This receipt does not re-run Lean."
        ),
    }


def _base_receipt(
    *,
    kind: str,
    request_parameters: Mapping[str, Any],
    normalized_parameters: Mapping[str, Any],
    status: str,
    request_passed: bool | None,
    evidence: Mapping[str, Any],
    theorem_ids: Sequence[str],
    proof_layers: Mapping[str, Any],
    not_claimed: Sequence[str],
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    canonical = canonical_contract_kind(kind)
    if status not in STATUS_VALUES:
        raise ValueError(f"unsupported receipt status {status!r}")
    pack_dict = _default_pack(pack)
    support = _support_block(pack_dict, canonical)
    proof_status = _proof_status(
        theorem_ids=theorem_ids,
        support=support,
        pack=pack_dict,
    )
    request_object = {
        "schema_id": REQUEST_SCHEMA_ID,
        "kind": canonical,
        "parameters": dict(request_parameters),
    }
    normalized_object = dict(normalized_parameters)
    receipt = {
        "schema_id": RECEIPT_SCHEMA_ID,
        "request_schema_id": REQUEST_SCHEMA_ID,
        "contract_pack_schema_id": support["schema_id"],
        "kind": canonical,
        "contract_id": support["contract_id"],
        "status": status,
        "request_passed": request_passed,
        "request": request_object,
        "request_content_fingerprint": _json_fingerprint(request_object),
        "normalized_request": normalized_object,
        "normalized_request_fingerprint": _json_fingerprint(normalized_object),
        "evidence": dict(evidence),
        "proof_status": proof_status,
        "proof_layers": dict(proof_layers),
        "recommendations": list(support["planner_recommendations"]),
        "validation_commands": list(support["validation_commands"]),
        "support": support,
        "not_claimed": list(_unique_strings(not_claimed)),
        "content_fingerprint_algorithm": FINGERPRINT_ALGORITHM,
        "receipt_content_fingerprint": "",
    }
    receipt["receipt_content_fingerprint"] = _json_fingerprint(receipt)
    failures = validate_contract_receipt(receipt)
    if failures:
        raise ValueError("invalid Circle AI contract receipt: " + "; ".join(failures))
    return receipt


def _d19_status_to_receipt_status(status: str) -> str:
    if status == "proved":
        return "proved"
    if status == "impossible":
        return "impossible"
    if status == "undecided_margin_gap":
        return "undecided"
    if status == "outside_range":
        return "outside_scope"
    return "numerical_only"


def _margin_relation_to_inv_context(
    *,
    margin: Fraction | None,
    inv_context_margin: Fraction,
) -> str | None:
    if margin is None:
        return None
    if margin < inv_context_margin:
        return "below_dirichlet_ceiling"
    if margin == inv_context_margin:
        return "at_dirichlet_ceiling"
    return "above_dirichlet_ceiling"


def _rope_dirichlet_guardrail(
    *,
    context: int,
    requested_margin: Fraction | None,
) -> dict[str, Any]:
    """Return the theorem-backed finite-context ``1/context`` ceiling guardrail."""

    if context <= 1:
        return {
            "applies": False,
            "context": context,
            "inv_context_margin": None,
            "requested_margin": (
                str(requested_margin) if requested_margin is not None else None
            ),
            "requested_margin_relation_to_ceiling": None,
            "requested_margin_exceeds_ceiling": None,
            "requested_margin_at_or_below_ceiling": None,
            "theorem_backed": False,
            "theorem_ids": [],
            "claim": (
                "The Dirichlet finite-context guardrail applies only when "
                "context > 1."
            ),
            "non_claim": (
                "This does not classify a nontrivial real-phase margin request."
            ),
        }

    inv_context_margin = Fraction(1, context)
    relation = _margin_relation_to_inv_context(
        margin=requested_margin,
        inv_context_margin=inv_context_margin,
    )
    return {
        "applies": True,
        "context": context,
        "inv_context_margin": str(inv_context_margin),
        "requested_margin": (
            str(requested_margin) if requested_margin is not None else None
        ),
        "requested_margin_relation_to_ceiling": relation,
        "requested_margin_exceeds_ceiling": (
            None if requested_margin is None else requested_margin > inv_context_margin
        ),
        "requested_margin_at_or_below_ceiling": (
            None if requested_margin is None else requested_margin <= inv_context_margin
        ),
        "theorem_backed": True,
        "theorem_ids": list(ROPE_DIRICHLET_GUARDRAIL_THEOREM_IDS),
        "claim": (
            "For any turn ratio and context > 1, there is an in-context "
            "nearest-integer witness with error at most 1/context; therefore "
            "any advertised finite-context margin strictly larger than "
            "1/context is impossible."
        ),
        "non_claim": (
            "This does not prove that a requested margin at or below 1/context "
            "holds; it is an upper-bound guardrail."
        ),
    }


def build_rope_receipt(
    *,
    head_dim: int = 128,
    base: float = 10000.0,
    context: int = 32768,
    tolerance: float = 1e-6,
    discretization: str = "round",
    requested_margin: str | Fraction | None = None,
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a theorem-linked receipt for one RoPE configuration."""

    margin = parse_fraction(requested_margin)
    config = RoPEConfig(
        head_dim=head_dim,
        base=base,
        context_length=context,
        tolerance=tolerance,
        discretization=discretization,
    )
    certificate = certify_rope_positions(config).to_dict()
    theorem_ids = list(certificate["theorem_ids"])
    evidence: dict[str, Any] = {
        "exact_discrete_pass": certificate["exact_discrete"]["pass_exact"],
        "exact_discretized_periods": certificate["exact_discrete"][
            "discretized_periods"
        ],
        "exact_total_bank_collision_pair_count": certificate["exact_discrete"][
            "total_bank_collision_pair_count"
        ],
        "exact_common_collision_gap": certificate["exact_discrete"][
            "common_collision_gap"
        ],
        "exact_common_collision_gap_reaches_context": certificate[
            "exact_discrete"
        ]["common_collision_gap_reaches_context"],
        "exact_sample_collision_pairs": certificate["exact_discrete"][
            "sample_collision_pairs"
        ],
        "real_phase_numerical_pass_margin": certificate["real_phase_margin"][
            "pass_margin"
        ],
        "real_phase_numerical_worst_margin_radians": certificate[
            "real_phase_margin"
        ]["worst_margin_radians"],
        "real_phase_numerical_worst_gap": certificate["real_phase_margin"][
            "worst_gap"
        ],
        "real_phase_numerical_worst_channel_index": certificate[
            "real_phase_margin"
        ]["worst_channel_index"],
        "real_phase_numerical_near_collision_gaps": certificate[
            "real_phase_margin"
        ]["near_collision_gaps"],
        "proof_layer_summaries": [
            {
                "layer": layer["layer"],
                "status": layer["status"],
                "theorem_backed": layer["theorem_backed"],
                "theorem_ids": layer["theorem_ids"],
            }
            for layer in certificate["proof_layers"]
        ],
    }
    dirichlet_guardrail = _rope_dirichlet_guardrail(
        context=context,
        requested_margin=margin,
    )
    evidence["real_phase_dirichlet_guardrail"] = dirichlet_guardrail
    if dirichlet_guardrail["applies"]:
        theorem_ids.extend(dirichlet_guardrail["theorem_ids"])
    status = "proved"
    request_passed: bool | None = bool(certificate["exact_discrete"]["pass_exact"])
    d19_receipt_status: str | None = None
    if margin is not None:
        d19 = certify_standard_channel0_d19_range_request_margin_bracket(
            requested_context=context,
            requested_margin=margin,
        ).to_dict()
        evidence["standard_channel0_d19_request_classifier"] = d19
        theorem_ids.extend(d19["theorem_ids"])
        d19_receipt_status = _d19_status_to_receipt_status(d19["request_status"])
        status = d19_receipt_status
        if status == "proved":
            request_passed = True
        elif status == "impossible":
            request_passed = False
        elif status in {"undecided", "outside_scope"}:
            request_passed = None
    if dirichlet_guardrail["requested_margin_exceeds_ceiling"] is True:
        status = "impossible"
        request_passed = False
    proof_layers = {
        "proved_fields": [
            "exact_discrete_pass",
            "exact_total_bank_collision_pair_count",
            "exact_common_collision_gap",
        ],
        "computed_fields": [
            "exact_discretized_periods",
            "exact_sample_collision_pairs",
        ],
        "numerical_only_fields": [
            "real_phase_numerical_pass_margin",
            "real_phase_numerical_worst_margin_radians",
            "real_phase_numerical_worst_gap",
            "real_phase_numerical_near_collision_gaps",
        ],
        "unsupported_fields": [
            "full all-channel real-valued RoPE separation theorem",
            "model quality or useful context-length improvement",
        ],
    }
    if dirichlet_guardrail["applies"]:
        proof_layers["proved_fields"].append("real_phase_dirichlet_guardrail")
    else:
        proof_layers["unsupported_fields"].append(
            "real_phase_dirichlet_guardrail requires context > 1"
        )
    if d19_receipt_status in {"proved", "impossible", "undecided"}:
        proof_layers["proved_fields"].append(
            "standard_channel0_d19_request_classifier"
        )
    elif d19_receipt_status == "outside_scope":
        proof_layers["unsupported_fields"].append(
            "standard_channel0_d19_request_classifier outside its proved context range"
        )
    return _base_receipt(
        kind="rope_position_distinguishability",
        request_parameters={
            "head_dim": head_dim,
            "base": base,
            "context": context,
            "tolerance": tolerance,
            "discretization": discretization,
            "requested_margin": str(margin) if margin is not None else None,
        },
        normalized_parameters={
            "head_dim": config.head_dim,
            "base": config.base,
            "context_length": config.context_length,
            "tolerance": config.tolerance,
            "discretization": config.discretization,
            "requested_margin": str(margin) if margin is not None else None,
        },
        status=status,
        request_passed=request_passed,
        evidence=evidence,
        theorem_ids=theorem_ids,
        proof_layers=proof_layers,
        not_claimed=[
            certificate["claim_boundary"],
            "The numerical real-phase scan is executable support, not a proof.",
        ],
        pack=pack,
    )


def build_kv_cache_receipt(
    *,
    cache_size: int,
    current: int,
    token: int,
    batch_tokens: Sequence[int] = (),
    sink_size: int = 0,
    request_id: str = "read_request",
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a theorem-linked receipt for one KV-cache ring-buffer request."""

    requested_tokens = tuple(batch_tokens) or (token,)
    window = asdict(
        certify_kv_cache_window(
            cache_size=cache_size,
            current=current,
            token=token,
        )
    )
    batch = asdict(
        certify_kv_cache_batch(
            cache_size=cache_size,
            current=current,
            tokens=requested_tokens,
        )
    )
    adapter_request = asdict(
        certify_kv_cache_adapter_request_trace(
            cache_size=cache_size,
            current=current,
            requested_tokens=requested_tokens,
            request_id=request_id,
        )
    )
    live_window = asdict(
        certify_kv_cache_live_window(
            cache_size=cache_size,
            current=current,
        )
    )
    live_window_request = asdict(
        certify_kv_cache_live_window_request(
            cache_size=cache_size,
            current=current,
            request_id=f"{request_id}_generated_live_window",
        )
    )
    evidence: dict[str, Any] = {
        "window_certificate": window,
        "batch_certificate": batch,
        "adapter_request_trace_certificate": adapter_request,
        "live_window_certificate": live_window,
        "live_window_request_certificate": live_window_request,
    }
    theorem_ids = list(window["theorem_ids"])
    theorem_ids.extend(batch["theorem_ids"])
    theorem_ids.extend(adapter_request["theorem_ids"])
    theorem_ids.extend(live_window["theorem_ids"])
    theorem_ids.extend(live_window_request["theorem_ids"])
    theorem_ids.extend(live_window_request["fixture_theorem_ids"])
    if sink_size:
        sink_window = asdict(
            certify_kv_cache_sink_window(
                sink_size=sink_size,
                cache_size=cache_size,
                current=current,
            )
        )
        evidence["sink_window_certificate"] = sink_window
        theorem_ids.extend(sink_window["theorem_ids"])
        theorem_ids.extend(sink_window["fixture_theorem_ids"])
    return _base_receipt(
        kind="kv_cache_ring_buffer",
        request_parameters={
            "cache_size": cache_size,
            "current": current,
            "token": token,
            "batch_tokens": list(batch_tokens),
            "sink_size": sink_size,
            "request_id": request_id,
        },
        normalized_parameters={
            "cache_size": cache_size,
            "current": current,
            "token": token,
            "requested_tokens": list(requested_tokens),
            "sink_size": sink_size,
            "request_id": request_id,
        },
        status="proved",
        request_passed=bool(adapter_request["pass_certificate"]),
        evidence=evidence,
        theorem_ids=theorem_ids,
        proof_layers={
            "proved_fields": [
                "window_certificate",
                "batch_certificate",
                "adapter_request_trace_certificate",
                "live_window_certificate",
                "live_window_request_certificate",
                "sink_window_certificate",
            ],
            "computed_fields": [],
            "numerical_only_fields": [],
            "unsupported_fields": [
                "paging policy",
                "throughput",
                "memory saving",
                "retrieval quality",
                "implementation correctness",
            ],
        },
        not_claimed=[
            "This is a proof-carrying finite ring-buffer indexing, retained-window, "
            "and modeled adapter request-trace certificate. It is not a paging-policy, "
            "throughput, memory-saving, retrieval-quality, implementation-correctness, "
            "deployment-safety, or model-quality claim."
        ],
        pack=pack,
    )


def build_sparse_attention_receipt(
    *,
    context: int,
    strides: Sequence[int],
    path_length: int,
    local_window: int,
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a theorem-linked receipt for one sparse-attention plan."""

    certificate = asdict(
        certify_stride_family_coverage(
            sequence_length=context,
            strides=tuple(strides),
            path_length=path_length,
            local_window=local_window,
        )
    )
    return _base_receipt(
        kind="sparse_attention_coverage",
        request_parameters={
            "context": context,
            "strides": list(strides),
            "path_length": path_length,
            "local_window": local_window,
        },
        normalized_parameters={
            "sequence_length": certificate["sequence_length"],
            "strides": list(certificate["strides"]),
            "path_length": certificate["path_length"],
            "local_window": certificate["local_window"],
        },
        status="proved",
        request_passed=bool(certificate["coverage_complete"]),
        evidence=certificate,
        theorem_ids=certificate["theorem_ids"],
        proof_layers={
            "proved_fields": [
                "coverage_complete",
                "covered_lags",
                "uncovered_lags",
                "first_uncovered_lag",
                "uncovered_lag_intervals",
                "candidate_budget_per_query",
                "theorem_side_lag_candidates",
                "theorem_side_query_candidates",
            ],
            "computed_fields": [],
            "numerical_only_fields": [],
            "unsupported_fields": [
                "attention quality",
                "runtime speed",
                "optimal sparse-layout design",
                "model accuracy",
            ],
        },
        not_claimed=[
            "This is a proof-carrying finite sparse-plan coverage and budget "
            "certificate. It is not an attention-quality, runtime, memory, "
            "optimal-layout, training, or model-quality claim."
        ],
        pack=pack,
    )


def build_recurrence_receipt(
    *,
    loop_period: int = 5,
    sample_index: int = 8,
    max_loops: int = 7,
    token_count: int = 8,
    selected_block_start: int = 2,
    selected_block_width: int = 3,
    shift_passes: int = 3,
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a theorem-linked receipt for one finite recurrence schedule."""

    payload = build_recurrence_schedule_contract(
        loop_period=loop_period,
        sample_index=sample_index,
        max_loops=max_loops,
        token_indices=tuple(range(token_count)),
        selected_block_start=selected_block_start,
        selected_block_width=selected_block_width,
        periodic_shift_passes=shift_passes,
    )
    fields = payload["fields"]
    return _base_receipt(
        kind="recurrence_schedule",
        request_parameters={
            "loop_period": loop_period,
            "sample_index": sample_index,
            "max_loops": max_loops,
            "token_count": token_count,
            "selected_block_start": selected_block_start,
            "selected_block_width": selected_block_width,
            "shift_passes": shift_passes,
        },
        normalized_parameters={
            "loop_period": fields["loop_period"],
            "sample_index": fields["sample_index"],
            "max_loops": fields["max_loops"],
            "token_count": len(fields["tokens"]),
            "selected_block_start": selected_block_start,
            "selected_block_width": selected_block_width,
            "periodic_shift_passes": fields["periodic_shift_passes"],
        },
        status="proved",
        request_passed=bool(payload["contract_passed"]),
        evidence=payload,
        theorem_ids=payload["theorem_ids"],
        proof_layers={
            "proved_fields": [
                "fields.required_steps",
                "fields.exit_step",
                "fields.active_token_count_trace",
                "fields.total_active_token_work",
                "fields.scheduled_work_saving",
                "fields.periodic_shift_required_steps_invariant",
                "fields.periodic_shift_active_at_step_invariant",
            ],
            "computed_fields": [],
            "numerical_only_fields": [],
            "unsupported_fields": [
                "reasoning quality",
                "training benefit",
                "recursive-transformer model quality",
            ],
        },
        not_claimed=[payload["not_claimed"]],
        pack=pack,
    )


def build_contract_receipt(
    kind: str,
    parameters: Mapping[str, Any],
    *,
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Dispatch to the receipt builder for ``kind``."""

    canonical = canonical_contract_kind(kind)
    params = dict(parameters)
    if canonical == "rope_position_distinguishability":
        return build_rope_receipt(pack=pack, **params)
    if canonical == "kv_cache_ring_buffer":
        return build_kv_cache_receipt(pack=pack, **params)
    if canonical == "sparse_attention_coverage":
        return build_sparse_attention_receipt(pack=pack, **params)
    if canonical == "recurrence_schedule":
        return build_recurrence_receipt(pack=pack, **params)
    raise ValueError(f"unsupported contract kind: {kind}")


def validate_contract_request(request: Mapping[str, Any]) -> list[str]:
    """Return request-shape failures for the public runner request object."""

    failures: list[str] = []
    if request.get("schema_id") != REQUEST_SCHEMA_ID:
        failures.append(f"schema_id must be {REQUEST_SCHEMA_ID!r}")
    kind = request.get("kind")
    if not isinstance(kind, str) or not kind:
        failures.append("kind must be a non-empty string")
    elif kind not in KIND_ALIASES:
        failures.append("kind must be a supported Circle AI contract kind or alias")
    parameters = request.get("parameters")
    if not isinstance(parameters, Mapping):
        failures.append("parameters must be an object")
    return failures


def build_contract_receipt_from_request(
    request: Mapping[str, Any],
    *,
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a receipt from a versioned public runner request object."""

    failures = validate_contract_request(request)
    if failures:
        raise ValueError("invalid Circle AI contract request: " + "; ".join(failures))
    kind = str(request["kind"])
    parameters = request["parameters"]
    assert isinstance(parameters, Mapping)
    try:
        return build_contract_receipt(kind, parameters, pack=pack)
    except TypeError as exc:
        raise ValueError(
            "invalid Circle AI contract request parameters: " + str(exc)
        ) from exc
    except ValueError as exc:
        message = str(exc)
        if message.startswith(
            ("invalid Circle AI contract pack", "invalid Circle AI contract receipt")
        ):
            raise
        raise ValueError(
            "invalid Circle AI contract request parameters: " + message
        ) from exc


def validate_contract_receipt(receipt: Mapping[str, Any]) -> list[str]:
    """Return receipt-shape failures. This is a JSON-level check, not Lean."""

    failures: list[str] = []
    if receipt.get("schema_id") != RECEIPT_SCHEMA_ID:
        failures.append(f"schema_id must be {RECEIPT_SCHEMA_ID!r}")
    if receipt.get("request_schema_id") != REQUEST_SCHEMA_ID:
        failures.append(f"request_schema_id must be {REQUEST_SCHEMA_ID!r}")
    kind = receipt.get("kind")
    if kind not in SUPPORTED_CONTRACT_KINDS:
        failures.append("kind must be a supported Circle AI contract kind")
    status = receipt.get("status")
    if status not in STATUS_VALUES:
        failures.append("status must be one of " + ", ".join(STATUS_VALUES))
    if receipt.get("content_fingerprint_algorithm") != FINGERPRINT_ALGORITHM:
        failures.append(
            f"content_fingerprint_algorithm must be {FINGERPRINT_ALGORITHM!r}"
        )
    fingerprint = receipt.get("receipt_content_fingerprint")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        failures.append("receipt_content_fingerprint must be a sha256 hex string")
    elif any(char not in "0123456789abcdef" for char in fingerprint):
        failures.append("receipt_content_fingerprint must be lowercase hex")
    elif fingerprint != _json_fingerprint(dict(receipt)):
        failures.append("receipt_content_fingerprint drifted from receipt content")
    request = receipt.get("request")
    if not isinstance(request, dict):
        failures.append("request must be an object")
    elif request.get("schema_id") != REQUEST_SCHEMA_ID:
        failures.append("request.schema_id must match request_schema_id")
    request_fingerprint = receipt.get("request_content_fingerprint")
    if not isinstance(request_fingerprint, str) or len(request_fingerprint) != 64:
        failures.append("request_content_fingerprint must be a sha256 hex string")
    elif any(char not in "0123456789abcdef" for char in request_fingerprint):
        failures.append("request_content_fingerprint must be lowercase hex")
    elif isinstance(request, dict) and request_fingerprint != _json_fingerprint(request):
        failures.append("request_content_fingerprint drifted from request content")
    normalized = receipt.get("normalized_request")
    if not isinstance(normalized, dict) or not normalized:
        failures.append("normalized_request must be a non-empty object")
    normalized_fingerprint = receipt.get("normalized_request_fingerprint")
    if not isinstance(normalized_fingerprint, str) or len(normalized_fingerprint) != 64:
        failures.append("normalized_request_fingerprint must be a sha256 hex string")
    elif any(char not in "0123456789abcdef" for char in normalized_fingerprint):
        failures.append("normalized_request_fingerprint must be lowercase hex")
    elif isinstance(normalized, dict) and normalized_fingerprint != _json_fingerprint(
        normalized
    ):
        failures.append(
            "normalized_request_fingerprint drifted from normalized_request content"
        )
    evidence = receipt.get("evidence")
    if not isinstance(evidence, dict) or not evidence:
        failures.append("evidence must be a non-empty object")
    proof_status = receipt.get("proof_status")
    if not isinstance(proof_status, dict):
        failures.append("proof_status must be an object")
    else:
        theorem_ids = proof_status.get("theorem_ids")
        if not isinstance(theorem_ids, list) or not theorem_ids:
            failures.append("proof_status.theorem_ids must be a non-empty list")
        if not isinstance(proof_status.get("theorem_count"), int):
            failures.append("proof_status.theorem_count must be an integer")
        if proof_status.get("all_theorem_ids_resolved") is not True:
            failures.append("all receipt theorem ids must resolve in the contract pack")
        if status in {"proved", "impossible"} and proof_status.get(
            "all_theorem_ids_proved"
        ) is not True:
            failures.append("proved/impossible receipts require proved theorem ids")
    support = receipt.get("support")
    if not isinstance(support, dict):
        failures.append("support must be an object")
    else:
        if not support.get("contract_id"):
            failures.append("support.contract_id must be present")
        if support.get("ready_for_downstream_fixture_use") is not True:
            failures.append("support.ready_for_downstream_fixture_use must be true")
        if not support.get("contract_pack_fingerprint"):
            failures.append("support.contract_pack_fingerprint must be present")
        if not support.get("contract_content_fingerprint"):
            failures.append("support.contract_content_fingerprint must be present")
    recommendations = receipt.get("recommendations")
    if not isinstance(recommendations, list) or not recommendations:
        failures.append("recommendations must be a non-empty list")
    elif not all(isinstance(recommendation, dict) for recommendation in recommendations):
        failures.append("recommendations must contain objects")
    validation_commands = receipt.get("validation_commands")
    if not isinstance(validation_commands, list) or not validation_commands:
        failures.append("validation_commands must be a non-empty list")
    elif not all(isinstance(command, str) and command for command in validation_commands):
        failures.append("validation_commands must contain non-empty strings")
    if not isinstance(receipt.get("not_claimed"), list) or not receipt.get(
        "not_claimed"
    ):
        failures.append("not_claimed must be a non-empty list")
    return failures


def receipt_summary_lines(receipt: Mapping[str, Any]) -> list[str]:
    """Return a compact text summary for humans."""

    proof_status = receipt["proof_status"]
    support = receipt["support"]
    lines = [
        (
            "circle_ai_contract_receipt="
            f"{receipt['status']} kind={receipt['kind']} "
            f"contract_id={receipt['contract_id']} "
            f"request_passed={receipt['request_passed']}"
        ),
        (
            "proof_status="
            f"theorems={proof_status['theorem_count']} "
            f"resolved={proof_status['all_theorem_ids_resolved']} "
            f"proved={proof_status['all_theorem_ids_proved']} "
            f"unresolved={len(proof_status['unresolved_theorem_ids'])} "
            f"unproved={len(proof_status['unproved_theorem_ids'])}"
        ),
        (
            "support="
            f"ready={support['ready_for_downstream_fixture_use']} "
            f"pack_fingerprint={str(support['contract_pack_fingerprint'])[:12]} "
            f"contract_fingerprint={str(support['contract_content_fingerprint'])[:12]}"
        ),
        (
            "request_fingerprints="
            f"request={str(receipt['request_content_fingerprint'])[:12]} "
            f"normalized={str(receipt['normalized_request_fingerprint'])[:12]}"
        ),
        (
            "runner_metadata="
            f"recommendations={len(receipt['recommendations'])} "
            f"validation_commands={len(receipt['validation_commands'])}"
        ),
    ]
    evidence = receipt["evidence"]
    kind = receipt["kind"]
    if kind == "rope_position_distinguishability":
        lines.append(
            "rope_exact_discrete="
            f"pass={evidence['exact_discrete_pass']} "
            f"collision_pairs={evidence['exact_total_bank_collision_pair_count']} "
            f"common_gap={evidence['exact_common_collision_gap']}"
        )
        lines.append(
            "rope_real_phase_scan="
            f"numerical_pass={evidence['real_phase_numerical_pass_margin']} "
            f"worst_gap={evidence['real_phase_numerical_worst_gap']} "
            f"worst_margin={evidence['real_phase_numerical_worst_margin_radians']}"
        )
        classifier = evidence.get("standard_channel0_d19_request_classifier")
        if isinstance(classifier, dict):
            lines.append(
                "rope_d19_request="
                f"status={classifier['request_status']} "
                f"theorem_backed={classifier['theorem_backed_classification']} "
                f"margin={classifier['requested_margin']} "
                f"context={classifier['requested_context']}"
            )
        guardrail = evidence.get("real_phase_dirichlet_guardrail")
        if isinstance(guardrail, dict):
            lines.append(
                "rope_dirichlet_guardrail="
                f"applies={guardrail['applies']} "
                f"inv_context_margin={guardrail['inv_context_margin']} "
                "requested_relation="
                f"{guardrail['requested_margin_relation_to_ceiling']} "
                f"exceeds_ceiling={guardrail['requested_margin_exceeds_ceiling']}"
            )
    elif kind == "kv_cache_ring_buffer":
        window = evidence["window_certificate"]
        adapter = evidence["adapter_request_trace_certificate"]
        live = evidence["live_window_certificate"]
        lines.append(
            "kv_cache_window="
            f"retained={window['retained']} slot={window['slot']} "
            f"lag={window['lag']} next_overwrite={window['next_overwrite_token']}"
        )
        lines.append(
            "kv_cache_request="
            f"pass={adapter['pass_certificate']} "
            f"stale_count={adapter['stale_requested_count']} "
            f"first_stale_token={adapter['first_stale_token']}"
        )
        lines.append(
            "kv_cache_live_window="
            f"full_coverage={live['full_coverage_contract']} "
            f"start={live['start']} length={live['length']}"
        )
    elif kind == "sparse_attention_coverage":
        lines.append(
            "sparse_attention="
            f"coverage_complete={evidence['coverage_complete']} "
            f"covered={evidence['covered_lag_count']} "
            f"uncovered={evidence['uncovered_lag_count']} "
            f"first_gap={evidence['first_uncovered_lag']}"
        )
        lines.append(
            "sparse_repair="
            f"complete_repair_window={evidence['complete_repair_window']} "
            f"largest_interval_repair={evidence['largest_uncovered_interval_repair_window']}"
        )
    elif kind == "recurrence_schedule":
        fields = evidence["fields"]
        lines.append(
            "recurrence_schedule="
            f"loop_period={fields['loop_period']} "
            f"sample_index={fields['sample_index']} "
            f"token_count={len(fields['tokens'])} "
            f"exit_step={fields['exit_step']}"
        )
        lines.append(
            "recurrence_work="
            f"active={fields['total_active_token_work']} "
            f"inactive={fields['total_inactive_token_work']} "
            f"saving={fields['scheduled_work_saving']}"
        )
    lines.append(f"not_claimed={'; '.join(receipt['not_claimed'])}")
    return lines


def build_contract_request_json_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://circle-calculus.local/schemas/circle_ai_contract_request.schema.json",
        "title": "Circle AI Contract Request",
        "type": "object",
        "required": ["schema_id", "kind", "parameters"],
        "properties": {
            "schema_id": {"const": REQUEST_SCHEMA_ID},
            "kind": {"enum": sorted(KIND_ALIASES)},
            "parameters": {"type": "object", "minProperties": 0},
        },
        "additionalProperties": True,
    }


def build_contract_receipt_json_schema() -> dict[str, Any]:
    string_list = {"type": "array", "items": {"type": "string"}}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://circle-calculus.local/schemas/circle_ai_contract_receipt.schema.json",
        "title": "Circle AI Contract Receipt",
        "type": "object",
        "required": [
            "schema_id",
            "request_schema_id",
            "contract_pack_schema_id",
            "kind",
            "contract_id",
            "status",
            "request_passed",
            "request",
            "request_content_fingerprint",
            "normalized_request",
            "normalized_request_fingerprint",
            "evidence",
            "proof_status",
            "proof_layers",
            "recommendations",
            "validation_commands",
            "support",
            "not_claimed",
            "content_fingerprint_algorithm",
            "receipt_content_fingerprint",
        ],
        "properties": {
            "schema_id": {"const": RECEIPT_SCHEMA_ID},
            "request_schema_id": {"const": REQUEST_SCHEMA_ID},
            "kind": {"enum": list(SUPPORTED_CONTRACT_KINDS)},
            "contract_id": {"type": "string", "minLength": 1},
            "status": {"enum": list(STATUS_VALUES)},
            "request_passed": {"type": ["boolean", "null"]},
            "request": {"type": "object"},
            "request_content_fingerprint": {
                "type": "string",
                "pattern": "^[0-9a-f]{64}$",
            },
            "normalized_request": {"type": "object"},
            "normalized_request_fingerprint": {
                "type": "string",
                "pattern": "^[0-9a-f]{64}$",
            },
            "evidence": {"type": "object"},
            "proof_status": {
                "type": "object",
                "required": [
                    "theorem_ids",
                    "theorem_count",
                    "all_theorem_ids_resolved",
                    "all_theorem_ids_proved",
                    "unresolved_theorem_ids",
                    "unproved_theorem_ids",
                ],
                "properties": {
                    "theorem_ids": string_list,
                    "theorem_count": {"type": "integer", "minimum": 0},
                    "all_theorem_ids_resolved": {"type": "boolean"},
                    "all_theorem_ids_proved": {"type": "boolean"},
                    "unresolved_theorem_ids": string_list,
                    "unproved_theorem_ids": string_list,
                },
                "additionalProperties": True,
            },
            "proof_layers": {"type": "object"},
            "recommendations": {
                "type": "array",
                "items": {"type": "object"},
                "minItems": 1,
            },
            "validation_commands": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
                "minItems": 1,
            },
            "support": {"type": "object"},
            "not_claimed": string_list,
            "content_fingerprint_algorithm": {"const": FINGERPRINT_ALGORITHM},
            "receipt_content_fingerprint": {
                "type": "string",
                "pattern": "^[0-9a-f]{64}$",
            },
        },
        "additionalProperties": True,
    }
