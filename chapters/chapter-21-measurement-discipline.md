# Chapter 21: The Measurement Discipline

> *"The first principle is that you must not fool yourself, and you are the easiest person to fool."*
> --- Richard Feynman, Caltech commencement address (1974)

The first twenty chapters describe instruments: distances, manifolds, indices, searches. This chapter describes the rules under which a number produced by one of those instruments may be called a result. The rules are short. A claim is either *posited* or *measured*. It becomes measured only by surviving a test that was fixed before the data were seen, that could have failed, and whose record is kept whatever its outcome.

The chapter exists because the instruments do not enforce this by themselves, and this volume is its own evidence. A review of the first twenty chapters in November 2026 found a worked example whose printed code gives a different answer from the prose around it (Section 6.6.1), an evaluation function whose output did not depend on its argument (Section 20.7.1), result tables that no run had produced (Chapters 19 and 20), and, in the campaign reported in Section 17.11, a statistic believed for a time to be free of a nuisance quantity that was not. None of these was caught by an accuracy number. Each would have been caught by one of the rules below.

The normative source is the Claim Ledger Specification, PE-CLS-1.0, in the `philosophy-engineering` repository. This chapter is a reader's guide to it for users of geometric methods, with examples from this volume. Where the two differ, the specification governs.

---

## 21.1 Posited and Measured

A **posited** statement is one asserted because it follows from the construction, seems reasonable, or was observed once without a prior commitment. A **measured** statement is one that was put at risk: a prediction and a pass mark were written down first, the measurement was then made, and the outcome was recorded.

Most of what a geometric model says is posited. The covariance matrix of Section 6.6.1 is posited. So are the boundary penalties of Section 6.4.3 and the tables in Chapters 8, 9, 11 and 12 that the text introduces with "might look like". This is not a defect. A construction has to be stated before it can be tested. The defect is to cite a posited statement as if it were measured, and the remedy is to label every statement with its class.

| Class | What supports it | Minimum evidence |
|---|---|---|
| Proved | Deduction | A complete written proof and one independent line-by-line check; machine-checked where feasible |
| Replicated | Several independent settings | Two or more settings, each meeting its own registered pass mark |
| Demonstrated | One setting | A registration that predates the run, a committed result, an instrument that can be rerun |
| Predicted | An out-of-sample forecast | Registered before the data existed or before they were unblinded |
| Definition | Nothing; it is stipulated | A construction or a name that asserts nothing about the world |
| Exploratory | A suggestive observation | Labelled as such wherever it appears; may not support a claim of a higher class |
| Refuted | Valid evidence against | The registered prediction failed on a valid measurement |
| Withdrawn | Nothing | The supporting evidence was found to be defective |

"Posited" covers the definition and exploratory rows. "Measured" covers the first four.

**Withdrawn is not refuted.** A claim is refuted when a valid measurement contradicted it. The world answered, and its negation is now supported. A claim is withdrawn when its evidence turns out to be invalid: a broken instrument, a contaminated arm, a sampling rule that was not what it was thought to be. The world did not answer, the claim returns to unknown, and its negation gains nothing. Section 17.11.2 has an example. The statement that hubness in the real corpus rises with corpus size was withdrawn, not refuted, when the split between queries and corpus was found to follow file order. The corrected measurement is consistent with a rise and with none.

---

## 21.2 Registration

A **registration** is a prediction recorded before the measurement that tests it. It contains five things:

1. the prediction, stated so that it can fail as written;
2. the **bar**, a numeric threshold that counts as success;
3. how the bar was sized: from a power analysis, from a pilot value with a margin, or with an explicit statement that neither was done;
4. the design: sample size, stopping rule, and the unit by which errors are clustered;
5. a content hash of the registration and of the instrument code.

A registration also separates two kinds of gate. A **physics gate** is one whose miss refutes the claim. An **instrument gate** is one whose miss voids the run, because the instrument was not measuring what it was meant to. If the two are not separated in advance, a failed experiment can be redescribed afterwards as a broken instrument.

