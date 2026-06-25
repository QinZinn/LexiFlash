# ADR 001: NLP Engine Migration To Rust (`nlprule` + `wordnet-db`)

- Status: Accepted
- Date: 2026-06-25

## Context

LexiAnki is currently a hybrid Python/Rust CLI application. The current roadmap targets a Rust-first desktop rewrite for v4.0.0 using Dioxus, with future expansion toward mobile and later AI-assisted features such as generated questions in the v6/v7 timeframe.

The main blocker for moving the NLP core fully into Rust is the current Python/NLTK dependency chain in `src/processor.py`. Today, the vocabulary extraction pipeline depends on:

- NLTK POS tagging
- NLTK WordNet lemmatization
- NLTK WordNet synset/lexname lookup
- Python-side stopword handling

That dependency chain is acceptable for the current CLI, but is a poor fit for a Rust-native desktop/mobile target. The goal of the spikes summarized here was to determine whether the current NLP pipeline can be replaced with a Rust-native implementation without carrying a Python runtime into the application.

Four technical spikes were completed:

1. `spikes/rust_bert_nlp/`: evaluate `rust-bert` + `tch` + `libtorch` for POS tagging
2. `spikes/nlprule_nlp/`: evaluate `nlprule` for POS tagging + lemmatization
3. `spikes/nlprule_processor_port/`: port the non-WordNet filtering logic from `src/processor.py`
4. `spikes/nlprule_processor_port/` extension: add WordNet lexname gating using `wordnet-db`

The core technical question was not just "can Rust do POS tagging?", but "can the existing processor behavior be reproduced closely enough in Rust to justify the migration?"

## Decision

Use:

- `nlprule` for POS tagging and lemmatization
- `wordnet-db` for WordNet lexname lookup
- Rust-native logic for all remaining filtering steps in `src/processor.py`

This means the planned Rust NLP engine for v4.0.0 should implement:

1. POS tagging
2. Proper noun filtering
3. Lowercase normalization
4. Pre-lemmatization token validation
5. POS mapping for downstream behavior
6. Lemmatization
7. Proper-adjective capitalization heuristic
8. WordNet lexname gate for capitalized tokens
9. Post-lemmatization validation
10. Stopword filtering
11. Known-word filtering
12. Deduplication with first-occurrence retention and context mapping

`rust-bert` / `tch` / `libtorch` are removed from consideration for this NLP engine decision.

Rationale:

- `rust-bert` can run POS tagging on this machine, but requires `tch` and `libtorch`
- the measured deploy/runtime cost is too high for this use case
- `rust-bert` does not solve lemmatization directly
- `nlprule` is materially lighter, faster to start, and already includes lemmatization

The migration accepts a measured behavior drift relative to the current Python pipeline:

- Recall of the Rust prototype vs the Python processor on the shared fixture: `29/31 = 93.55%`
- Effective mismatch floor on that fixture after adding the WordNet gate: `2/31 = 6.45%`

This drift is accepted as a model/data difference, not an engineering defect, for the current decision. The remaining observed mismatches are caused by POS/lemma differences between `nlprule` and the current NLTK+WordNet pipeline.

## Decision Data

### `rust-bert` vs `nlprule`

| Metric | `rust-bert` | `nlprule` |
| --- | --- | --- |
| POS pipeline availability | Yes | Yes |
| Lemmatization availability | No built-in lemmatization pipeline used in spike | Yes |
| Clean release build time | ~`3m45s` to first failure, then ~`1m20s` after dependency workaround | `66.1s` |
| Build stability | Initial dependency failure (`indicatif` / `console` feature conflict) | No serious build failure in spike |
| Release binary size | `13 MB` | `16 MB` |
| Extra runtime/model assets | `95 MB` model cache + `967 MB` libtorch | `12 MB` `en_tokenizer.bin` used for POS+lemma; cache directory `~/.cache/nlprule` measured `19 MB` including `en_rules.bin` |
| Cold load on sample run | `2991 ms` model load | `571 ms` model load on 5-sentence sample |
| Cold load on ~230-token benchmark | `3049 ms` model load | `455 ms` model load |
| Throughput on ~230-token benchmark | `157 ms` POS inference | `44 ms` tokenize + POS + lemma |
| 5-sentence POS comparison vs NLTK | `43/46 = 93.48%` exact tag match | `41/46 = 89.13%` exact tag match, `42/46 = 91.30%` normalized POS match |
| Lemma comparison vs NLTK | Not applicable in spike | `44/46 = 95.65%` lemma match |
| License note | Depends on `tch` / `libtorch`; model cache in 100s of MB to GB range per crate docs | Crate is `MIT OR Apache-2.0`; binary data derived from LanguageTool v5.2 is `LGPLv2.1` |

### Why `rust-bert` was rejected

Measured during spike 1:

