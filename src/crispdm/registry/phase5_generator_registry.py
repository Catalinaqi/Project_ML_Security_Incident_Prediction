# src/crispdm/registry/generators/phase5_generator_registry.py
"""
=============================================================================
Registry dei generatori degli artefatti per la Fase 5 (Evaluation & Interpretation)
=============================================================================
Crea e salva tutti gli output relativi all'interpretazione dei cluster,
alla valutazione business, all'audit di riproducibilità e alle decisioni finali.

Ogni funzione è decorata con `@register_artifact(step, artifact_key)` in
modo che il motore del pipeline possa invocarla automaticamente quando
deve produrre quell'artefatto.

Convenzioni:
- ctx : RunContext — contesto di esecuzione (contiene i percorsi delle directory)
- path : str — nome relativo del file (rispetto alla directory di fase)
- **data : dict — dizionario arbitrario passato dal chiamante
=============================================================================
"""

from __future__ import annotations

from crispdm.common.context_facade_common import RunContext
from crispdm.common.logging_adapter_common import get_logger
from crispdm.configuration.enum_registry_config import StepsPhase, StepOutputArtifact
from crispdm.data.persist_persister_data import save_json, save_parquet, save_pickle
from crispdm.registry.generator_registry_registry import register_artifact
import matplotlib.pyplot as plt

log = get_logger(__name__)

# =============================================================================
# Phase 5 — Generatori degli artefatti di valutazione e interpretazione
# Steps: 5.1 Interpretation, 5.2 Business Evaluation,
#        5.3 Process Audit, 5.4 Decision Making
# =============================================================================

# -----------------------------------------------------------------------------
# Step 5.1 — Interpretation (profili dei cluster, regole di minaccia)
# -----------------------------------------------------------------------------

@register_artifact(StepsPhase.STEP_5_1.value, StepOutputArtifact.THREAT_KNOWLEDGE_BASE)
def _write_threat_knowledge_base(ctx: RunContext, path: str, **data) -> None:
    """Salva la knowledge base delle minacce: regole di interpretazione per cluster.

    Contiene le descrizioni qualitative dei cluster (es. ‘FalsePositive cluster’,
    ‘TruePositive cluster’) e le feature più discriminanti.
    """
    kb = data.get("threat_knowledge_base")
    if kb is not None:
        save_json(kb, ctx.phase5_dir / path)
        log.info("[5.1] knowledge base minacce → %s", path)
    else:
        log.warning("[5.1] threat_knowledge_base non disponibile")

# -----------------------------------------------------------------------------
# Step 5.2 — Business Evaluation (matrici di confusione, grafici di allineamento)
# -----------------------------------------------------------------------------

@register_artifact(StepsPhase.STEP_5_2.value, StepOutputArtifact.CONFUSION_MATRICES)
def _write_confusion_matrices(ctx: RunContext, path: str, **data) -> None:
    """Salva le matrici di confusione (cluster vs IncidentGrade) per ogni variante."""
    matrices = data.get("confusion_matrices")
    if matrices is not None:
        save_json(matrices, ctx.phase5_dir / path)
        log.info("[5.2] matrici di confusione → %s", path)
    else:
        log.warning("[5.2] confusion_matrices non disponibile")

# @register_artifact(StepsPhase.STEP_5_2.value, StepOutputArtifact.ALIGNMENT_PLOT)
# def _write_alignment_plot(ctx: RunContext, path: str, **data) -> None:
#     """Salva il grafico di allineamento cluster vs target (stacked bar)."""
#     fig = data.get("alignment_plot")  # potrebbe essere un oggetto matplotlib Figure
#     if fig is not None:
#         # Esempio di salvataggio come PNG (nel caso sia un oggetto Figure)
#         try:
#             # Se `fig` è una figura matplotlib, salviamola direttamente
#             fig.savefig(ctx.phase5_dir / path, dpi=300, bbox_inches="tight")
#             log.info("[5.2] grafico allineamento → %s", path)
#         except Exception:
#             # Fallback: salva come JSON dei dati grezzi
#             save_json(fig, ctx.phase5_dir / path)
#             log.info("[5.2] dati grezzi allineamento salvati come JSON → %s", path)
#     else:
#         log.warning("[5.2] alignment_plot non disponibile")

@register_artifact(StepsPhase.STEP_5_2.value, StepOutputArtifact.ALIGNMENT_PLOT)
def _write_alignment_plot(ctx: RunContext, path: str, **data) -> None:
    """Salva il grafico di allineamento cluster vs target (stacked bar)."""
    fig = ctx.artifacts.get("alignment_plot")  # Legge dal contesto
    if fig is not None:
        try:
            fig.savefig(ctx.phase5_dir / path, dpi=300, bbox_inches="tight")
            log.info("[5.2] grafico allineamento → %s", path)
        except Exception as e:
            log.error("[5.2] errore salvataggio grafico allineamento: %s", e)
        finally:
            plt.close(fig)  # Chiudi la figura dopo il salvataggio
    else:
        log.warning("[5.2] alignment_plot non disponibile in ctx.artifacts")

# -----------------------------------------------------------------------------
# Step 5.3 — Process Audit (riproducibilità, leakage)
# -----------------------------------------------------------------------------

@register_artifact(StepsPhase.STEP_5_3.value, StepOutputArtifact.REPRODUCIBILITY_CERTIFICATE)
def _write_reproducibility_certificate(ctx: RunContext, path: str, **data) -> None:
    """Salva il certificato di riproducibilità: seed validation e sanity check."""
    cert = data.get("reproducibility_certificate")
    if cert is not None:
        save_json(cert, ctx.phase5_dir / path)
        log.info("[5.3] certificato riproducibilità → %s", path)
    else:
        log.warning("[5.3] reproducibility_certificate non disponibile")

# -----------------------------------------------------------------------------
# Step 5.4 — Decision Making (deployment readiness e raccomandazioni)
# -----------------------------------------------------------------------------

@register_artifact(StepsPhase.STEP_5_4.value, StepOutputArtifact.DEPLOYMENT_READINESS)
def _write_deployment_readiness(ctx: RunContext, path: str, **data) -> None:
    """Salva le metriche di readiness per il deployment."""
    readiness = data.get("deployment_readiness")
    if readiness is not None:
        save_json(readiness, ctx.phase5_dir / path)
        log.info("[5.4] prontezza deployment → %s", path)
    else:
        log.warning("[5.4] deployment_readiness non disponibile")


@register_artifact(StepsPhase.STEP_5_4.value, StepOutputArtifact.RECOMMENDATIONS)
def _write_recommendations(ctx: RunContext, path: str, **data) -> None:
    """Salva le raccomandazioni finali (monitoring, miglioramenti, prossimi passi)."""
    recs = data.get("recommendations")
    if recs is not None:
        save_json(recs, ctx.phase5_dir / path)
        log.info("[5.4] raccomandazioni → %s", path)
    else:
        log.warning("[5.4] recommendations non disponibile")