**Priority is shown by ancestry, not by date.** A timestamp is written by the author. The position of a commit in a version-control graph is not. The registration must be an ancestor of the first commit that contains the result:

```bash
git merge-base --is-ancestor <seal-commit> <first-commit-adding-result>
```

This is evidence that is hard to tamper with. It is not proof of the time on the clock, and it is destroyed by rewriting history, so commits that carry a seal are never rebased.

**Amendments** are dated, state their reason, and come before the data are unblinded. A change of plan after the result is seen is a new registration.

---

## 21.3 Frozen-Null Gates

A bar stated as an absolute number invites two errors. It can be set where chance already reaches it, and it can be moved after the result is known. A **frozen-null gate** avoids both. The bar is a margin over one or more *nulls*, which are versions of the instrument that cannot contain the effect, and the nulls, the margin and the date are committed before the run.

Let $s$ be the score of the system under test and $s^{(1)}_0, \ldots, s^{(J)}_0$ the scores of $J$ nulls on the same held-out data. The gate passes when

$$s - \max_{j} s^{(j)}_0 \;\geq\; \delta. \tag{21.1}$$

The `xbse` instrument, which scores text on moral dimensions, uses two nulls: an encoder with untrained weights, and a bag-of-words classifier. A dimension is validated only if its cross-dataset score beats both by $\delta = 0.10$. Under that gate eight of nine dimensions pass and one fails, and the one that fails is reported with the others (`xbse` README, 2026-09-02). A bar of this kind may be tightened later. It may not be loosened.

**Size the margin in units of noise.** A margin has to be compared with the spread of the difference it is judging. If the difference in (21.1) has standard error $\sigma_\Delta$ when no effect is present, and the margin is set at $\delta = z\,\sigma_\Delta$, then a system with no effect passes with probability

$$\Pr(\text{pass} \mid \text{no effect}) = 1 - \Phi(z), \tag{21.2}$$

where $\Phi$ is the standard normal distribution function. A margin chosen without reference to $\sigma_\Delta$ has an unknown false-positive rate, and an absolute tolerance tests itself and not the system.

**A null can move.** Section 17.11.2 is a warning about nulls that depend on the experiment. The null skewness of a retrieval count is $1/\sqrt{\rho}$, which rises as the query budget $\rho$ falls. A comparison made at two different budgets compares two different nulls. Where a null depends on a design quantity, either hold that quantity fixed or model the null and remove it, and then confirm by measurement that it has been removed.

---

## 21.4 Admissibility

A registration can be made first, reported in full and cited at the right class, and the experiment can still be incapable of grading the claim. **Admissibility** is the property that the design could have failed. It has four checks, and each is discharged by a named artifact, not by the author's assurance.

| Check | Question | Discharged by |
|---|---|---|
| A1 Nonvacuity | Could any outcome have withheld the pass? | A constructed record that the registered grading code scores as a miss. For a statistical test, many records drawn from the null, on which the code passes at no more than its nominal rate |
| A2 Identification | Is every fitted object the test relies on identified, on data fit for that role? | The data each object was fitted on and its overlap with the evaluation data; an identification statistic with a threshold |
| A3 Intervention | Did the manipulation move the named construct, leave the instrument measuring, and not build the response? | A manipulation check; an instrument check under treatment; a placebo arm |
| A4 Inference | Is the estimate the registered one, on the registered population? | A fixed estimand and denominator; an account of exclusions; a correction for the family of tests, fixed in advance |

A1 is a property of the design and is settled before any data exist. A2 to A4 are instrument gates: a miss voids the run and does not refute the claim, and the void is recorded with the check that failed.

Three examples from this volume show what each check is for.

