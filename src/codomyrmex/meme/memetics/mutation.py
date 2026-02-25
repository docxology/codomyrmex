"""Mutation operators for memes and memeplexes."""

from __future__ import annotations

import random

from codomyrmex.meme.memetics.models import Meme


def semantic_drift(meme: Meme, intensity: float = 0.1) -> Meme:
    """Apply semantic drift to a meme's content.

    Simulates gradual meaning shift via token-level perturbation markers.
    Real semantic drift would use an LLM; this provides the structural
    framework with deterministic perturbation.

    Args:
        meme: Source meme.
        intensity: Drift magnitude (0–1). Controls fidelity degradation.

    Returns:
        New Meme with drifted content and reduced fidelity.
    """
    words = meme.content.split()
    if not words:
        return meme.descend(meme.content)

    n_drift = max(1, int(len(words) * intensity))
    indices = random.sample(range(len(words)), min(n_drift, len(words)))
    drifted = list(words)
    for i in indices:
        drifted[i] = f"~{drifted[i]}~"

    return meme.descend(
        new_content=" ".join(drifted),
        fidelity=max(0.0, meme.fidelity - intensity * 0.3),
    )


def recombine(meme_a: Meme, meme_b: Meme, crossover_point: float | None = None) -> Meme:
    """Recombine two memes via content crossover.

    Splits each meme's content and joins halves to produce
    an offspring meme with blended properties.

    Args:
        meme_a: First parent meme.
        meme_b: Second parent meme.
        crossover_point: Fraction (0–1) at which to split. Default: random.

    Returns:
        New Meme with recombined content and averaged properties.
    """
    if crossover_point is None:
        crossover_point = random.random()
    crossover_point = max(0.0, min(1.0, crossover_point))

    words_a = meme_a.content.split()
    words_b = meme_b.content.split()
    cut_a = int(len(words_a) * crossover_point)
    cut_b = int(len(words_b) * (1 - crossover_point))

    child_words = words_a[:cut_a] + words_b[cut_b:]
    child_content = " ".join(child_words) if child_words else meme_a.content

    return Meme(
        content=child_content,
        meme_type=random.choice([meme_a.meme_type, meme_b.meme_type]),
        fidelity=(meme_a.fidelity + meme_b.fidelity) / 2,
        fecundity=(meme_a.fecundity + meme_b.fecundity) / 2,
        longevity=(meme_a.longevity + meme_b.longevity) / 2,
        lineage=list(set(meme_a.lineage + [meme_a.id] + meme_b.lineage + [meme_b.id])),
    )


def splice(host: Meme, insert: Meme, position: float | None = None) -> Meme:
    """Splice one meme's content into another at a given position.

    Analogous to horizontal gene transfer — inject foreign memetic
    material into a host meme.

    Args:
        host: The host meme receiving foreign material.
        insert: The meme whose content is being injected.
        position: Fractional insertion point (0–1). Default: midpoint.

    Returns:
        New Meme with spliced content.
    """
    if position is None:
        position = 0.5

    host_words = host.content.split()
    insert_pos = int(len(host_words) * position)
    spliced = host_words[:insert_pos] + [f"[{insert.content}]"] + host_words[insert_pos:]

    return host.descend(
        new_content=" ".join(spliced),
        fidelity=max(0.0, host.fidelity - 0.1),
        fecundity=min(1.0, (host.fecundity + insert.fecundity) / 2),
    )


def batch_mutate(
    population: list[Meme], mutation_rate: float = 0.1, intensity: float = 0.1
) -> list[Meme]:
    """Apply mutations to a population of memes.

    Each meme has a `mutation_rate` probability of being drifted
    with the given `intensity`.

    Args:
        population: List of memes to mutate.
        mutation_rate: Probability each meme is mutated (0–1).
        intensity: Drift intensity passed to `semantic_drift`.

    Returns:
        New population list (unmutated memes are referenced, not copied).
    """
    result = []
    for meme in population:
        if random.random() < mutation_rate:
            result.append(semantic_drift(meme, intensity))
        else:
            result.append(meme)
    return result
