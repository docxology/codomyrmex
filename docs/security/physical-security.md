# Physical Security -- Perimeter Fences and Badge Readers

Walk up to any well-run factory and the first thing you notice is the fence. Not because it is impenetrable -- a determined intruder can always find a way over, under, or through -- but because it establishes a boundary. It says: *everything inside this line is our responsibility, and we control who crosses it*. Behind the fence sits a gatehouse with badge readers. Behind the gatehouse, individual buildings have their own locks. Inside each building, sensitive areas require additional credentials. This layered access model -- perimeter, zone, asset -- is the oldest and most intuitive security architecture in human civilization, and it maps directly to how Codomyrmex structures its physical security layer.

## Access Control Theory

Access control is fundamentally about answering three questions for every request: *Who are you?* (authentication), *What are you allowed to do?* (authorization), and *What did you do?* (accountability). These three A's form the bedrock of every access control system.

- **Identification and Authentication**: A badge is a claim of identity. The reader verifies that claim against a database. In software, this maps to tokens, certificates, or API keys. The principle is identical: never trust a claim without verification.
- **Authorization Models**: Role-based access control (RBAC) assigns permissions to roles rather than individuals -- a factory worker badge opens the shop floor but not the server room. Attribute-based access control (ABAC) adds context: the same badge might work only during shift hours. Mandatory access control (MAC) enforces classification levels that even administrators cannot override.
- **Separation of Duties**: No single person should be able to both authorize a transaction and execute it. In the factory, the person who signs the purchase order should not be the one who receives the goods. This prevents fraud and reduces the blast radius of a compromised account.

## Defense-in-Depth at the Perimeter

A single fence is a speed bump. Multiple concentric barriers create a defense-in-depth posture:

1. **Deterrence** -- Visible fences, signage, and lighting discourage casual intrusion.
2. **Detection** -- Sensors, cameras, and motion detectors identify intrusion attempts.
3. **Delay** -- Reinforced barriers, mantraps, and access vestibules slow an attacker down.
4. **Response** -- Alarms trigger human or automated response before the attacker reaches the asset.

The goal is never to make intrusion impossible but to make the time-to-breach longer than the time-to-respond.

## Asset Management Lifecycle

You cannot protect what you do not know you have. Asset management follows a lifecycle:

- **Discovery**: Enumerate every asset -- hardware, software, data store, API endpoint. Shadow IT is the factory equivalent of an unlabeled chemical drum in the corner.
- **Classification**: Assign sensitivity levels. Not everything behind the fence is equally valuable. Crown jewels (private keys, customer data) get vault-level protection; break-room furniture does not.
- **Tracking**: Maintain a living inventory. Assets move, change ownership, and deprecate. A stale inventory is worse than none because it breeds false confidence.
- **Decommissioning**: When an asset reaches end-of-life, destroy it securely. A discarded hard drive is a factory loading dock left unlocked overnight.

## Surveillance Principles

Surveillance is not voyeurism; it is accountability. Effective surveillance follows four principles:

- **Comprehensive coverage**: No blind spots. Every entry, exit, and critical zone is observed.
- **Tamper evidence**: Logs and recordings must be immutable or at least tamper-evident. A camera whose footage can be erased by the person it watches is theater, not security.
- **Proportionality**: Monitor what matters. Excessive surveillance erodes trust and generates noise that obscures real threats.
- **Retention policy**: Keep recordings long enough to support incident investigation but not so long that storage becomes a liability.

## Vulnerability Assessment Methodology

A factory safety inspector walks the floor, checks fire extinguisher dates, tests emergency exits, and interviews workers. Vulnerability assessment follows the same pattern:

1. **Scope definition**: What are we assessing? A single building? The entire campus?
2. **Information gathering**: Blueprints, access logs, prior incident reports.
3. **Testing**: Attempt controlled intrusions. Verify that locks lock and alarms alarm.
4. **Analysis**: Rank findings by likelihood and impact. A propped-open fire door in the chemical storage wing is more critical than a loose hinge on the break-room door.
5. **Remediation tracking**: Findings without follow-up are findings wasted.

## Component Mapping

The physical security layer in Codomyrmex is implemented through five primary components at `src/codomyrmex/security/physical/`:

| Component | Factory Analogy | Responsibility |
|-----------|----------------|----------------|
| **AccessControlSystem** | Badge readers and gatehouse | Authentication, authorization, session management |
| **AssetInventory** | Factory asset register | Discovery, classification, tracking, decommissioning |
| **SurveillanceMonitor** | CCTV and alarm system | Real-time monitoring, log aggregation, alert correlation |
| **PerimeterManager** | Fences, gates, mantraps | Boundary definition, zone enforcement, ingress/egress control |
| **PhysicalVulnerabilityScanner** | Safety inspector walkthrough | Automated assessment, finding prioritization, remediation tracking |

## From Factory Floor to Code

The fence around a factory and the firewall around a network serve the same purpose: they define a trust boundary. The badge reader and the authentication token answer the same question: *should this entity be here?* The asset register and the software bill of materials solve the same problem: *what do we have and where is it?*

Understanding physical security concepts makes digital security intuitive. The abstractions are identical; only the medium changes. When you read about `AccessControlSystem` in the technical documentation, picture the gatehouse. When you see `SurveillanceMonitor`, picture the CCTV control room. The factory metaphor is not decoration -- it is a thinking tool.

## Why Physical Security Comes First

In any factory safety program, physical security is the foundation. You cannot train workers who cannot safely enter the building. You cannot monitor machines that have no power because someone cut the electrical feed from outside the fence. You cannot enforce governance over assets you have not inventoried.

The same logic applies in Codomyrmex. Physical security concepts -- authentication, asset management, monitoring, boundary enforcement -- are prerequisites that every other security layer depends upon. Digital security assumes you know what systems you have (asset inventory). Cognitive security assumes you know who your workers are (access control). Governance assumes you can prove what happened (surveillance and audit). AI safety assumes you can contain and observe AI systems (perimeter management and monitoring).

This is why physical security is documented first and why its components are foundational: they answer the most basic questions any security program must answer before it can do anything else.

## Cross-References

- Technical implementation details: [`docs/modules/security/physical/README.md`](../modules/security/physical/README.md)
- Full security module reference: [`docs/modules/security/`](../modules/security/)
- Security philosophy and index: [index.md](index.md)
- Digital security (the next factory layer inward): [digital-security.md](digital-security.md)