**A1, a function that cannot fail.** The first version of the evaluation function in Section 20.7.1 computed a vector of weights from its parameters and then did not use it. Its return value was the same for every parameter vector. A campaign run on it would give every subset of dimensions the same error, a flat sensitivity profile and a robustness index of zero, and none of these would say anything about the decoder. The witness that A1 asks for takes one line: evaluate the function at two different parameter vectors and require the outputs to differ. The corrected function in Section 20.7.1 now ends with that line. The defect example of Chapter 19 has a milder form of the same problem, and the recorded run shows its cost: the function reads only whether each parameter is below 1000, so 189,462 calls in one campaign came down to 32 distinct models, and the robustness index came out exactly zero (Section 19.7).

**A3, a manipulation that moved something else.** In the measurement reported in Section 17.11.2, the manipulated quantity was corpus size. The script that varied it also drew queries from a different part of the dataset than the corpus, so the query distribution was shifted in every cell. The response attributed to corpus size was partly a response to that shift. A placebo arm, the same rows shuffled before the split, exposed it.

**A4, an error bar on the wrong unit.** In the same measurement the largest corpus in each ladder was the whole pool, so every seed shared one corpus and only the queries varied. The spread across seeds in that cell was a fraction of the spread in the others, and that cell carried the most weight in the fitted slope. Standard errors belong to the unit that was resampled. A corpus that was drawn once has a sample size of one, however many queries were run against it.

A registration that declares all four checks not applicable has checked nothing, and a conforming report says how many were declared not applicable.

---

## 21.5 The Record

**Completeness.** Every result is reported, whatever its sign. Stated that way the rule cannot be checked, because the set of unreported results cannot be seen. The specification makes it checkable by a device: registrations are numbered from a contiguous sequence, and every number resolves to a disposition, which is one of reported, superseded, void with a reason, or never assigned. A hidden failure then needs a visible gap or a false entry. This does not prove that nothing was hidden. It means that hiding takes an act and not an omission.

**Authority.** A book, a paper or a talk holds no authority to assert. It is a view over the record, and every assertion in it resolves to an entry whose class the context admits. This is why the sections of this volume that report measurements name the file each number came from, and why Sections 6.4.4 and 17.11 open with a statement of status. A reader should be able to tell, for any number in the text, whether it was measured, on what, and where the record is.

**Dependencies.** A claim that uses another claim says so. When a claim is refuted or withdrawn, everything that depends on it is found mechanically and suspended until it is re-examined. The size of that set is the cost of the error, and keeping it small is a reason to state claims narrowly.

---

## 21.6 Five Working Rules

The following rules are not in the specification. Each records a mistake made in this programme, and each is cheap to apply.

1. **Test the pipeline, not the components.** Every stage can pass its own check while the composed result is wrong. The witness of A1 is run through the whole path, from raw input to the graded number.
2. **Selection is fitting.** Data used to choose among model structures, even only to rank candidates, are not held out. A held-out set is one that no decision has touched.
3. **Cluster by the unit of the covariate.** If the predictor of interest varies by problem, the sample size is the number of problems, not the number of responses, and standard errors are clustered by problem.
4. **Measure invariance.** Before a statistic is called independent of a nuisance quantity, measure it under two protocols that differ only in that quantity (Section 17.11.3, rule 6). Dividing by a null removes the null's location and not its shape.
5. **Agreement under one sampling rule is one measurement.** Repetitions that share a split, a seed schedule or a corpus agree with each other for that reason. Independent confirmation changes the thing that might be wrong.

---

## 21.7 How the Discipline Fails

A method that cannot say how it fails should not be trusted, and this one fails in at least four ways.

**The apparatus becomes the output.** A programme can produce registrations and conformance reports and no results. Nothing in the rules detects this. The record is to be judged by the claims it carries.

**Registration as theatre.** A bar that no outcome could miss satisfies the letter of Section 21.2. The witness of A1 is the main defence, and it is incomplete: a witness can be weaker than the real alternative, and a bar that refuses a pure null can still credit a proxy for the effect.