- `rust-bert` built only after a dependency workaround in the spike crate
- release binary was only `13 MB`, but deployment required:
  - `95 MB` model cache in `~/.cache/.rustbert`
  - `967 MB` libtorch runtime
- cold load was approximately `3.0s`
- POS-only inference on the ~230-token benchmark was `157 ms`
- lemmatization still required a separate solution

This cost is too high for the LexiAnki/LexiFlash NLP core, where the requirement is lightweight local processing, not transformer-grade semantic modeling.

### Why `nlprule` was accepted

Measured during spikes 2-4:

- release binary: `16 MB`
- tokenizer asset used for POS+lemma: `12 MB`
- `~/.cache/nlprule`: `19 MB`
- cold load on sample: `571 ms`
- cold load on ~230-token benchmark: `455 ms`
- tokenize + POS + lemma on ~230-token benchmark: `44 ms`
- no Python runtime required
- lemmatization is already included
- processor-port prototype reached `29/31 = 93.55%` recall vs the Python processor on the shared fixture once the WordNet gate was added

### License Risk

`nlprule` itself is licensed under `MIT OR Apache-2.0`, but the project README states:

> The nlprule binaries (`*.bin`) are derived from LanguageTool v5.2 and licensed under the LGPLv2.1 license.

This is a packaging/release risk that must be reviewed before any public release or commercial use. This ADR is not legal advice; it records a concrete technical licensing note discovered during the spike.

### Remaining Mismatches After WordNet Gate

The Rust processor-port prototype initially had a false mismatch caused by missing WordNet lexname gating:

- `american` appeared in Rust output but not Python output

After adding `wordnet-db` + lexname mapping from the same NLTK WordNet data:

- `american` disappeared from Rust-only output
- the remaining mismatches were:
  - `datasets` in Python vs `dataset` in Rust
  - `tagging` in Python vs dropped in Rust because `nlprule` produced `VBG -> tag`, which then failed the `len >= 5` validation rule

These are the currently observed mismatch examples that remain after removing the "missing WordNet gate" explanation.

### Cost Of Adding WordNet

Measured in `spikes/nlprule_processor_port/`:

- before WordNet gate:
  - `model_load_ms = 290`
  - `process_ms = 54`
- after WordNet gate:
  - `model_load_ms = 426`
  - `wordnet_load_ms = 502`
  - `process_ms = 70`

Observed additional cost on the small fixture:

- `+502 ms` startup load time for WordNet
- `+16 ms` processing time

This overhead must be re-measured on a larger real-world corpus before it is treated as representative.

## Status

Accepted on `2026-06-25`.

This ADR applies to the NLP core planned for v4.0.0.

The UI framework decision (Dioxus) is out of scope for this ADR. This record only captures the NLP engine decision.

## Consequences

### Positive

- Removes the Python runtime from the planned NLP core
- Avoids `tch` / `libtorch` entirely
- Keeps runtime and deploy size materially smaller than the `rust-bert` path
- Keeps cold start much lower than the `rust-bert` path
- Preserves the ability to reproduce most of the current processor logic directly in Rust

### Negative / Risks To Track

- Extracted vocabulary output will differ from the current Python CLI output
- The difference is not necessarily a bug; it is a consequence of using a different NLP engine
- Migration between the current CLI and the future Rust app should communicate that output differences are expected
- `nlprule` binary data is under `LGPLv2.1`; packaging and release implications must be reviewed before public release or commercial use
- The spike measurements were taken on a small shared fixture (8 sentences) and a ~230-token synthetic benchmark; larger corpus validation is still required
- `nlprule` binary data is derived from LanguageTool v5.2, which is relatively old; availability of newer resources should be monitored
- The WordNet gate depends on bundling or otherwise shipping WordNet data files, which adds size and packaging complexity

## Follow-up Actions

Before beginning the real port, complete the following:

1. Validate the spike results on a larger real corpus, such as one full VnExpress or BBC article, using both the Python processor and the Rust prototype
2. Review the practical implications of `LGPLv2.1` for `nlprule` binary data before any public release or commercial distribution
3. Decide how to bundle and update:
   - `nlprule` tokenizer data
   - WordNet data required by `wordnet-db`
4. Re-run startup and processing measurements on larger inputs once the real Rust processor implementation exists
5. Design the Rust processor port as an explicit checklist based on the current Python pipeline:
   - POS tagging
   - Proper noun filtering
   - Lowercase normalization
   - Pre-lemmatization token validation
   - POS mapping for downstream behavior
   - Lemmatization
   - Proper-adjective capitalization heuristic
   - WordNet lexname gate for capitalized tokens
   - Post-lemmatization validation
   - Stopword filtering
   - Known-word filtering
   - Deduplication with first-occurrence retention and context mapping
6. Confirm whether any additional spike is needed to reduce or better characterize the remaining mismatch floor (`datasets/dataset`, `tagging/tag`) before the production port starts

