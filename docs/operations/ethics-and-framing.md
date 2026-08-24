# Ethics and framing

## The framing rule is a build rule

**The question is when a person notices they have been steered, not how steering is made
unnoticeable.**

The same experiment, described the other way, reads as a manipulation manual in an ethics committee
and at MPKK. Write from the detection and protection side in every document, every paper, and every
participant-facing string.

This is not only about prose. It constrains the software:

- **Detection measures are built before the manipulation.** Without the attribution battery, error
  injection is a manipulation experiment with no measure attached.
- **Every participant's exposure is exactly reconstructable from the log**: which projection, which
  injection flag, which order, which distortion direction and magnitude. This is a requirement of
  the debrief and of the ethics review, not a convenience.
- **The debrief view is part of the software**, not a page in the researcher's folder. At the end of
  the session the participant is told what was manipulated and how their own decisions related to
  the original order.

## Deception and its handling

The study uses two forms of deception: projection error and guidance distortion. Both are
presentation-layer only — world truth is never altered
([ADR-006](../adr/ADR-006-error-injection-in-the-presentation-layer.md)).

| Obligation | How it is met |
|---|---|
| Justification | The construct cannot be measured without it: recognising an invalid interpretation *is* the measured behaviour |
| Minimisation | Two types, never combined; magnitude calibrated to the smallest level that separates from human dispersion |
| Disclosure | Debrief view at the end of every session, covering every distortion type used (validator V-15) |
| Withdrawal | The participant may withdraw at any point; interrupted sessions are retained only with consent |
| Preregistration | OSF or AsPredicted before the first main session, with the injection design stated |

## Data

- Identifier is a URL parameter. The system never holds real identity; the link file stays with the
  principal investigator, outside the system.
- Excluded records are documented, never deleted.
- The repository is private during collection to protect the sample from contamination
  ([ADR-012](../adr/ADR-012-private-repository-during-collection.md)).

## What must not be built

- Any feature whose purpose is to make steering harder to notice.
- Any analysis that reports how to increase compliance rather than how to detect drift.
- Any publication framing that reads as an operational recommendation for AI-mediated command
  without the detection findings attached.
