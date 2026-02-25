"""Epidemic models adapted for information spread."""

from __future__ import annotations

from codomyrmex.meme.contagion.models import PropagationTrace


class SIRModel:
    """Susceptible-Infected-Recovered model for meme spread.

    Nodes move from Susceptible -> Infected (adopt meme) -> Recovered (bored/immune).
    Recovered nodes generally do not re-adopt the meme.
    """

    def __init__(
        self, population_size: int = 1000, beta: float = 0.3, gamma: float = 0.1
    ) -> None:
        """
        Args:
            population_size: Total nodes (N).
            beta: Infection rate per contact.
            gamma: Recovery rate per step.
        """
        self.N = population_size
        self.beta = beta
        self.gamma = gamma

    def simulate(self, steps: int = 100, initial_infected: int = 1) -> PropagationTrace:
        """Run simulation steps.

        Uses standard compartmental logic (S, I, R counts only, mean-field approximation).
        """
        S = self.N - initial_infected
        I = initial_infected
        R = 0

        trace = PropagationTrace(seed_meme_id="simulated_meme")

        for t in range(steps):
            trace.time_steps.append(t)
            trace.susceptible_counts.append(S)
            trace.infected_counts.append(I)
            trace.recovered_counts.append(R)

            # New infections: beta * I * (S/N)
            new_infections = int(self.beta * I * (S / self.N))
            # Recoveries: gamma * I
            new_recoveries = int(self.gamma * I)

            # Apply
            new_infections = min(new_infections, S)
            new_recoveries = min(new_recoveries, I)

            S -= new_infections
            I += new_infections - new_recoveries
            R += new_recoveries

            if I <= 0:
                break  # Extinct

        return trace


class SISModel:
    """Susceptible-Infected-Susceptible model.

    Nodes recover but do not gain immunity (e.g. rumors, recurring trends).
    S -> I -> S loop allows endemic states.
    """

    def __init__(
        self, population_size: int = 1000, beta: float = 0.3, gamma: float = 0.1
    ) -> None:
        """Execute   Init   operations natively."""
        self.N = population_size
        self.beta = beta
        self.gamma = gamma

    def simulate(self, steps: int = 100, initial_infected: int = 1) -> PropagationTrace:
        """Execute Simulate operations natively."""
        S = self.N - initial_infected
        I = initial_infected
        # SIS has no "Recovered" bucket in the same sense, but we track
        # logic similarly.

        trace = PropagationTrace(seed_meme_id="sis_simulated_meme")

        for t in range(steps):
            trace.time_steps.append(t)
            trace.susceptible_counts.append(S)
            trace.infected_counts.append(I)
            trace.recovered_counts.append(0)  # Always 0 for SIS trace compatibility

            new_infections = int(self.beta * I * (S / self.N))
            new_recoveries = int(self.gamma * I)

            new_infections = min(new_infections, S)
            new_recoveries = min(new_recoveries, I)

            S = S - new_infections + new_recoveries
            I = I + new_infections - new_recoveries

            if I <= 0:
                break

        return trace


class SEIRModel(SIRModel):
    """Susceptible-Exposed-Infected-Recovered model.

    Adds an 'Exposed' (incubating) state. Useful for memes that require
    repeated exposure or "priming" before adoption.
    """

    def __init__(
        self,
        population_size: int = 1000,
        beta: float = 0.3,
        sigma: float = 0.1,  # Incubation rate (1/incubation_period)
        gamma: float = 0.1,
    ) -> None:
        """Execute   Init   operations natively."""
        super().__init__(population_size, beta, gamma)
        self.sigma = sigma

    def simulate(self, steps: int = 100, initial_infected: int = 1) -> PropagationTrace:
        """Execute Simulate operations natively."""
        S = self.N - initial_infected
        E = 0
        I = initial_infected
        R = 0

        trace = PropagationTrace(seed_meme_id="seir_simulated_meme")

        for t in range(steps):
            trace.time_steps.append(t)
            trace.susceptible_counts.append(S)
            trace.infected_counts.append(I)
            trace.recovered_counts.append(R)

            # New exposed
            new_exposed = int(self.beta * I * (S / self.N))
            # New infected (from exposed)
            new_infected = int(self.sigma * E)
            # New recovered
            new_recovered = int(self.gamma * I)

            new_exposed = min(new_exposed, S)
            new_infected = min(new_infected, E)
            new_recovered = min(new_recovered, I)

            S -= new_exposed
            E += new_exposed - new_infected
            I += new_infected - new_recovered
            R += new_recovered

            if E <= 0 and I <= 0:
                break

        return trace
