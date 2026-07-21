# src/crispdm/registry/generators/phase4_generator_registry.py
"""
=============================================================================
Registry dei generatori degli artefatti per la Fase 4 (Modelling)
=============================================================================
Crea e salva tutti gli output delle fasi 4.1 ÷ 4.5 del pipeline di clustering.

Ogni funzione è decorata con `@register_artifact(step, artifact_key)` in
modo che il motore del pipeline possa invocarla automaticamente quando
deve produrre quell'artefatto.

Convenzioni:
- ctx : RunContext — contesto di esecuzione (contiene i percorsi delle directory)
- path : str — nome relativo del file (rispetto alla directory di fase)
- **data : dict — dizionario arbitrario passato dal chiamante (es. modelli,
  metriche, DataFrames)
=============================================================================
"""

from __future__ import annotations

from crispdm.common.context_facade_common import RunContext
from crispdm.common.logging_adapter_common import get_logger
from crispdm.configuration.enum_registry_config import StepsPhase, StepOutputArtifact
from crispdm.data.persist_persister_data import save_json, save_parquet, save_pickle
from crispdm.registry.generator_registry_registry import register_artifact

log = get_logger(__name__)

# =============================================================================
# Fase 4 — Generatori degli artefatti di modelling
# Steps: 4.1 Algorithm Selection, 4.2 Pretrain Analysis,
#        4.3 Model Training, 4.4 Test Design, 4.5 Model Evaluation
# =============================================================================

# -----------------------------------------------------------------------------
# Step 4.1 — Algorithm Selection
# -----------------------------------------------------------------------------

@register_artifact(StepsPhase.STEP_4_1.value, StepOutputArtifact.ALGORITHMS_SELECTED)
def _write_algorithms_selected(ctx: RunContext, path: str, **data) -> None:
    """Salva il riepilogo degli algoritmi selezionati (KMeans, DBSCAN, ecc.)."""
    report = data.get("algorithm_selection_report")
    if report is not None:
        save_json(report, ctx.phase4_dir / path)
        log.info("[4.1] algoritmi selezionati → %s", path)
    else:
        log.warning("[4.1] nessun report di selezione disponibile")

# -----------------------------------------------------------------------------
# Step 4.2 — Pretrain Analysis (k‑NN distance analysis per DBSCAN)
# -----------------------------------------------------------------------------

@register_artifact(StepsPhase.STEP_4_2.value, StepOutputArtifact.EPS_RECOMMENDATION)
def _write_eps_recommendation(ctx: RunContext, path: str, **data) -> None:
    """Salva il valore di eps suggerito in base all'analisi k‑NN."""
    eps = data.get("eps_recommendation")
    if eps is not None:
        save_json(eps, ctx.phase4_dir / path)
        log.info("[4.2] eps raccomandato → %s", path)
    else:
        log.warning("[4.2] eps_recommendation non disponibile")

@register_artifact(StepsPhase.STEP_4_2.value, StepOutputArtifact.KNN_DISTANCE_SUMMARY)
def _write_knn_distance_summary(ctx: RunContext, path: str, **data) -> None:
    """Salva le statistiche descrittive delle distanze k‑NN."""
    stats = data.get("knn_distance_summary")
    if stats is not None:
        save_json(stats, ctx.phase4_dir / path)
        log.info("[4.2] summary distanze k‑NN → %s", path)
    else:
        log.warning("[4.2] knn_distance_summary non disponibile")

@register_artifact(StepsPhase.STEP_4_2.value, StepOutputArtifact.SAMPLE_METADATA)
def _write_sample_metadata(ctx: RunContext, path: str, **data) -> None:
    """Salva i metadati del campione usato per l'analisi k‑NN."""
    meta = data.get("sample_metadata")
    if meta is not None:
        save_json(meta, ctx.phase4_dir / path)
        log.info("[4.2] metadati campione → %s", path)
    else:
        log.warning("[4.2] sample_metadata non disponibile")

@register_artifact(StepsPhase.STEP_4_2.value, StepOutputArtifact.EPS_VALIDATION_PREVIEW)
def _write_eps_validation_preview(ctx: RunContext, path: str, **data) -> None:
    """Salva un'anteprima della validazione di eps (es. grafico elbow)."""
    preview = data.get("eps_validation_preview")
    if preview is not None:
        save_json(preview, ctx.phase4_dir / path)
        log.info("[4.2] anteprima validazione eps → %s", path)
    else:
        log.warning("[4.2] eps_validation_preview non disponibile")

