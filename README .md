# Data Fidelity Register (DFR) Specification

A machine-readable, cryptographically verifiable format in which an organisation publishes facts about itself, each bound to a cited public source, such that any independent party can re-verify the register **without trusting the organisation, or trusting whoever compiled the record**.

**Current version:** [v0.1 (draft)](dfr-specification-v0.1.md)

---

## The problem

Facts about an organisation reach the public through machines: search engines, assistants, language models, directories, procurement systems, data vendors. The answers they return are assembled from whatever they found, and what they found is usually not the organisation's own record.

Three failures follow, and an organisation can currently correct none of them:

- **Substitution.** A machine cites a third party. The figure may be stale, approximate, or wrong, and the organisation's own source is nowhere in the answer.
- **Silent drift.** Figures change. A machine that captured one two years ago has no way to know it has moved.
- **No way to check.** Nothing binds a quoted value to the document it came from.

Underneath all three: there is no machine-readable record of an organisation's own facts that a third party can verify without trusting someone.

## What DFR does

Each fact is **bound to a source**: an entry carries the URL of the public document the value came from, and the surrounding text that situates it.

Each fact is **verifiable by anyone**: every entry is sealed with a SHA-256 hash over its content and its source, using [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) canonicalisation. The seals in a release are committed to with an [RFC 6962](https://www.rfc-editor.org/rfc/rfc6962) Merkle root. That commitment, the entity, the chain to the prior release, and the hashes of every published file are bound into a signed **release digest**, which is anchored in a public transparency log.

Anyone can recompute all of it from the published files, with open standards and open-source code.

## What DFR does not do

**A DFR attests fidelity to a cited source, not the veracity of that source.**

The comparison is a certificate authority: a CA attests that a key belongs to a domain, not that the domain is trustworthy. A publisher can seal a faithful record of a false statement. The seal will verify, and the statement will still be false.

This is deliberate, and it is the format's central honesty. See §3 and §7 (Non-goals) of the specification.

## Verifying a register

The reference verifier lives in [`data-fidelity-register/verifier`](../verifier) and is published under the MIT licence.

```
python verify_register.py https://ledger.example.org
```

## Status

v0.1 is a draft. It is implemented by [Apparat](https://derappar.at), which is its first implementation, and the specification is maintained separately from it so that adopters publish *in the DFR format* rather than in a vendor's format.

Nothing in the specification requires a builder. An entity can produce, sign and publish a conformant register using only the primitives specified here and the reference verifier.

## Licence

The specification text is licensed **CC BY 4.0**. See [LICENSE](LICENSE).

The reference verifier is licensed **MIT**.

Editor: Thomas Meister.
