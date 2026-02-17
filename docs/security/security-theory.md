# Security Theory -- The OSHA Rulebook

Before any factory opens its doors, engineers study decades of accumulated wisdom about what goes wrong and why. OSHA regulations did not appear from thin air -- they were written in the aftermath of real disasters, each clause representing a lesson paid for in injuries or lives. HAZOP analysis (Hazard and Operability Study) systematically asks "what if?" for every process parameter: what if the temperature is too high, the pressure too low, the flow reversed? Security theory serves the same purpose for information systems. It is the codified knowledge of what attacks look like, what defenses work, and how to reason about risk before an incident forces you to learn the hard way.

## Foundational Principles

### The CIA Triad

Every security decision ultimately serves one or more of three goals:

- **Confidentiality**: Information is accessible only to those authorized to see it. The factory equivalent: blueprints for a proprietary manufacturing process are stored in a locked safe, not pinned to the bulletin board.
- **Integrity**: Information is accurate and has not been tampered with. The factory equivalent: calibration records for precision instruments are signed and sealed so that no one can alter them undetected.
- **Availability**: Information and systems are accessible when needed. The factory equivalent: the fire suppression system works when there is a fire, not just during the annual inspection.

These three goals frequently tension against one another. Maximum confidentiality (encrypt everything, restrict all access) harms availability. Maximum availability (open everything, no authentication) destroys confidentiality. Security architecture is the art of finding the right balance for each asset.

### Least Privilege

Every user, process, and system should operate with the minimum set of permissions necessary to perform its function. The factory worker who operates the lathe does not need keys to the chemical storage room. When permissions are granted broadly, the blast radius of any compromise expands correspondingly.

### Defense-in-Depth

No single control is sufficient. Layer independent controls so that the failure of one does not expose the asset. This principle recurs throughout every security domain -- physical, digital, cognitive, and governance.

### Zero Trust

Traditional security models assume that anything inside the perimeter is trusted. Zero trust rejects this assumption: verify every request, regardless of origin. In the factory, this means badge-checking workers even when they are already inside the building, because a compromised badge should not grant unlimited access.

## Frameworks Overview

Security frameworks provide structured approaches to organizing and measuring security programs:

- **NIST Cybersecurity Framework (CSF)**: Organized around five functions -- Identify, Protect, Detect, Respond, Recover. Widely adopted, flexible, and technology-agnostic. Think of it as the factory safety manual's table of contents.
- **ISO 27001**: An international standard for information security management systems (ISMS). Certification demonstrates that an organization follows a systematic approach. The factory ISO 9001 certification, but for security.
- **OWASP Top 10**: The ten most critical web application security risks, updated periodically. Not a framework in the governance sense, but an invaluable prioritization tool. The "Top 10 Causes of Factory Injuries" poster.
- **CIS Controls**: Prioritized, actionable security measures. Divided into Implementation Groups (IG1, IG2, IG3) by organizational maturity. The factory equivalent of basic, intermediate, and advanced safety programs.

## Threat Modeling Methodologies

Threat modeling asks: *what can go wrong, and what should we do about it?*

### STRIDE

Developed at Microsoft, STRIDE categorizes threats by type:
- **S**poofing identity -- pretending to be someone else
- **T**ampering with data -- unauthorized modification
- **R**epudiation -- denying an action occurred
- **I**nformation disclosure -- exposing data to unauthorized parties
- **D**enial of service -- making a system unavailable
- **E**levation of privilege -- gaining unauthorized access levels

### DREAD

A risk-scoring model that evaluates threats on five axes:
- **D**amage potential -- how bad is it if the threat materializes?
- **R**eproducibility -- how easily can the attack be repeated?
- **E**xploitability -- how much skill does the attack require?
- **A**ffected users -- how many users are impacted?
- **D**iscoverability -- how easy is the vulnerability to find?

### PASTA

Process for Attack Simulation and Threat Analysis -- a seven-stage, risk-centric methodology that aligns threat modeling with business objectives. It proceeds from business context through technical scope to attack enumeration and risk analysis.

### Attack Trees

A hierarchical representation of how an attacker might achieve a goal. The root node is the objective ("steal proprietary blueprints"); child nodes are methods ("bribe an employee," "compromise the file server," "dumpster dive"). Each path through the tree is a potential attack scenario. This is the security equivalent of a factory fault tree analysis.

## Risk Assessment: Quantitative Methods

- **Annual Loss Expectancy (ALE)** = Single Loss Expectancy (SLE) x Annual Rate of Occurrence (ARO). This translates risk into financial terms that executives understand. A factory that loses $100,000 per fire and expects one fire every five years has an ALE of $20,000 -- which justifies a $15,000 sprinkler system but not a $200,000 one.
- **Monte Carlo simulation**: When probabilities are uncertain, run thousands of simulated scenarios and examine the distribution of outcomes. This replaces false precision with honest uncertainty ranges.
- **Risk matrices**: Plot likelihood against impact on a grid. Simple, visual, and useful for communication, though they can oversimplify complex risk landscapes.

## Security Architecture Patterns

- **DMZ (Demilitarized Zone)**: A network segment between the external and internal networks, hosting public-facing services. The factory visitor center -- open to the public but separated from the production floor.
- **Microsegmentation**: Divide the internal network into fine-grained zones, each with its own access controls. Instead of one large factory floor, imagine individual work cells with their own badge readers.
- **Defense-in-depth layering**: Combine preventive, detective, and corrective controls at every tier.
- **Fail-safe defaults**: When a control fails, it should fail to a secure state. The factory door that locks when power fails, not the one that swings open.

## Component Mapping

Security theory in Codomyrmex is implemented at `src/codomyrmex/security/theory/`:

| Component | Factory Analogy | Responsibility |
|-----------|----------------|----------------|
| **ThreatModeler** | HAZOP analysis team | STRIDE/DREAD/PASTA threat enumeration and scoring |
| **RiskCalculator** | Actuarial analysis for insurance | Quantitative risk assessment, ALE computation, Monte Carlo |
| **FrameworkMapper** | Regulatory compliance cross-reference | Mapping controls to NIST, ISO, OWASP, CIS frameworks |
| **PrincipleEnforcer** | Safety engineering review board | Validation of least privilege, separation of duties, fail-safe defaults |
| **ArchitectureAnalyzer** | Factory layout planning | DMZ design, microsegmentation analysis, defense-in-depth validation |

## From Factory Floor to Code

OSHA regulations exist because people were hurt before the rules were written. Security frameworks exist because organizations were breached before the controls were defined. Theory is not abstract -- it is the distilled memory of every past failure, organized so that we do not repeat it.

When you perform threat modeling on a Codomyrmex module, you are doing exactly what a HAZOP team does when they review a new chemical process: systematically asking "what if this goes wrong?" and documenting the answer before it happens on the factory floor.

## Cross-References

- Technical implementation details: [`docs/modules/security/theory/README.md`](../modules/security/theory/README.md)
- Full security module reference: [`docs/modules/security/`](../modules/security/)
- Security philosophy and index: [index.md](index.md)
- Physical security (where theory meets tangible controls): [physical-security.md](physical-security.md)
- Digital security (operational application of theory): [digital-security.md](digital-security.md)