# -----------------------------------------------------------------------------
# Step 4.3 — Model Training
# -----------------------------------------------------------------------------

@register_artifact(StepsPhase.STEP_4_3.value, StepOutputArtifact.BEST_MODEL)
def _write_best_model(ctx: RunContext, path: str, **data) -> None:
    """Serializza il miglior modello (pipeline completa) in pickle."""
    model = data.get("best_model")
    if model is not None:
        save_pickle(model, ctx.phase4_dir / path)
        log.info("[4.3] miglior modello salvato → %s", path)
    else:
        log.warning("[4.3] best_model non disponibile")

@register_artifact(StepsPhase.STEP_4_3.value, StepOutputArtifact.MODEL_CARD)
def _write_model_card(ctx: RunContext, path: str, **data) -> None:
    """Salva la scheda del modello (iperparametri, versione, metriche)."""
    card = data.get("model_card")
    if card is not None:
        save_json(card, ctx.phase4_dir / path)
        log.info("[4.3] scheda modello → %s", path)
    else:
        log.warning("[4.3] model_card non disponibile")

@register_artifact(StepsPhase.STEP_4_3.value, StepOutputArtifact.VALIDATION_METRICS)
def _write_validation_metrics(ctx: RunContext, path: str, **data) -> None:
    """Salva le metriche di validazione (silhouette, Davies‑Bouldin, ecc.)."""
    metrics = data.get("validation_metrics")
    if metrics is not None:
        save_json(metrics, ctx.phase4_dir / path)
        log.info("[4.3] metriche validazione → %s", path)
    else:
        log.warning("[4.3] validation_metrics non disponibile")

@register_artifact(StepsPhase.STEP_4_3.value, StepOutputArtifact.CLUSTER_ASSIGNMENTS_SAMPLE)
def _write_cluster_assignments_sample(ctx: RunContext, path: str, **data) -> None:
    """Salva un campione delle assegnazioni ai cluster (etichhette + eventuali features)."""
    df = data.get("cluster_assignments")
    if df is not None:
        save_parquet(df, ctx.phase4_dir / path, compression="snappy")
        log.info("[4.3] assegnazioni campione → %s", path)
    else:
        log.warning("[4.3] cluster_assignments non disponibile")

@register_artifact(StepsPhase.STEP_4_3.value, StepOutputArtifact.CLUSTER_CENTROIDS)
def _write_cluster_centroids(ctx: RunContext, path: str, **data) -> None:
    """Salva i centroidi dei cluster (solo per KMeans)."""
    centroids = data.get("centroids")
    if centroids is not None:
        save_parquet(centroids, ctx.phase4_dir / path, compression="snappy")
        log.info("[4.3] centroidi cluster → %s", path)
    else:
        log.warning("[4.3] centroids non disponibile (modello non KMeans)")

@register_artifact(StepsPhase.STEP_4_3.value, StepOutputArtifact.CLUSTER_SIZES)
def _write_cluster_sizes(ctx: RunContext, path: str, **data) -> None:
    """Salva il conteggio di elementi per ogni cluster."""
    sizes = data.get("cluster_sizes")
    if sizes is not None:
        save_json(sizes, ctx.phase4_dir / path)
        log.info("[4.3] dimensioni cluster → %s", path)
    else:
        log.warning("[4.3] cluster_sizes non disponibile")

@register_artifact(StepsPhase.STEP_4_3.value, StepOutputArtifact.HP_SEARCH_SUMMARY)
def _write_hp_search_summary(ctx: RunContext, path: str, **data) -> None:
    """Salva il riepilogo della ricerca iperparametrica (grid/random)."""
    hp = data.get("hp_search_summary")
    if hp is not None:
        save_json(hp, ctx.phase4_dir / path)
        log.info("[4.3] ricerca iperparametri → %s", path)
    else:
        log.warning("[4.3] hp_search_summary non disponibile")

@register_artifact(StepsPhase.STEP_4_3.value, StepOutputArtifact.CLUSTER_FEATURE_PROFILES)
def _write_cluster_feature_profiles(ctx: RunContext, path: str, **data) -> None:
    """Salva i profili delle feature per cluster (medie, deviazioni, ecc.)."""
    profiles = data.get("cluster_feature_profiles")
    if profiles is not None:
        save_json(profiles, ctx.phase4_dir / path)
        log.info("[4.3] profili feature cluster → %s", path)
    else:
        log.warning("[4.3] cluster_feature_profiles non disponibile")

