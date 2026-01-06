"""Bayesian inference engine for probabilistic reasoning."""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np

from codomyrmex.cerebrum.exceptions import InferenceError, NetworkStructureError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class Distribution:
    """Represents a probability distribution."""

    values: list[Any]
    probabilities: list[float]

    def __post_init__(self):
        """Normalize probabilities."""
        total = sum(self.probabilities)
        if total > 0:
            self.probabilities = [p / total for p in self.probabilities]

    def sample(self, n: int = 1) -> list[Any]:
        """Sample from the distribution.

        Args:
            n: Number of samples

        Returns:
            List of samples
        """
        return np.random.choice(self.values, size=n, p=self.probabilities).tolist()

    def expectation(self) -> float:
        """Compute expectation if values are numeric."""
        if not all(isinstance(v, (int, float)) for v in self.values):
            raise ValueError("Cannot compute expectation for non-numeric values")
        return sum(v * p for v, p in zip(self.values, self.probabilities))

    def mode(self) -> Any:
        """Get the most probable value."""
        max_idx = np.argmax(self.probabilities)
        return self.values[max_idx]


class BayesianNetwork:
    """Represents a Bayesian network (probabilistic graphical model)."""

    def __init__(self, name: str = "bayesian_network"):
        """Initialize Bayesian network.

        Args:
            name: Network name
        """
        self.name = name
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: dict[str, list[str]] = defaultdict(list)
        self.parents: dict[str, list[str]] = defaultdict(list)
        self.cpt: dict[str, dict[tuple, Distribution]] = {}  # Conditional probability tables
        self.logger = get_logger(__name__)

    def add_node(self, node: str, values: list[Any], prior: Optional[list[float]] = None) -> None:
        """Add a node to the network.

        Args:
            node: Node name
            values: Possible values for the node
            prior: Prior probabilities (uniform if None)
        """
        if node in self.nodes:
            raise NetworkStructureError(f"Node {node} already exists")

        if prior is None:
            prior = [1.0 / len(values)] * len(values)

        if len(prior) != len(values):
            raise NetworkStructureError("Prior probabilities must match number of values")

        self.nodes[node] = {"values": values, "prior": prior}
        self.edges[node] = []
        self.cpt[node] = {}

        # Create default CPT entry (no parents)
        self.cpt[node][()] = Distribution(values, prior.copy())

        self.logger.debug(f"Added node {node}")

    def add_edge(self, parent: str, child: str) -> None:
        """Add a directed edge from parent to child.

        Args:
            parent: Parent node name
            child: Child node name
        """
        if parent not in self.nodes:
            raise NetworkStructureError(f"Parent node {parent} does not exist")
        if child not in self.nodes:
            raise NetworkStructureError(f"Child node {child} does not exist")

        if child in self.edges[parent]:
            raise NetworkStructureError(f"Edge from {parent} to {child} already exists")

        self.edges[parent].append(child)
        self.parents[child].append(parent)
        self.logger.debug(f"Added edge {parent} -> {child}")

    def set_cpt(
        self, node: str, cpt: dict[tuple, dict[Any, float]]
    ) -> None:
        """Set conditional probability table for a node.

        Args:
            node: Node name
            cpt: Conditional probability table mapping parent value tuples to value probabilities
        """
        if node not in self.nodes:
            raise NetworkStructureError(f"Node {node} does not exist")

        node_values = self.nodes[node]["values"]
        parent_nodes = self.parents[node]

        # Convert CPT to Distribution objects
        distributions = {}
        for parent_config, value_probs in cpt.items():
            if len(parent_config) != len(parent_nodes):
                raise NetworkStructureError(
                    f"CPT parent configuration length mismatch for {node}"
                )

            # Ensure all values are covered
            probs = [value_probs.get(v, 0.0) for v in node_values]
            distributions[parent_config] = Distribution(node_values, probs)

        self.cpt[node] = distributions
        self.logger.debug(f"Set CPT for node {node}")

    def get_topological_order(self) -> list[str]:
        """Get nodes in topological order (parents before children).

        Returns:
            List of node names in topological order
        """
        visited = set()
        order = []

        def visit(node: str):
            if node in visited:
                return
            visited.add(node)
            for parent in self.parents[node]:
                visit(parent)
            order.append(node)

        for node in self.nodes:
            visit(node)

        return order

    def to_dict(self) -> dict[str, Any]:
        """Convert network to dictionary."""
        return {
            "name": self.name,
            "nodes": self.nodes,
            "edges": {k: v for k, v in self.edges.items()},
            "parents": {k: v for k, v in self.parents.items()},
            # CPT serialization would need custom handling
        }