**The verifier shares the author's blind spot.** A check made by someone, or something, with the same assumptions and tools will miss what the author missed. Independence comes in degrees and is described, not asserted. The proofs of Appendix C and the identities of Chapter 17 that are checked symbolically are checked by a different kind of process from the one that wrote them, which is the point of doing so. A symbolic check confirms the algebra. It does not confirm that the algebra is the right model.

**The method is itself posited.** The specification is an unregistered claim about how inquiry should be governed. By its own rules its class is exploratory until programmes other than its author's have used it and reported what broke.

---

## 21.8 The Status of This Volume

Applying Section 21.1 to the volume itself gives the following, as of November 2026.

| Material | Class | Record |
|---|---|---|
| Theorems of Appendix C | Proved in writing. Parts (iii) and (iv) of Theorem C.1, Proposition C.3.1 and Corollary C.7.1 were restated or reproved in the November 2026 review | `formal/matlab/volume_checks.m` for the identities and cases it covers; no machine-checked proof |
| Identities of Section 17.11 | Proved; checked symbolically | `formal/matlab/ch17_neighbourhood_stats.m` |
| Measurements of Section 17.11 | Demonstrated or exploratory, as each source file states; one withdrawn claim | `openvector-bench`, files named in the section |
| Einstein midpoint (Section 3.6), interaction identities (Section 12.4.2), hypervolume (Section 18.6) | Proved; checked symbolically or against an independent computation | `formal/matlab/volume_checks.m` |
| Edge weights of Section 6.6.1 and loss-aversion table of Section 7.7.1 | Computed from the printed code; the values follow from hand-set inputs | `formal/matlab/volume_checks.m` |
| Covariance, penalties, displacement coefficients and scaling functions of Chapters 6 and 7 | Posited | None |
| Discontinuities quoted in Section 6.4.4 | Record of an archived draft | `geometric-economics`, as cited there |
| Tables of Chapters 1, 8, 9, 11 and 12 | Posited; the text presents them as illustrations | None |
| Results of Chapter 19 | Measured on one recorded run, with an oracle bound and a 20-seed redraw. Exploratory: no prediction was registered before the run | `formal/runs/ch19_*.py` and their JSON outputs |
| Experiment of Section 14.9 | Three predictions registered in the script before it ran, graded on one recorded run | `formal/runs/ch14_shortcut_experiment.py` and its JSON output; priority shown by file hash, not by version-control ancestry |
| Results of Section 20.9 | Measured, but the executed notebook is not committed, so there is no public record | `eris-ketos` notebook, executed copy of 12 March 2026 |
| Contributions claimed for the geometric layers in Sections 20.2 to 20.4 | Posited; the comparison of Section 20.9.4 has not been run | None |

Two domains of the wider series had passed frozen-null gates when the repository's status note was written in July 2026: moral dimensions in text, and legal text. Their records are in the instrument repositories `xbse`, `moral-spectrum-analyzer` and `lebse`, not in this volume.

---

## Summary

A number from a geometric instrument is posited until it has been put at risk. Putting it at risk means registering the prediction and its bar before the measurement, with the registration an ancestor of the result in the version-control graph; setting the bar as a margin over nulls that are fixed in advance and sized in units of noise; showing that the design could have failed, by a witness the grading code scores as a miss; and keeping every outcome in a numbered record. A withdrawn claim is not a refuted one. A book is a view over that record and asserts nothing the record cannot show.

---

## Notes and Further Reading

The normative text is PE-CLS-1.0, *The Claim Ledger Specification* (Bond, 2026; amended 2026-10-17), in the `philosophy-engineering` repository, with its companions PE-BRW-1.0 and PE-DSC-1.0. Pre-registration as a remedy for undisclosed flexibility in analysis is argued in Simmons, Nelson and Simonsohn, "False-Positive Psychology" (*Psychological Science*, 2011), and the practice is set out in Nosek et al., "The Preregistration Revolution" (*PNAS*, 2018). The distinction between a claim's support and the risk it bore follows Popper, *The Logic of Scientific Discovery* (1959), and Mayo, *Statistical Inference as Severe Testing* (2018).