# -----------------------------------------------------------------------------
# Step 4.4 — Test Design Generation
# -----------------------------------------------------------------------------

@register_artifact(StepsPhase.STEP_4_4.value, StepOutputArtifact.EVALUATION_PLAN)
def _write_evaluation_plan(ctx: RunContext, path: str, **data) -> None:
    """Salva il piano di valutazione (metriche, modello/i da testare, strategia)."""
    plan = data.get("evaluation_plan")
    if plan is not None:
        save_json(plan, ctx.phase4_dir / path)
        log.info("[4.4] piano valutazione → %s", path)
    else:
        log.warning("[4.4] evaluation_plan non disponibile")

# -----------------------------------------------------------------------------
# Step 4.5 — Model Evaluation
# -----------------------------------------------------------------------------

@register_artifact(StepsPhase.STEP_4_5.value, StepOutputArtifact.CLUSTER_LABELS)
def _write_cluster_labels(ctx: RunContext, path: str, **data) -> None:
    """Salva le etichette dei cluster (array 1D) — input critico per la Fase 5."""
    labels = data.get("cluster_labels")
    if labels is not None:
        save_parquet(labels, ctx.phase4_dir / path, compression="snappy")
        log.info("[4.5] etichette cluster → %s", path)
    else:
        log.warning("[4.5] cluster_labels non disponibile")

@register_artifact(StepsPhase.STEP_4_5.value, StepOutputArtifact.SUMMARY_COMPARISON)
def _write_summary_comparison(ctx: RunContext, path: str, **data) -> None:
    """Salva il confronto riassuntivo tra varianti di modello (n2 vs n3)."""
    comparison = data.get("summary_comparison")
    if comparison is not None:
        save_json(comparison, ctx.phase4_dir / path)
        log.info("[4.5] confronto riassuntivo → %s", path)
    else:
        log.warning("[4.5] summary_comparison non disponibile")

@register_artifact(StepsPhase.STEP_4_5.value, StepOutputArtifact.CONSOLIDATED_ARI)
def _write_consolidated_ari(ctx: RunContext, path: str, **data) -> None:
    """Salva l'Adjusted Rand Index consolidato per tutte le varianti."""
    ari = data.get("consolidated_ari")
    if ari is not None:
        save_json(ari, ctx.phase4_dir / path)
        log.info("[4.5] ARI consolidato → %s", path)
    else:
        log.warning("[4.5] consolidated_ari non disponibile")

@register_artifact(StepsPhase.STEP_4_5.value, StepOutputArtifact.CONSOLIDATED_PROFILING)
def _write_consolidated_profiling(ctx: RunContext, path: str, **data) -> None:
    """Salva il profiling consolidato dei cluster per tutte le varianti."""
    profiling = data.get("consolidated_profiling")
    if profiling is not None:
        save_json(profiling, ctx.phase4_dir / path)
        log.info("[4.5] profiling consolidato → %s", path)
    else:
        log.warning("[4.5] consolidated_profiling non disponibile")

@register_artifact(StepsPhase.STEP_4_5.value, StepOutputArtifact.CLUSTER_SUBSETS_N2)
def _write_cluster_subsets_n2(ctx: RunContext, path: str, **data) -> None:
    """Salva i subset per cluster del modello kmeans_n2 (1000 righe/cluster)."""
    df = data.get("cluster_subsets_n2")
    if df is not None:
        save_parquet(df, ctx.phase4_dir / path, compression="snappy")
        log.info("[4.5] subset cluster n2 → %s", path)
    else:
        log.warning("[4.5] cluster_subsets_n2 non disponibile")

@register_artifact(StepsPhase.STEP_4_5.value, StepOutputArtifact.CLUSTER_SUBSETS_N3)
def _write_cluster_subsets_n3(ctx: RunContext, path: str, **data) -> None:
    """Salva i subset per cluster del modello kmeans_n3 (1000 righe/cluster)."""
    df = data.get("cluster_subsets_n3")
    if df is not None:
        save_parquet(df, ctx.phase4_dir / path, compression="snappy")
        log.info("[4.5] subset cluster n3 → %s", path)
    else:
        log.warning("[4.5] cluster_subsets_n3 non disponibile")