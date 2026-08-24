# Development environment, demo mode, and repository handling

## Demo mode

A separate flag, on only in demonstrations:

- Consent and identifier are skipped
- Condition set from the URL: `?demo=1&condition=ai_mediated&injection=guidance`
- **Debug panel:** the active condition, what the model computed, which injection is live, and
  which observations the answer was built from
- Time acceleration 10×

The debug panel is what turns a demonstration into an argument. Without it a supervisor sees one
arbitrary condition and does not know what they are looking at.

Demo mode collects no data and is the only place a condition may be changed freely
([ADR-011](../adr/ADR-011-condition-locked-at-session-start.md)).

## Codespaces

`.devcontainer/devcontainer.json`:

```json
{
  "name": "sa-experiment",
  "dockerComposeFile": "../docker-compose.yml",
  "service": "app",
  "forwardPorts": [5173, 8000],
  "portsAttributes": {
    "5173": {"label": "web", "visibility": "public"}
  },
  "postCreateCommand": "make setup && make seed-demo"
}
```

`make demo` starts the stack on the demo scenario. A supervisor can open a Codespace straight from
the repository and click a link.

## Repository visibility

**Private for the duration of collection.** The target population is technically capable young
officers; if injection proportions and probe answer keys are public before collection, one
participant searching the repository contaminates the sample.

Public at publication, with Zenodo archiving, a DOI, and a `CITATION.cff`. Scenario files are
written to be publishable from the start, so publication is a visibility change rather than a
rewrite. See [ADR-012](../adr/ADR-012-private-repository-during-collection.md).

## Secrets

Environment secrets, never the repository. Any model API key lives in the backend only and never
reaches the browser.

## Remote collection

Participants take part on their own devices, which is what makes a sample of 100 reachable. Four
consequences that are solved in code, not in instructions:

| Problem | Solution |
|---|---|
| Blanking is no longer a supervised-room matter | Fullscreen API plus `visibilitychange` and `blur`. A freeze begins only when fullscreen is active; every exit is logged as `focus_lost` and feeds an exclusion criterion |
| A second screen cannot be prevented | Do not try. Measure tab switches, window resizes, and focus loss during freezes. Report as a limitation |
| Browser variety is uncontrolled | Terrain and map are **baked** to hashed assets; nothing is generated at run time. Minimum viewport checked before the session starts |
| Attrition is higher | Design for 80 usable, recruit 100-110. Interrupted sessions remain analysable up to the point of interruption |

The supervised-room researcher console is replaced by an **admin view**: inspecting sessions and
logs during collection, filtering, JSON export, session health. The researcher observes rather than
drives.
