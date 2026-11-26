# Corrections of 2026-11-26: Geometric Methods (Volume 1)

These corrections were made on 2026-11-26 at the author's direction after a review of the series.

They follow the first round committed as 371478c (the tables of Sections 17.2 and 17.7, the stage costs of Section 16.2.3, Figure 16.2). No figure, caption or file under `tools/`, `figures/` or `.build/` was changed. No line was added or removed, so line numbers are unchanged.

## Reconciled

1. **Chapter 16, Section 16.2.1 (robustness parameters).** The text said `adversarial_tolerance` "sets the convergence criterion for binary search during adversarial threshold detection". It now says the parameter "sets how far a prediction target may move before the log-spaced adversarial threshold search records a tipping point". Established from Section 9.4.1 (the search is log-spaced from the baseline outward), Section 10.2.3 (which contrasts Chapter 9's log-spaced grid with binary search in signal space) and Section 19.8 (the search records the first value at which any metric moves by more than the tolerance).

2. **Chapter 1, Section 1.5.2, Step 5.** "Binary search along each dimension" now reads "A log-spaced search along each dimension", for the same reason. The binary search of Sections 10.2.3, 14.6.3 and 20.5.4 is the signal-space flip-threshold search and is correct as written.

3. **Chapter 17, Section 17.3.2 (backward elimination).** The text gave the number of `optimize_subset` calls as $B(n) = n(n-1)/2 + 1$. It now gives $B(n) = n(n+1)/2$, "the same count as forward selection run to completion, $F(n, n)$". Established from the printed code: one call for the full set, then one call per active dimension while more than one is active, which is $1 + n + (n-1) + \cdots + 2 = n(n+1)/2$. For $n = 5$ this is 15, not 11. It equals the section's own $F(n, K) = Kn - K(K-1)/2$ at $K = n$.

4. **Chapter 16, Section 16.2.3 (evaluation budget table).** The backward-elimination row said $n \times C(\cdot)$. It now says $\frac{n(n+1)}{2} \times C(\cdot)$, from item 3. The "Other stages" column of Section 17.7 does not include the baselines (for $n = 5$ it is the compositional test, the MRI, the sensitivity profile and the adversarial search, about 32,400 calls), so it is unaffected.

5. **Chapter 19, Sections 19.4.1 and 19.5.1 ("30" and "31" configurations).** Both numbers are right and the text now says why. Section 19.4.1 reads "the 30 enumerated configurations". Section 19.5.1 reads "Thirty of the 31 configurations (the 30 enumerated ones and the full model)". Established from `formal/runs/ch19_campaign.json`: run A holds 30 enumerated subsets, and of the 31 non-empty on/off patterns exactly 30 have zero recall, the exception being {OO, Process}. The AUC range of 43% to 59% over the 31 was recomputed from the same file (43.1 to 58.5). `formal/runs/ch19_redraw.py` evaluates all 31.

6. **Chapter 9, Section 9.2.2 (indexing of the MRI weights).** The formula used $(w_0, w_1, w_2)$. It now uses $(w_1, w_2, w_3)$, as Appendix C (Definition C.1, Theorem C.6) and Section 10.6.3 do. The code listing, which indexes `weights[0]` to `weights[2]`, is unchanged.

7. **Chapter 5, Section 5.4 (example).** "Two circular clusters" now reads "two ring-shaped clusters". The example needs rings for its two loops, and the caption of Figure 5.2 already called them ring-shaped.

8. **Chapter 1, Section 1.5.2, Step 4 (MRI table).** The composite was printed as 1.43. It is now 1.44. Recomputed from the three values in the same table with the default weights: $0.5 \times 0.8 + 0.3 \times 1.4 + 0.2 \times 3.1 = 1.44$, as Sections 9.2.3 and 9.6.2 print it.

9. **Chapter 1, Section 1.5.3, item 3.** "5% of perturbations nearly double the error" now reads "nearly triple the error". A deviation of 3.1 on a baseline of 1.5 gives about 4.6, which Section 9.6.2 calls nearly triple, and Section 1.5.2 itself says the error moves by about twice the whole error.

10. **Chapter 1, Section 1.5.2, Step 2.** Step 1 enumerates the 25 subsets of size up to 3, but the frontier table of Step 2 includes the five-group model. Step 2 now reads "all 25 configurations, together with the full five-group model".

## Marked as illustrative or simulated

1. **Chapter 1, Sections 1.5.2 and 1.5.3.** The section's opening already says its numbers are invented. The steps and the summary used "the results reveal", "revealed" and "findings" without that qualifier. The words "in this illustration" or "(illustrative values)" were added at Step 1, at the two tables, and at the two summary sentences of Section 1.5.3.

2. **Chapter 8, Section 8.7.3.** "For the defect prediction example, the ratios are" now reads "For the illustrative frontier of Section 8.7.2, the ratios are".

3. **Chapter 8, Section 8.8.4.** The section said the Pareto frontier "recovers the known ground truth", that the absence of $k = 4$ "confirms" a property, and that "this result validates the Pareto approach". No run supports this, and the recorded run of Chapter 19 contradicts it. The section now presents the outcome as the intended, illustrative one ("would recover", "would mean", "would validate") and adds that the recorded run gives a frontier of two points, {Complexity} and {OO, Process}, the second a lucky draw (Sections 19.5 and 19.6; `formal/runs/ch19_campaign.json`, `pareto` has two entries).

4. **Chapter 9, Sections 9.6.3 and 9.6.4.** The tables were already introduced with "produces results like" and Figure 9.2 is captioned illustrative. "Several findings stand out", the synthesis sentence and the closing sentence now carry "in these illustrative results" or "in the illustration".

5. **Chapter 11, chapter opening and Sections 11.6.3 to 11.6.5 and 11.10.** The opening promised an example "that reveals which feature groups genuinely drive predictive performance". Section 11.6.3 said the results "typically exhibit" its tables, Section 11.6.4 that the frontier "typically contains four points", and Section 11.6.5 that the enumeration "correctly recovers this structure" and that "this ground-truth validation confirms" the pattern's reliability. The values are illustrative and the recorded run of Chapter 19 does not recover the generator's structure. The passages now say the values are illustrative, that the recorded run gives a two-point frontier, and that on these data the ground-truth test is not passed (best subset contains OO, single groups within two MAE points of one another, as Section 19.4.1 prints).

6. **Chapter 17, Section 17.3.1 and the chapter Summary, item 1.** The text said forward selection "empirically" and "typically" finds configurations within 5 to 15% of the global optimum. The repository holds no run that measured this. Both sentences now call it a working expectation that no recorded run in this volume tests. The figure of 5 to 15% is kept.

7. **Chapter 5, Sections 5.7.4 and 5.7.5.** "In practice, the most discriminative features tend to be" now reads "The features expected to discriminate most are". Section 5.7.5 said that on the DSWP dataset "TDA features reveal structure aligned with the known social organization", including separation by clan. Section 20.9 lists what has been run, which does not include any topological feature, and Sections 20.9.4 and 21.8 class the contribution of each geometric layer as posited. The lead sentence now says the features "are expected to show" the structure and that the three statements are posited with no recorded run.

8. **Chapter 20, Sections 20.2.3, 20.6, 20.7.3.** "In the DSWP data, regular codas tend to produce low geodesic deviation" is now stated as an expectation not yet measured (Section 20.9.4). "Produces a decoder ... invariant to recording artifacts" is now "is intended to produce", and "can then verify that" is "can then test whether", in line with Section 14.9, where reversal did not remove the nuisance. The sensitivity table of Section 20.7.3 is introduced with "would reveal ... (hypothetical values)", and "the defect prediction finding in Chapter 1" is "the defect prediction illustration in Chapter 1".

9. **Chapter 22.** Checked and left as it is. Section 22.4, the caption of Figure 22.2, the chapter summary and Section 21.8 all call the recorded run exploratory (one synthetic consumer, one seed).

## Withdrawn or updated

1. **Hohfeldian D4.** The volume does not use it. The only dihedral group in the volume is the symmetry group of a square grid in Chapter 13 (data augmentation), which the withdrawal in Geometric Ethics does not concern. The word "Hohfeld" does not occur in any chapter or appendix. Nothing was changed.

2. **Results of other volumes.** Chapter 22 and Section 21.8 cite three rows of the Volume 14 ledger. They were checked against `geometric-observation/claims/LEDGER.md` at its commit of 2026-11-25: PAPER-III.a is `[proved]`, T1 is `[exploratory]`, T1-MK is `[exploratory]`. The volume gives the same classes. Section 6.4.4 cites an archived draft of `geometric-economics` and says it is archived. Sections 10.6.3 and 14.1.2 name the Bond Index only as the template of the DRI and assert no result of it. No "Conservation of Harm", SU(2) gauge prediction or hysteresis result is cited. The "gauge transformation" of Section 7.7.4 is the chapter's own model of framing, not the Ethics prediction. Nothing was changed.

3. **README and Chapter 1's chapter list.** The README's "22 chapters + 3 appendices" matches `chapters/`. Section 1.6 lists Parts I to V as Chapters 2 to 5, 6 to 10, 11 to 15, 16 to 20 and 21 to 22, which matches the files. All 22 chapters and 3 appendices are on the `site` branch. Nothing was changed.

## Unresolved

1. **Chapter 18, Section 18.8.1, LaTeX report template (code listing).** The listing prints "The Model Robustness Index of 1.43" beside a 95th-percentile deviation of 3.1, the same illustrative numbers whose composite is 1.44 (Reconciled, item 8). It is inside a code listing, which this round does not edit. To change: 1.43 to 1.44 in the listing.

2. **Chapter 7, Section 7.4.2 ("Empirical Convergence Behavior").** The text says "for the economic games tested ... convergence typically occurs within 5--15 iterations" and gives an iteration profile. This repository holds no record of those runs, and Section 21.8 lists the material of Chapters 6 and 7 as posited or computed from hand-set inputs. Needed: either the `eris-econ` record (script, commit, output) that the iteration counts come from, or a decision to reword the passage as an expectation.

3. **Chapter 9, Section 9.2.1.** "The default has proven effective across a range of geometric models" (of the perturbation scale 0.5). No record in this repository. Needed: the source of the statement, or a decision to reword.

4. **Chapters 5 and 20, size of the coda dataset.** Section 5.7.5 gives "the DSWP dataset (1,501 annotated sperm whale codas)". Section 20.9.1 gives 8,719 annotated codas of 35 types from the repository of Sharma et al. (2024). These may be two different releases, and the repository does not say. Needed: which dataset Section 5.7.5 refers to and its size.

5. **Chapter 4, Section 4.6, subsection heading "Why SPD Distance Outperforms Flat Distance".** The subsection is an argument from a constructed pair of clicks and reports no measurement, and Section 20.9.4 says the comparison has not been run. The heading was left because the text under it is conditional ("Consider two whale clicks"). Needed: a decision whether the heading should read as an expectation.

## Figures and captions

No figure or caption is made wrong by these corrections. Three were checked because the text beside them changed: Figure 1.2 (its caption already says the values are invented, and it does not print the MRI), Figure 5.2 (already "ring-shaped"), and Figure 16.2 (it says the baselines are not shown, so the corrected backward-elimination count does not enter it). `tools/figs_*.py` contains neither 1.43 nor a backward-elimination count.
