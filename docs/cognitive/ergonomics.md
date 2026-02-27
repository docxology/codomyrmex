# Cognitive Ergonomics: Human Factors and the Operator Interface

**Series**: [Cognitive Perspectives](./README.md) | **Topic**: Human Factors Engineering

## The Theory

Human factors engineering -- the discipline of designing systems that account for human cognitive, perceptual, and motor capabilities -- provides the formal foundation for interface design. Three frameworks are central.

**Fitts's Law** (1954) states that the time to reach a target is a logarithmic function of the distance-to-width ratio: MT = a + b * log2(2D/W). In CLI design, "targets" are commands and "distance" is the number of keystrokes or navigation steps required. Shorter command paths to frequent operations reduce movement time; deeply nested subcommands increase it. Fitts's Law is not a guideline -- it is a quantitative prediction that can be validated against actual operator timing data.

**Cognitive load theory** (Sweller, 1988) distinguishes three types of load. *Intrinsic* load is the inherent complexity of the task. *Extraneous* load is complexity introduced by poor design -- confusing layout, inconsistent terminology, unnecessary steps. *Germane* load is the cognitive effort devoted to learning and schema formation. Good interface design minimizes extraneous load so that more cognitive capacity is available for intrinsic and germane processing. This is not aesthetic preference; it is a measurable property of task performance.

The **GOMS model** (Card, Moran & Newell, 1983) decomposes expert task performance into Goals, Operators, Methods, and Selection rules. Goals are what the user wants to achieve. Operators are the atomic actions available (keystrokes, mouse clicks, command entries). Methods are sequences of operators that achieve goals. Selection rules determine which method to use when multiple exist. GOMS provides quantitative predictions of expert task completion time -- KLM-GOMS predicts to within 20% for routine tasks.

Norman's **mental model theory** (1988) explains errors as mismatches between the user's internal model of system behavior and the system's actual behavior. When the mental model is accurate, the user can predict system responses and recover from errors. When it diverges, the user takes actions based on false beliefs about what will happen. Interface design governs how accurately users form mental models; transparency reduces divergence.

## Architectural Mapping

| Ergonomics Principle | Module | Source Path | Implementation |
|---------------------|--------|-------------|----------------|
| Fitts's Law: minimize command distance | cli | [`cli/core.py`](../../src/codomyrmex/cli/) | Top-level commands for frequent operations; most common ops require fewest keystrokes |
| GOMS: Goals as nouns, Operators as verbs | cli | [`cli/`](../../src/codomyrmex/cli/) | `codomyrmex modules` (goal: discover), `codomyrmex analyze <path>` (goal: analyze) |
| Rich structured output | terminal_interface | [`terminal_interface/`](../../src/codomyrmex/terminal_interface/) | Colored, formatted output using Rich library; reduces visual parsing load |
| Mental model transparency | system_discovery | [`system_discovery/`](../../src/codomyrmex/system_discovery/) | `codomyrmex modules` lists all components; `codomyrmex status` shows system state |
| Progressive disclosure | documentation/education | [`education/curriculum.py`](../../src/codomyrmex/documentation/education/) | Curriculum sequences learning from simple to complex; scaffolded instruction |
| Composability (Unix philosophy) | cli + orchestrator | [`cli/`](../../src/codomyrmex/cli/), [`orchestrator/`](../../src/codomyrmex/orchestrator/) | JSON/YAML output formats enable shell piping and composition |
| Error recovery | terminal_interface | [`terminal_interface/`](../../src/codomyrmex/terminal_interface/) | Tab completion, inline help, error messages with remediation suggestions |

**The CLI architecture** embodies Fitts's Law. The most frequent operations -- `codomyrmex modules`, `codomyrmex status`, `codomyrmex check` -- are single-word subcommands requiring minimal keystrokes. Less frequent operations use longer paths: `codomyrmex workflow list`, `codomyrmex skills list`. Each additional path segment adds approximately 0.3 seconds for expert users according to KLM-GOMS timing estimates. The CLI hierarchy encodes a priority ranking: shorter paths for higher-frequency operations.

**The `terminal_interface` module** uses the Rich library for structured, colored terminal output. This is an explicit cognitive ergonomics decision. Unformatted monochrome text requires the operator to visually parse structure from whitespace and keywords -- extraneous cognitive load. Rich markup provides that structure via color, indentation, tables, and progress bars. The extraneous load reduction is not decorative; it frees cognitive capacity for germane processing (understanding the content) and intrinsic processing (solving the problem).

**`system_discovery`** supports accurate mental model formation. The `codomyrmex modules` command makes the entire system legible at a glance -- 86 modules with descriptions, status, and health indicators. Without this, the user must construct their mental model of available capabilities from documentation, source code, or trial-and-error. Each of these alternatives introduces higher extraneous load and greater risk of mental model divergence.

**`documentation/education/curriculum.py`** is a formal cognitive load management system. It sequences learning topics from simpler to more complex, each building on the previous. This is *progressive disclosure* -- the interface design principle of revealing information only when it becomes relevant. In cognitive load terms, it controls intrinsic load by staging complexity, ensuring that the learner is not overwhelmed by the full system at once.

## Design Implications

**Measure command frequency and optimize path depth for high-frequency operations.** Fitts's Law makes quantitative predictions. If `codomyrmex status` is used 10x more frequently than `codomyrmex compliance audit`, the former should have a shorter path. Analyze actual usage patterns and restructure command hierarchy accordingly.

**Use Rich output as extraneous load reduction, not decoration.** Every color, table, and progress bar should serve a cognitive function: grouping related information, distinguishing types, or indicating progress. Gratuitous formatting adds extraneous load rather than reducing it.

**Design for error recovery, not error prevention alone.** Norman's mental model theory predicts that users will take wrong actions when their model diverges from reality. Rather than trying to prevent all errors (impossible), design for rapid error detection and recovery: clear error messages, undo capabilities, confirmation prompts before destructive operations.

**Compose for the Unix pipeline.** The Unix philosophy (McIlroy, 1978) is a cognitive ergonomics principle: small tools, composable by pipes, minimize the working memory required to reason about each step. JSON and YAML output formats enable this composability, allowing operators to chain codomyrmex commands with standard Unix tools without learning a proprietary orchestration language.

## Further Reading

- Card, S.K., Moran, T.P. & Newell, A. (1983). *The Psychology of Human-Computer Interaction*. Lawrence Erlbaum Associates.
- Fitts, P.M. (1954). The information capacity of the human motor system in controlling the amplitude of movement. *Journal of Experimental Psychology*, 47(6), 381--391.
- Sweller, J. (1988). Cognitive load during problem solving: effects on learning. *Cognitive Science*, 12(2), 257--285.
- Norman, D.A. (1988). *The Psychology of Everyday Things*. Basic Books.
- McIlroy, M.D. (1978). Unix time-sharing system: foreword. *Bell System Technical Journal*, 57(6), 1902--1903.

## See Also

- [Cognitive Security](./cognitive_security.md) -- Cognitive load under adversarial conditions degrades security decision-making
- [Industrialization](./industrialization.md) -- Ergonomic interfaces at production scale
- [Cognitive Modeling](./cognitive_modeling.md) -- Working memory limits constrain interface design
- [Eusociality and Division of Labor](../bio/eusociality.md) -- Role specialization as ergonomic design (biological perspective)

*Docxology references*: [Personal_AI_Infrastructure](https://github.com/docxology/Personal_AI_Infrastructure) (CLI-first design, voice notifications for hands-free operation, rich terminal feedback)

---

*Return to [series index](./README.md) | [Bio perspectives](../bio/README.md) | [Project README](../../README.md)*
