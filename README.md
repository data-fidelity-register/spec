# Data Fidelity Register: Specification

This repository holds the open specification for the **Data Fidelity Register
(DFR)**: a structured, machine-readable record of facts an organisation has
publicly disclosed, where each fact is bound to its public source and
cryptographically sealed so that the record can be verified by anyone, without
trusting its publisher.

- **Current version:** [`dfr-specification-v0.2.md`](dfr-specification-v0.2.md) (v0.2)
- **Previous version:** [`dfr-specification-v0.1.md`](dfr-specification-v0.1.md)
- **Licence:** CC BY 4.0
- **Reference verifier:** [data-fidelity-register/verifier](https://github.com/data-fidelity-register/verifier) (MIT)

A Data Fidelity Register attests **fidelity, not veracity**: it proves that a
recorded value faithfully reflects the source cited beside it and has not changed
since it was sealed. It does not attest that the source itself is true. This
boundary is the core of the design and is stated throughout the specification.

## What the specification defines

The specification is self-contained; the summary below is orientation, not a
substitute for reading it.

- **The entry model.** Each entry is a single sourced fact carrying six
  substantive fields: `label`, `value`, `unit`, `time_period`, `context`
  (a verbatim quote from the source) and `source_url`. Nullable fields (`unit`,
  `time_period`) are always present as literal JSON `null`.

- **The entry seal.** A SHA-256 hash computed over those six fields, and only
  those six, in a deterministic canonical form (keys in fixed alphabetical order,
  compact separators, raw UTF-8, literal `null` for absent nullable fields). Any
  change to any sealed field produces a different seal. Management and lifecycle
  fields that surround an entry are deliberately **not** sealed, so ordinary
  release-to-release changes do not break entry seals.

- **The release commitment.** All entry seals in a release are combined into a
  single Merkle root (RFC 6962 construction over the seals, sorted), published as
  `release_commitment` in `release.json`. This binds the whole release to one
  value.

- **Anchoring.** The signed release commitment is submitted to a public
  transparency log (Sigstore Rekor), giving third-party-verifiable evidence that
  the release existed, independent of the publisher.

- **Verification procedure, threat model, lifecycle, key compromise, and
  freshness limitations** are specified explicitly, including the honest limit
  that a passing verification proves integrity, not currency.

## Conformance vectors

The [`conformance/`](conformance/) directory contains test vectors validated
byte-for-byte against production registers:

- `entry-vectors.json`: canonicalisation and entry-seal cases
- `merkle-vectors.json`: release-commitment (Merkle root) cases
- `invalid-vectors.json`: cases a conforming verifier must reject

## Relationship to SCITT (RFC 9943)

The DFR is **architecturally aligned with, but not conformant to**, the IETF
SCITT architecture (RFC 9943). Both draw the same boundary, a signed, logged
statement is proven *recorded*, not proven *true*, but the DFR uses a JSON
representation and Rekor receipts rather than SCITT's COSE message and receipt
model. The specification's appendix sets out the alignment in detail. The DFR is
not a SCITT implementation and does not claim to be.

## Status and governance

This is an open **specification**, currently version 0.2, not a ratified
standard. It has one reference implementation (the register-producing engine
operated by Apparat / Der Apparat SASU) and one independent reference verifier.
The format and the verifier are open so that anyone can read the format and check
a register without depending on Apparat. Versions are published here as tagged
releases; the version in a register's `release.json` (`spec_version`) states which
version it conforms to.