class InferenceEngine:
    """Performs probabilistic inference on Bayesian networks."""

    def __init__(self, network: BayesianNetwork, method: str = "variable_elimination"):
        """Initialize inference engine.

        Args:
            network: Bayesian network
            method: Inference method ("variable_elimination", "mcmc", "belief_propagation")
        """
        self.network = network
        self.method = method
        self.logger = get_logger(__name__)

    def infer(
        self, query: dict[str, Any], evidence: Optional[dict[str, Any]] = None
    ) -> dict[str, Distribution]:
        """Perform inference to compute posterior distributions.

        Args:
            query: Variables to query (dict of variable -> None or desired value)
            evidence: Observed evidence (dict of variable -> value)

        Returns:
            Dictionary of variable -> posterior distribution
        """
        evidence = evidence or {}

        if self.method == "variable_elimination":
            return self._variable_elimination(query, evidence)
        elif self.method == "mcmc":
            return self._mcmc_inference(query, evidence)
        else:
            raise InferenceError(f"Unknown inference method: {self.method}")

    def _variable_elimination(
        self, query: dict[str, Any], evidence: dict[str, Any]
    ) -> dict[str, Distribution]:
        """Simple variable elimination (exact inference for small networks).

        Args:
            query: Variables to query
            evidence: Observed evidence

        Returns:
            Posterior distributions
        """
        # For small networks, use brute force enumeration
        # In practice, this would use proper variable elimination algorithm
        results = {}

        for var in query:
            if var not in self.network.nodes:
                raise InferenceError(f"Query variable {var} not in network")

            # Get all possible values
            values = self.network.nodes[var]["values"]
            probabilities = []

            # Compute marginal by summing over all configurations
            for value in values:
                prob = self._compute_joint_probability({**evidence, var: value})
                probabilities.append(prob)

            # Normalize
            total = sum(probabilities)
            if total > 0:
                probabilities = [p / total for p in probabilities]
            else:
                probabilities = [1.0 / len(values)] * len(values)

            results[var] = Distribution(values, probabilities)

        return results

    def _compute_joint_probability(self, assignment: dict[str, Any]) -> float:
        """Compute joint probability of a complete assignment.

        Args:
            assignment: Complete variable assignment

        Returns:
            Joint probability
        """
        prob = 1.0
        topo_order = self.network.get_topological_order()

        for node in topo_order:
            if node not in assignment:
                continue

            node_value = assignment[node]
            parents = self.network.parents[node]

            if not parents:
                # Root node - use prior
                prior = self.network.nodes[node]["prior"]
                values = self.network.nodes[node]["values"]
                idx = values.index(node_value) if node_value in values else 0
                prob *= prior[idx]
            else:
                # Get parent configuration
                parent_config = tuple(assignment[p] for p in parents)
                cpt = self.network.cpt.get(node, {})
                dist = cpt.get(parent_config)

                if dist is None:
                    # Use uniform if CPT entry missing
                    values = self.network.nodes[node]["values"]
                    prob *= 1.0 / len(values)
                else:
                    # Get probability for node value
                    values = dist.values
                    if node_value in values:
                        idx = values.index(node_value)
                        prob *= dist.probabilities[idx]
                    else:
                        prob *= 0.0

        return prob

    def _mcmc_inference(
        self, query: dict[str, Any], evidence: dict[str, Any], n_samples: int = 10000
    ) -> dict[str, Distribution]:
        """MCMC-based approximate inference.

        Args:
            query: Variables to query
            evidence: Observed evidence
            n_samples: Number of MCMC samples

        Returns:
            Posterior distributions
        """
        # Simplified MCMC - in practice would use proper Gibbs sampling or Metropolis-Hastings
        results = {}

        for var in query:
            if var not in self.network.nodes:
                raise InferenceError(f"Query variable {var} not in network")

            values = self.network.nodes[var]["values"]
            counts = defaultdict(int)

            # Sample from posterior
            for _ in range(n_samples):
                sample = self._gibbs_sample(evidence, var)
                if var in sample:
                    counts[sample[var]] += 1

            # Convert counts to probabilities
            total = sum(counts.values())
            if total == 0:
                probabilities = [1.0 / len(values)] * len(values)
            else:
                probabilities = [counts.get(v, 0) / total for v in values]

            results[var] = Distribution(values, probabilities)

        return results

    def _gibbs_sample(self, evidence: dict[str, Any], query_var: str) -> dict[str, Any]:
        """Perform one Gibbs sampling step.

        Args:
            evidence: Fixed evidence
            query_var: Variable to sample

        Returns:
            Sample assignment
        """
        assignment = evidence.copy()

        # Initialize unobserved variables
        for node in self.network.nodes:
            if node not in assignment:
                values = self.network.nodes[node]["values"]
                assignment[node] = np.random.choice(values)

        # Sample query variable given its Markov blanket
        values = self.network.nodes[query_var]["values"]
        probs = []

        for value in values:
            assignment[query_var] = value
            prob = self._compute_joint_probability(assignment)
            probs.append(prob)

        # Normalize and sample
        total = sum(probs)
        if total > 0:
            probs = [p / total for p in probs]
        else:
            probs = [1.0 / len(values)] * len(values)

        assignment[query_var] = np.random.choice(values, p=probs)
        return assignment

    def compute_marginal(self, variable: str, evidence: Optional[dict[str, Any]] = None) -> Distribution:
        """Compute marginal distribution of a variable.

        Args:
            variable: Variable name
            evidence: Optional evidence

        Returns:
            Marginal distribution
        """
        results = self.infer({variable: None}, evidence)
        return results[variable]

    def update_beliefs(self, evidence: dict[str, Any]) -> dict[str, Distribution]:
        """Update beliefs given new evidence.

        Args:
            evidence: New evidence

        Returns:
            Updated beliefs for all variables
        """
        # Query all variables
        query = {var: None for var in self.network.nodes if var not in evidence}
        return self.infer(query, evidence)


class PriorBuilder:
    """Constructs prior distributions from cases."""

    def __init__(self):
        """Initialize prior builder."""
        self.logger = get_logger(__name__)

    def build_prior_from_cases(
        self, cases: list[Any], variable: str, feature_extractor: callable
    ) -> Distribution:
        """Build prior distribution from case outcomes.

        Args:
            cases: List of cases
            variable: Variable name
            feature_extractor: Function to extract variable value from case

        Returns:
            Prior distribution
        """
        values = []
        for case in cases:
            value = feature_extractor(case)
            if value is not None:
                values.append(value)

        if not values:
            return Distribution([], [])

        # Count frequencies
        value_counts = defaultdict(int)
        for value in values:
            value_counts[value] += 1

        unique_values = list(value_counts.keys())
        counts = [value_counts[v] for v in unique_values]
        total = sum(counts)
        probabilities = [c / total for c in counts]

        return Distribution(unique_values, probabilities)

