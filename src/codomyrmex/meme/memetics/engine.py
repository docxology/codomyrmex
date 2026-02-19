"""MemeticEngine — high-level orchestrator for memetic operations."""

from __future__ import annotations

import random
import re
from typing import Dict, List

from codomyrmex.meme.memetics.models import Meme, Memeplex, MemeType, FitnessMap
from codomyrmex.meme.memetics.mutation import semantic_drift, recombine, batch_mutate
from codomyrmex.meme.memetics.fitness import (
    virality_score,
    robustness_score,
    population_fitness_stats,
)


class MemeticEngine:
    """High-level engine for memetic analysis and synthesis.

    Provides methods to dissect text into constituent memes,
    synthesize memes into coherent text, compute fitness landscapes,
    and run evolutionary selection on meme populations.
    """

    # Sentence-boundary pattern for dissection
    _SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")

    # Heuristic type keywords
    _TYPE_KEYWORDS: Dict[MemeType, List[str]] = {
        MemeType.BELIEF: ["believe", "true", "fact", "know", "think"],
        MemeType.NORM: ["should", "must", "ought", "duty", "rule"],
        MemeType.STRATEGY: ["plan", "tactic", "approach", "method", "way"],
        MemeType.AESTHETIC: ["beautiful", "ugly", "style", "taste", "art"],
        MemeType.NARRATIVE: ["story", "tale", "once", "journey", "hero"],
        MemeType.SYMBOL: ["symbol", "flag", "icon", "sign", "logo"],
        MemeType.RITUAL: ["ritual", "ceremony", "tradition", "practice"],
        MemeType.SLOGAN: ["slogan", "motto", "catchphrase", "mantra"],
    }

    def dissect(self, text: str) -> List[Meme]:
        """Decompose text into constituent atomic memes.

        Splits on sentence boundaries and classifies each sentence
        by memetic type using keyword heuristics.

        Args:
            text: Input text to dissect.

        Returns:
            List of Meme objects, one per detected meme unit.
        """
        sentences = self._SENTENCE_RE.split(text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]

        memes: List[Meme] = []
        for sentence in sentences:
            meme_type = self._classify_type(sentence)
            word_count = len(sentence.split())
            # Shorter memes have higher fecundity
            fecundity = min(1.0, 1.0 / (1.0 + word_count / 20.0))
            memes.append(
                Meme(
                    content=sentence,
                    meme_type=meme_type,
                    fecundity=fecundity,
                    fidelity=0.8,
                    longevity=0.5,
                )
            )
        return memes

    def _classify_type(self, text: str) -> MemeType:
        """Classify a text fragment into a MemeType via keyword matching."""
        text_lower = text.lower()
        scores: Dict[MemeType, int] = {}
        for mtype, keywords in self._TYPE_KEYWORDS.items():
            scores[mtype] = sum(1 for kw in keywords if kw in text_lower)
        
        # Check if max score > 0
        if not scores:
            return MemeType.BELIEF
            
        best = max(scores, key=lambda k: scores[k])
        if scores[best] == 0:
            return MemeType.BELIEF  # Default
        return best

    def synthesize(self, memes: List[Meme], separator: str = " ") -> str:
        """Combine a list of memes into coherent text.

        Args:
            memes: Memes to synthesize.
            separator: How to join meme contents.

        Returns:
            Combined text string.
        """
        return separator.join(m.content for m in memes)

    def fitness_landscape(self, population: List[Memeplex]) -> FitnessMap:
        """Compute the fitness landscape of a memeplex population.

        Args:
            population: List of memeplexes to evaluate.

        Returns:
            FitnessMap mapping each memeplex ID to its fitness.
        """
        fmap = FitnessMap()
        for mplex in population:
            fmap.add(mplex.id, mplex.fitness)
        return fmap

    def select(
        self, population: List[Memeplex], n: int = 10, method: str = "tournament"
    ) -> List[Memeplex]:
        """Select the fittest memeplexes from a population.

        Args:
            population: Source population.
            n: Number to select.
            method: Selection method ('tournament' or 'truncation').

        Returns:
            Selected memeplexes.
        """
        if not population:
            return []
            
        if method == "truncation":
            ranked = sorted(population, key=lambda m: m.fitness, reverse=True)
            return ranked[:n]

        # Tournament selection
        selected: List[Memeplex] = []
        for _ in range(n):
            tournament_size = min(3, len(population))
            contestants = random.sample(population, tournament_size)
            winner = max(contestants, key=lambda m: m.fitness)
            selected.append(winner)
            
        return selected

    def evolve(
        self, population: List[Memeplex], generations: int = 10, mutation_rate: float = 0.1
    ) -> List[Memeplex]:
        """Run evolutionary selection on a memeplex population."""
        current_pop = list(population)
        
        for _ in range(generations):
            # Select parents
            parents = self.select(current_pop, n=max(2, len(current_pop) // 2))
            
            # Recombine and mutate to form next generation
            offspring = []
            while len(offspring) < len(current_pop) - len(parents):
                if len(parents) < 2:
                    break
                p1, p2 = random.sample(parents, 2)
                # Simple cloning — upgrade to crossover recombination when memeplex algebra is implemented
                child = p1
                offspring.append(child)
            
            current_pop = parents + offspring
            
        return current_pop
