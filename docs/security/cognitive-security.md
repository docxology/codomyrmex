# Cognitive Security -- Training the Factory Workers

The most sophisticated factory security system in the world can be defeated by a single worker who holds the door open for a stranger carrying a pizza box. This is not a failure of technology; it is a failure of cognition. Social engineering attacks do not exploit software vulnerabilities -- they exploit human psychology: trust, helpfulness, urgency, deference to authority. Cognitive security is the factory's training program, safety poster campaign, buddy system, and reporting culture. It is the recognition that human beings are both the weakest link and the strongest defense, depending entirely on how well they are prepared.

## Social Engineering Theory: Cialdini's Six Principles

Robert Cialdini identified six principles of influence that explain why social engineering works. Every phishing email, pretexting call, and tailgating attempt leverages at least one:

1. **Reciprocity**: When someone does you a favor, you feel obligated to return it. The attacker who holds the door, buys coffee, or offers technical help is banking a future favor -- like access to a restricted area.
2. **Commitment and Consistency**: Once you agree to a small request, you are more likely to agree to a larger one to remain consistent with your self-image. The attacker starts with "Can you confirm your department?" and escalates to "Can you reset my password?"
3. **Social Proof**: People follow the crowd. "Everyone else on your team has already updated their credentials through this link" exploits the assumption that if others did it, it must be safe.
4. **Authority**: People obey authority figures. An email that appears to come from the CEO, a phone call from "IT support," or a uniform and clipboard at the factory gate all exploit deference to perceived authority.
5. **Liking**: People comply with requests from people they like. Attackers build rapport, mirror body language, find common interests -- standard sales techniques repurposed for infiltration.
6. **Scarcity**: Urgency drives poor decisions. "Your account will be locked in 30 minutes unless you verify now" short-circuits deliberation. The factory equivalent is the vendor who says "this safety part is on backorder; I can get you one today if you let me into the warehouse."

Understanding these principles is not academic -- it is the foundation of effective awareness training. Workers who can name the principle being used against them are dramatically harder to manipulate.

## Phishing Attack Taxonomy

Phishing is not a single technique; it is a family of attacks that vary by targeting and medium:

- **Bulk phishing**: Mass-mailed, low-effort, low-specificity. The factory equivalent of leaflets thrown over the fence.
- **Spear phishing**: Targeted at a specific individual using personal information gathered from OSINT. The attacker who knows the factory manager's name, direct reports, and current projects.
- **Whaling**: Spear phishing aimed at senior executives. High effort, high reward.
- **Vishing**: Voice phishing. The phone call from "the bank" or "IT support."
- **Smishing**: SMS-based phishing. The text message with a malicious link.
- **Business Email Compromise (BEC)**: The attacker compromises or spoofs a legitimate business email to redirect payments or extract data. The factory equivalent of forged purchase orders.

Each variant requires different detection strategies, which is why a single "don't click links" rule is insufficient.

## Awareness Training Pedagogy

Effective security training is not a yearly checkbox exercise. Research consistently shows that:

- **Spaced repetition** beats single sessions. Monthly micro-trainings outperform annual hour-long lectures.
- **Simulated attacks** build muscle memory. Workers who have experienced a (simulated) phishing email recognize the real thing faster.
- **Positive reinforcement** outperforms punishment. Rewarding workers who report suspicious emails creates a reporting culture. Punishing workers who click bad links creates a hiding culture.
- **Contextual training** is more effective than generic training. A finance team needs training about invoice fraud; an engineering team needs training about watering-hole attacks.
- **Metrics drive improvement**: Track click rates on simulated phishes, time-to-report, and training completion rates. What is not measured cannot improve.

## Behavior Analysis Fundamentals

Behavioral analysis looks for anomalies that suggest compromised accounts or insider threats:

- **Baseline establishment**: What does normal behavior look like for this user, this role, this time of day?
- **Deviation detection**: Logging in at 3 AM, accessing files outside one's department, downloading unusual volumes of data -- these are deviations that warrant investigation.
- **Contextual enrichment**: A deviation is not automatically malicious. The worker who logs in at 3 AM might be covering a night shift. Context separates true positives from false alarms.
- **Privacy preservation**: Behavioral monitoring must respect privacy boundaries. The factory CCTV watches the shop floor, not the restroom. The monitoring system tracks access patterns, not personal communications.

## The Cognitive Threat Landscape

Beyond individual attacks, cognitive security must address systemic threats:

- **Disinformation campaigns**: Coordinated efforts to undermine trust in security controls, making workers dismissive of legitimate warnings.
- **Insider threat progression**: The path from disgruntled employee to data exfiltration follows a recognizable pattern -- grievance, ideation, planning, execution -- that behavioral analysis can interrupt.
- **Alert fatigue**: When workers receive too many false alarms, they stop responding to real ones. The factory where the fire alarm rings weekly for no reason is the factory where everyone ignores the alarm during an actual fire.

## Component Mapping

Cognitive security in Codomyrmex is implemented at `src/codomyrmex/security/cognitive/`:

| Component | Factory Analogy | Responsibility |
|-----------|----------------|----------------|
| **SocialEngineeringDetector** | The skeptical veteran who spots a fake uniform | Pattern recognition for social engineering indicators |
| **PhishingAnalyzer** | Mail room screening for suspicious packages | Email/message analysis, URL reputation, header inspection |
| **AwarenessTrainer** | Safety training program and poster campaigns | Training content delivery, simulation management, progress tracking |
| **BehaviorAnalyzer** | Shift supervisor who notices unusual behavior | Baseline modeling, deviation detection, contextual scoring |
| **CognitiveThreatAssessor** | Safety committee reviewing incident trends | Threat landscape analysis, campaign detection, risk scoring |

## From Factory Floor to Code

The factory safety poster and the security awareness module serve the same purpose: they embed vigilance into daily routine. The buddy system -- where no one works alone on dangerous equipment -- and multi-party authorization for sensitive operations share the same insight: a second pair of eyes catches what the first pair misses.

Cognitive security is where technology meets psychology. The most elegant encryption algorithm cannot protect data from a user who willingly hands over their credentials because someone on the phone sounded authoritative and urgent. Training, culture, and behavioral awareness are not "soft" controls -- they are the controls that address the threat surface that firewalls and scanners cannot see.

## Cross-References

- Technical implementation details: [`docs/modules/security/cognitive/README.md`](../modules/security/cognitive/README.md)
- Full security module reference: [`docs/modules/security/`](../modules/security/)
- Security philosophy and index: [index.md](index.md)
- Trust and governance (how organizational structure supports cognitive security): [trust-and-governance.md](trust-and-governance.md)
