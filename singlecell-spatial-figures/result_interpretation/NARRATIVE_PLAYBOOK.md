# Narrative patterns and contradiction handling

## Six reusable patterns

**Atlas / discovery.** Unresolved heterogeneity → robust identity and programme → time/space/condition structure → focused biological observation → validation appropriate to the claim. The narrative contribution can be an enabling resource or reproducible organization; it need not fabricate a causal mechanism. [P1, P2]

**Mechanism.** Phenomenon → candidate explanatory link → alternative explanation → perturbation or other identifying design → molecular/functional response → specificity and scope. Distinguish “X changes Y in this assay” from “X mediates the entire disease through Y”. The second requires evidence for the intervening chain.

**Spatial ecology.** Across-specimen co-variation → measured tissue localization → context-associated state/programme → controls against composition/density/anatomical artifacts → recurrence or functional challenge. Do not turn the localization step into an unperformed intervention. [P2, P6]

**Development.** Measured stage and state → inferred ordering → independently observed fate or localization → candidate regulator → selective experimental test. A temporal narrative must identify which arrows are measured and which are inferred. [P1, P3]

**Prediction / methods.** Defined prediction target → fair holdout and baselines → aggregate and failure-mode results → attribution through controlled comparisons → biological usefulness and scope. Negative comparisons can be the principal finding; do not select only the metric that favors the model. [P7]

**Mixed or negative findings.** Explicit prior prediction → observed effect and precision → checks that the test actually interrogated the prediction → supported versus unresolved parts → revised model and discriminating next step. Do not equate a wide interval with absence or claim compensation without measuring it. [P8]

These are author-defined operational patterns distilled from the sources, not an empirical survey proving that all CNS papers share one format.

## Result paragraph recipe

1. State the local question or motivated comparison.
2. Identify the experimental contrast and relevant biological units.
3. Report the main observation, effect/uncertainty where supplied, and heterogeneity.
4. Explain what the complementary or challenging experiment adds.
5. Finish with the strongest bounded conclusion and next unresolved question.

For Results, use concrete finding-led prose instead of a chronological list of tools. Use Discussion for the integrated conceptual model, external literature, novelty and remaining explanations. A figure title is a proposed claim and must pass the same evidence check as a sentence in the manuscript.

## Do not force these pairs to agree

| Apparent disagreement | First interpretation check | What would discriminate |
|---|---|---|
| Fraction increases but total cell number does not | Denominator and sampling coverage | Absolute counts/density with matched sampling |
| RNA increases but protein does not | Assay, temporal lag, normalization, uncertainty | Matched RNA/protein/time-course evidence |
| Spatial proximity but no receiver programme | Anatomy/density and relevant response endpoint | Appropriate local null and receiver response assay |
| Knockdown changes target RNA but not phenotype | Target engagement, timescale, endpoint precision | Functional endpoint with a design that resolves a meaningful effect |
| Discovery and validation effect signs differ | Contrast, population, effect scale and heterogeneity | Harmonized estimand and independent comparison |
| Significant subgroup A, nonsignificant subgroup B | Difference of significance is not interaction | Explicit difference-of-effects / interaction test |
| Model wins one metric but not another | What each metric rewards | Task-relevant errors, baselines and failure-mode analysis |

These possibilities are hypotheses to investigate, not explanations to assert by default.

## Worked example: fabricated teaching case, not biological results

Suppose source-linked synthetic results show that a state is more frequent in diseased tissue (R1), a programme rises within that state (R2), and the state is enriched near a particular compartment (R3). A perturbation changes the programme (R4), but the measured functional endpoint is imprecise and not convincingly changed (R5).

**Supported synthesis:** “The data identify a compartment-associated transcriptional state and show that the tested perturbation modifies its molecular programme in the experimental model.”

**Not established:** “The compartment drives disease by activating the programme” or “the perturbation rescues disease”. R3 adds location, not intervention; R4 tests a molecular consequence, not the full tissue mechanism; R5 does not establish either a functional benefit or its absence.

**Next decisive question:** Does manipulating the candidate component alter a prespecified functional endpoint after successful target engagement, with enough precision to distinguish a biologically meaningful effect? Additional UMAPs do not answer this question.

**Results-style draft (synthetic):** “We first compared the frequency and transcriptional programme of the candidate state across specimens. Its representation and programme score were elevated in the disease group (R1–R2), and spatial analysis placed the state preferentially near the tested compartment (R3). Perturbation of the candidate component reduced the molecular programme in the experimental system (R4). The functional comparison remained imprecise (R5). These observations link tissue localization to a perturbation-responsive programme, while leaving its contribution to the functional phenotype unresolved.”

This paragraph deliberately contains no invented patient counts, p-values or causal upgrade. Use the actual values only when the supplied bundle supports them.

## Acceptance checklist for the agent and reviewer

Every important sentence must have a source-linked result or verified external citation. The test/reference direction, denominator, measurement scale and biological repeat must be preserved. Negative and contradictory observations relevant to the question must be included or explicitly scoped out for a defensible reason. The final conclusion must not exceed its strongest identifying evidence. Targeted next steps must distinguish explanations rather than decorate the story. Record the reviewer and artifact version separately from automated checks.
