# The Data Fidelity Register

## Specification, version 0.2

Status: draft for the version 0.2 release.
License: this specification is published under CC BY 4.0. The reference verifier
is published separately under the MIT license.

This specification defines the Data Fidelity Register (DFR): an open format for
publishing verifiable, sourced facts about an organization in a form that both
people and automated systems can consume and independently check. It describes
how an entry is sealed, how a release commits to a set of entries and is anchored
in a public transparency log, how the register evolves over time, and how it
relates to adjacent standards. A conforming register can be produced and
verified by independent parties without trusting the register's operator.

## What this is, in brief

Der Apparat is a Paris-based company that publishes verifiable, sourced facts about
organizations in a form that both people and automated systems (search engines, AI
assistants, autonomous agents) can read and independently check. It extracts facts
from an organization's public documents, seals each fact cryptographically, commits
a set of facts into a release, and anchors that release in a public transparency
log. The result is a machine-readable register of an organization's facts that
anyone can verify has not been altered since it was published.

The Data Fidelity Register (DFR) is the open format that makes this possible. It is
what this document specifies. Its central promise is deliberately narrow: it attests
that each published entry faithfully reflects the public source it cites (fidelity),
not that the source itself is true (veracity). That boundary is what makes the format
safe to operate and trustworthy to rely on. The specification below defines exactly
how an entry is sealed, how a release is committed and anchored, how the register
evolves over time, and how an independent party can verify all of it without trusting
the register's operator.

## Contents

- [Introduction](#introduction)
- [Core model](#core-model)
- [Deterministic derivation](#deterministic-derivation)
  - [The sealed fields](#the-sealed-fields)
  - [Canonicalization](#canonicalization)
  - [The entry seal](#the-entry-seal)
  - [The release commitment](#the-release-commitment)
  - [What is signed and anchored](#what-is-signed-and-anchored)
  - [Note on the canonicalization scheme](#note-on-the-canonicalization-scheme)
- [Verification procedure](#verification-procedure)
- [Build provenance](#build-provenance)
  - [Principle: seal what you assert, record what you did](#principle-seal-what-you-assert-record-what-you-did)
  - [The `build_provenance` block](#the-build_provenance-block)
  - [Why record it](#why-record-it)
  - [Model change is a recorded event, not an automatic one](#model-change-is-a-recorded-event-not-an-automatic-one)
  - [Model migration procedure](#model-migration-procedure)
  - [Periodic review](#periodic-review)
- [Freshness and lifecycle](#freshness-and-lifecycle)
- [Security considerations](#security-considerations)
  - [Threat model](#threat-model)
  - [What the register does and does not attest](#what-the-register-does-and-does-not-attest)
  - [Threat: silent alteration of a published entry](#threat-silent-alteration-of-a-published-entry)
  - [Threat: content-layer tampering at the edge (observed)](#threat-content-layer-tampering-at-the-edge-observed)
  - [Threat: compromise of the signing key](#threat-compromise-of-the-signing-key)
  - [Threat: misreading provenance as truth](#threat-misreading-provenance-as-truth)
  - [Non-goals](#non-goals)
- [Revocation and compromise](#revocation-and-compromise)
  - [Entry-level revocation](#entry-level-revocation)
  - [Key compromise](#key-compromise)
  - [What revocation cannot do](#what-revocation-cannot-do)
- [Data protection and the immutability of the register](#data-protection-and-the-immutability-of-the-register)
  - [Design posture: data minimization](#design-posture-data-minimization)
  - [Lawful basis and professional-capacity data](#lawful-basis-and-professional-capacity-data)
  - [Erasure and supersession](#erasure-and-supersession)
  - [Summary](#summary)
- [Appendix: schemas and a worked example](#appendix-schemas-and-a-worked-example)
  - [Entry object](#entry-object)
  - [Release object](#release-object)
  - [Worked example (test vector)](#worked-example-test-vector)
- [Appendix: relationship to SCITT (RFC 9943)](#appendix-relationship-to-scitt-rfc-9943)
  - [Shared boundary: transparency attests registration, not truth](#shared-boundary-transparency-attests-registration-not-truth)
  - [Terminology map](#terminology-map)
  - [Compatibility position: aligned, not conformant](#compatibility-position-aligned-not-conformant)

## Introduction

The Data Fidelity Register makes one promise, and states its limits plainly. It
attests fidelity, not veracity: that each published entry faithfully reflects the
public source it cites, sealed and anchored so that any later alteration is
detectable, and that anyone can verify this independently. It does not attest
that the cited source is true. This boundary is deliberate and runs through the
entire specification: every mechanism below concerns the integrity and
verifiability of the record, not the correctness of the underlying facts, whose
truth remains the responsibility of the sources the register cites.

This boundary is also what makes the register safe to operate and useful to
rely on. A register operator does not adjudicate truth, audit methodology, or
substitute for the accountable parties who originally published a fact. It
republishes an already-public fact in a structured, sealed, citable form, with a
link back to the source, so that a reader, or an automated system representing the
organization, can retrieve the fact accurately and confirm it has not been
altered. The value is in reducing the approximation and drift that occur when
machines assemble facts about an organization from scattered or contested
sources, not in asserting authority the register does not have.

This specification is designed for facts about organizations, drawn from their
public disclosures and official records: figures from financial filings, identifiers
from public registries, and comparable facts that an organization or an accountable
third party has already published elsewhere. The cryptographic mechanisms it defines
are general and do not depend on this domain, but the six-field entry model, the
fidelity boundary, and the worked examples throughout all reflect that intended use.
The fidelity boundary in particular is a natural fit for this domain: because these
facts are already published by accountable parties, the register's role is to
republish them faithfully and verifiably, not to originate or adjudicate them.

The key words MUST, MUST NOT, REQUIRED, SHALL, SHOULD, SHOULD NOT, MAY, and
RECOMMENDED in this document are to be interpreted as described in RFC 2119 and
RFC 8174 when they appear in capitals.

## Core model

A register is built from three nested objects: entries, releases, and anchors.

An entry is a single sourced fact. Each entry carries six substantive fields that
constitute the claim it makes: a label (the metric or claim), a value, a context
that disambiguates the value, a source_url pointing to the public source the entry
reflects, an optional unit, and an optional time_period. These six fields, and
only these six, are sealed. An entry also carries management and lifecycle fields
(identifiers, approval and status information, publication dates, and the seal and
signature themselves), which are deliberately not sealed, because they legitimately
change over an entry's life without the underlying claim changing. The principle
throughout the specification is to seal what the register asserts and to record,
without sealing, the administrative state around it.

The entry seal is a SHA-256 hash computed over the six substantive fields, using
the deterministic derivation defined below, so that the same fields always produce
the same seal and any change to a sealed field produces a different one.

A release is a published set of entries at a point in time. A release commits to
the entry seals it contains by combining them into a single release commitment
using a Merkle tree, and it records the previous release's commitment, so that
releases form a chain. The release commitment, together with a fixed set of
release metadata, forms a release digest.

An anchor binds a release to public, append-only evidence. The release digest is
signed with the register operator's key, held in a hardware security module, and
submitted to a public transparency log (Sigstore Rekor). The resulting log entry
is the anchor: independent, timestamped, third-party evidence that the release
existed in this exact form at this time. Because the transparency log is
append-only, the operator cannot later alter or backdate a release without
detection.

The served register presents the current state. It is produced from the register's
full history by serving, for each entry, only its latest version, and only where
that version has not been retired. The full history, including superseded and
retired entries, remains in the underlying record and in the chain of anchored
releases. This separation between what is served and what is historically attested
recurs throughout the specification: it is how the register stays current while
keeping an honest, tamper-evident account of its own past.

## Deterministic derivation

Independent verification depends on one property above all others: that the
derivation from an entry's fields to its seal, and from a set of seals to a
release commitment, is fully deterministic. Anyone who holds the same inputs and
follows this section MUST arrive at byte-identical results. A verifier that
computed a different hash from the same data would be worthless, so this section
specifies the derivation exactly, leaving nothing to implementation choice.

### The sealed fields

The seal is computed over exactly the six substantive fields introduced in the
core model, and no others: label, value, context, source_url, unit, and
time_period. The management and lifecycle fields that surround an entry are not
part of the seal, so that ordinary lifecycle changes do not alter it.

For the purpose of deterministic derivation, one rule about these fields is
essential: fields that do not apply to a given entry (for example a unit for a
non-numeric fact) are represented as explicit null rather than omitted, so that
presence and absence are themselves deterministic. The required fields (label,
value, context, source_url) MUST be present as non-null strings; the nullable
fields (unit, time_period) MUST be present as literal null when they do not
apply, and MUST NOT be omitted.

### Canonicalization

Before hashing, the six fields are assembled into a single JSON object and
serialized deterministically. The scheme removes every representational degree of
freedom that would otherwise let the same data produce different bytes:

- Keys appear in a fixed order: the six field names in alphabetical order
  (context, label, source_url, time_period, unit, value).
- The object is serialized compactly, with no insignificant whitespace between
  tokens.
- Strings are emitted as raw UTF-8. Non-ASCII characters MUST appear as their
  raw UTF-8 bytes, not as `\uXXXX` escape sequences, because escaping would change
  the bytes and therefore the hash. Standard JSON escaping applies only to the
  characters JSON requires to be escaped (such as quotation marks and
  backslashes). The worked example in the appendix demonstrates this on an
  accented character.
- Required fields (context, label, source_url, value) are always present as
  non-null strings; an implementation MUST reject an entry whose required field
  is null or missing.
- Nullable fields (time_period, unit) are always present, as a literal JSON null
  when they do not apply, never omitted. An undefined value MUST be coerced to
  an explicit null before serialization, because a serializer that drops the key
  would produce a shorter object and a different hash. The string "null" MUST be
  rejected and never treated as a real null.

Two implementations that assemble these six fields in this order, apply these
rules, and serialize compactly produce the identical byte sequence, which is the
precondition for identical hashes. This scheme is consistent with RFC 8785 (JSON
Canonicalization Scheme) for the restricted shape of object used here (a flat
object of string-or-null values with fixed keys); an implementer MAY use an RFC
8785 serializer, but the normative requirement is the byte result described
above, not the use of any particular library.

### The entry seal

The seal is the SHA-256 hash of the canonicalized six-field object, expressed as
lowercase hexadecimal. SHA-256 is the single hash function used throughout;
there is no negotiation of algorithm, and no other digest appears in the
derivation.

### The release commitment

A release commits to the set of entry seals it contains. The seals are combined
into a single commitment using a Merkle tree constructed according to RFC 6962
(the Certificate Transparency Merkle tree definition), and the commitment is the
resulting Merkle tree head. RFC 6962 fixes the two details that otherwise vary
between Merkle implementations and would break reproducibility: the leaf and
interior node prefixes that prevent second-preimage ambiguity, and the handling
of trees whose leaf count is not a power of two. Using a specified,
widely-implemented Merkle definition rather than an ad hoc one means an
independent verifier can reproduce the commitment with an existing library.

The entry seals are sorted lexicographically by their hexadecimal value before
being placed into the Merkle tree, so the ordering is derived from the seals
themselves and does not depend on the order in which entries happen to be stored
or served. A verifier collects the entry seals, sorts them by the same rule,
recomputes the tree, and confirms the head matches the published commitment. This
means the commitment is reproducible from the set of seals alone, with no
additional ordering information needing to be trusted.

### What is signed and anchored

The signature and the transparency-log anchor are applied to a release digest,
not to each entry individually. The digest is derived from a fixed set of release
fields: the company identifier, the file hashes of the published artifacts (with
their keys sorted), the generation timestamp, the previous release commitment,
the current release commitment, and the entry count. Fixing this composition
means the digest is reproducible: a verifier assembles the same fields from the
published release, in the same way, and confirms both that the digest matches the
signature and that it appears in the transparency log. This keeps the chain of
derivation unbroken from the six fields of a single entry all the way to the
public anchor, with every step reproducible from published data.

### Note on the canonicalization scheme

The canonicalization above is defined directly, rather than by reference to an
external library, because the register's serialization was validated against RFC
8785 and confirmed to produce equivalent bytes for the restricted object shape
used here. Defining the byte-level result explicitly, and treating RFC 8785 as an
aligned reference rather than a dependency, means an implementer can reproduce the
seal with any conforming serializer and does not need to trust a particular
library. The value of a shared, specified scheme is precisely that independent
parties need not trust each other's implementation to arrive at the same bytes.
## Verification procedure

Derivation and verification are mirror images: derivation produces a seal, a
commitment, and an anchor from the data; verification recomputes each and
confirms it matches what was published. This section states verification as an
explicit procedure, because the register's guarantee is only as strong as the
independent check that can be performed against it. A conforming verifier
performs the following steps, and reports PASS only if all of them succeed.

1. Fetch the published register. Retrieve the served entries and the release
   object. When verifying a served HTML page, the verifier fetches the page as
   served, not an origin file, so that any alteration introduced between origin
   and consumer is within the scope of the check. Redirects are not followed: a
   resource that does not exist at its stated path is a failure, not an occasion
   to accept a redirected substitute, because following redirects would allow a
   served page to pass by pointing the verifier at different content.

2. Recompute each entry seal. For each entry, assemble its six substantive fields,
   apply the canonicalization defined above, compute the SHA-256 hash, and confirm
   it equals the entry's published seal. Any mismatch means the entry has been
   altered since sealing.

3. Recompute the release commitment. Collect the verified entry seals, sort them
   lexicographically by hexadecimal value, construct the RFC 6962 Merkle tree over
   them, and confirm the resulting head equals the published release commitment.

4. Recompute the release digest. Assemble the fixed set of release fields (the
   company identifier, the file hashes with keys sorted, the generation timestamp,
   the previous release commitment, the current release commitment, and the entry
   count), derive the release digest as specified, and confirm it matches the
   value that was signed.

5. Verify the signature. Confirm that the signature over the release digest
   validates against the operator's published public key, and that the public key
   is the one identified in the release. This establishes that the release digest
   was produced by the holder of the signing key.

6. Confirm the anchor. Confirm that the signed release digest is present in the
   public transparency log (Sigstore Rekor) at the referenced entry, and that the
   logged entry is consistent with the release. This establishes that the release
   existed in this exact form at the logged time, independently of the operator.

A verifier that completes all six steps has established, without trusting the
register operator, that every served entry is unaltered since it was sealed, that
the release commits to exactly those entries, and that the commitment was publicly
anchored at the stated time. A failure at any step MUST be reported as a failure
of the whole, identifying the step, rather than downgraded to a warning: partial
verification is not verification.

## Build provenance

### Principle: seal what you assert, record what you did

A register makes exactly one cryptographically sealed claim: that each entry
faithfully reflects the public source it cites. That claim, and only that claim,
is what the release commitment protects. Everything describing *how* and *when*
the register was produced, the models used, the generation timestamp, the
transparency-log anchor, is recorded in the release metadata but is not part of
the sealed commitment.

This line is deliberate. Sealing is reserved for the assertion that needs to be
tamper-evident (the facts and their sources). The build process has no adversary:
no party gains by forging which extraction model was used, and no verifier's
trust depends on that value being unforgeable. Recording it serves transparency
and operational hygiene, not integrity. Sealing it would also bind the build
tooling to the release identity, so that changing a model version would force a
new commitment even when no fact changed, which is incorrect: the facts did not
change, so their commitment must not.

Seal what you assert. Record what you did.

### The `build_provenance` block

A conforming release SHOULD include a `build_provenance` object in `release.json`,
recorded alongside the `anchor` block (that is, in the metadata tier, outside the
sealed commitment). It documents the tooling that produced the register:

```json
"build_provenance": {
  "extraction_model": "gemini-3.5-flash",
  "verification_model": "claude-sonnet-4-6",
  "generator_version": "apparat-bridge@<git-sha>"
}
```

Fields:

- `extraction_model` (string, RECOMMENDED): the model identifier used to extract
  atomic facts from source documents.
- `verification_model` (string, RECOMMENDED): the model identifier used to
  independently audit the extracted facts. A conforming two-engine pipeline uses
  a different model here than for extraction, so that a single model's error
  cannot both introduce and confirm a fact.
- `generator_version` (string, OPTIONAL): an identifier for the generator build
  itself (for example, the git commit of the generator script), so a release can
  be traced to the exact tooling that produced it.

Implementations MAY record the resolved model version returned by the provider
at call time, in addition to the requested identifier, where the provider exposes
it. Model identifiers that are stable aliases (for example `gemini-3.5-flash`)
name a channel, not a frozen build; recording the requested identifier is
sufficient for provenance, while capturing any provider-resolved version improves
reproducibility.

### Why record it

Recording the build models serves two purposes beyond transparency:

1. It makes the register auditable in a dimension buyers increasingly ask about:
   exactly how the facts were produced, not merely that they are sealed.
2. It makes model drift visible. A pinned stable model identifier keeps working
   long after newer models ship, so a pipeline can silently run an outdated model
   without any error. Recording the model in every release turns that invisible
   drift into a legible line that a periodic review can check against the
   provider's current models and deprecation schedule.

### Model change is a recorded event, not an automatic one

A verification product favours reproducibility: releases SHOULD pin explicit
stable model identifiers rather than moving aliases (such as `*-latest`), so that
the model does not change without the operator's knowledge. Migrating to a newer
model is therefore a deliberate act: the operator evaluates the new model,
migrates, and records the change simply by producing new releases whose
`build_provenance` names the new model. Prior releases retain their original
record. The register thus carries an honest history of the tooling that produced
each release, in the same spirit as the freshness fields carry the history of
what was true when.

### Model migration procedure

Model identifiers are pinned in two places that must stay in agreement: the
engine constants (`GEMINI_MODEL`, `CLAUDE_MODEL` in the Cloud Run service) and
the generator's mirrored constants (`EXTRACTION_MODEL_`, `VERIFICATION_MODEL_`
in the release generator). They are mirrored deliberately rather than shared
from one source, because the two runtimes have no common config surface and the
values change rarely and deliberately. Keeping them in step is therefore a
process, not a plumbing problem.

Migrating a model is a single deliberate act with these steps:

1. Trigger. A migration is prompted either by an announcement (a provider ships
   a newer or cheaper model in the relevant tier) or by the periodic review (see
   below). It is never automatic.
2. Evaluate. Run a test extraction with the candidate model on representative
   source documents. Because a different model independently verifies extraction,
   a regression is caught by the existing two-engine audit rather than shipping
   silently. Compare the audited output against the current model's.
3. Update both constants in the same change. Edit the engine constant and the
   generator constant together, so no release is ever produced with the two out
   of step. Deploy the engine; save the generator.
4. Record, don't rewrite. New releases record the new model in
   `build_provenance`. Prior releases keep their original record. The register
   thus carries an honest history of which model produced each release; no past
   release is restated.

### Periodic review

Model staleness is reviewed on two triggers:

- Announcement-triggered: when a provider ships a new model in a tier the
  pipeline uses, that announcement is itself a review prompt, not merely news.
  This is where migration decisions are actually made.
- Calendar backstop: a standing six-month review, tracked alongside other dated
  operational obligations. Six months matches the roughly twice-yearly rhythm of
  deliberate model change; a shorter interval mostly confirms "still current" and
  trains the review to be skipped.

At each review, read the model recorded in recent releases' `build_provenance`
and compare it against the provider's current models and published deprecation
schedule. The recorded field is what makes this a one-line check rather than an
archaeology exercise: staleness is visible in the release record, not buried in
the build tooling.
## Freshness and lifecycle

Facts change over time, and a register that only ever presented a static snapshot
would decay into inaccuracy. The DFR therefore models an entry's lifecycle
explicitly, while keeping the common cases simple.

Three kinds of change are distinguished, because conflating them is a frequent
source of error:

- A new period. Most changes are not changes to an existing fact at all, but new
  facts for a new period. A revenue figure for one financial year and the figure
  for the next are both permanently true; they coexist, distinguished by their
  time_period, and neither supersedes the other. This is the ordinary case and
  requires no lifecycle machinery beyond the time_period field.
- A correction. The same fact, for the same period, takes a new value because the
  source restated it or because an earlier entry misread the source. The prior
  value is replaced and marked as corrected. This is comparatively rare.
- A supersession. A current-state fact with no natural period, such as a current
  registration code, takes a new value that replaces the old. The prior value is
  marked superseded.

An entry therefore carries lifecycle fields in addition to its sealed claim: a
status drawn from a small vocabulary (current, superseded, corrected), a
validFrom indicating when the entry became the current value, and, where an entry
replaces a specific prior entry, a supersedes reference to it. These fields are
lifecycle metadata and are not part of the seal, consistent with the core model:
the claim is sealed, its lifecycle state is recorded.

Whether the history of a fact is published alongside its current value, or only
the current value is served while history remains in the anchored record, is an
editorial decision that depends on whether the history is informative or merely
noise for a given fact. This specification defines the lifecycle fields and their
meaning; it does not mandate a single history-serving policy, and the detailed
mechanism for presenting superseded history is expected to be refined against
real-world use before it is fixed normatively.

## Security considerations

The Data Fidelity Register makes one security-relevant promise: that a published
entry can be verified, by anyone, to be the entry that was sealed and anchored,
unaltered since. This section states the threats to that promise, what the design
does about each, and, importantly, the threats it does not defend against,
because a verification standard that overstates its guarantees is worse than one
that draws its boundaries honestly.

### Threat model

The security properties below are best read against an explicit model of what is
being protected, from whom, and under what assumptions.

Assets. The protected asset is the integrity and verifiability of the record: the
guarantee that a published entry is the entry that was sealed, that a release is
the set of entries that was committed, and that the commitment was anchored at the
stated time. The truth of the underlying facts is explicitly not an asset this
system protects.

Adversaries. The model considers three: an external party who alters a served
page after it leaves the origin (for example a compromised or misconfigured
content-delivery layer); a party who obtains the register operator's signing key;
and the register operator itself, which the design constrains so that a consumer
need not simply trust it. The last is the point of anchoring to a public log: the
operator cannot silently rewrite or backdate history.

Trust assumptions. Verification relies on three assumptions, and no more: that
SHA-256 and the ECDSA signature scheme used are not broken; that the public
transparency log (Sigstore Rekor) provides an append-only, publicly auditable
history; and that a verifier can obtain the operator's public key through a
channel it trusts (the key is published at a stable, verifiable location, and its
compromise is handled by the revocation and compromise section). Notably,
verification does not require trusting the register operator's honesty, only the
cryptographic primitives and the public log. This is what lets an independent
party verify a register without any relationship to its operator.

### What the register does and does not attest

The register attests fidelity, not veracity: that each entry faithfully reflects
the public source it cites, not that the source is true. Every threat below is
therefore about the integrity of the *record* and its *verifiability*, not about
the correctness of the underlying facts. A reader who treats a passing
verification as proof that a claim is true has misread the guarantee.

### Threat: silent alteration of a published entry

The primary threat is that a published fact is changed after anchoring, a value
edited, a source swapped, while the page continues to present itself as
authoritative.

Mitigation. Each entry is sealed over its substantive fields; the seals are
combined into a release commitment; the commitment is signed with a key held in
a hardware security module and anchored in a public transparency log (Sigstore
Rekor). Any alteration changes the entry's seal, which changes the commitment,
which no longer matches the signed, publicly logged anchor. The reference
verifier performs this check independently, so detection does not depend on
trusting the register operator. The append-only transparency log means the
operator cannot quietly withdraw or backdate a past commitment either.

### Threat: content-layer tampering at the edge (observed)

This is not hypothetical. A register's pages can be altered *after* they leave
the origin, by the content-delivery network or reverse proxy that serves them,
without the origin file changing. In deployment we observed three distinct
instances of this class:

- A CDN "email obfuscation" feature rewrote an email address inside a sealed
  page, changing the served bytes and therefore breaking the seal against the
  origin content.
- A bot-mitigation feature injected a script into served pages.
- A client zone injected a real-user-monitoring beacon into every page.

Each of these silently modifies what a consumer actually receives, even though
the file the register produced is unchanged. For a hash-attested page this is
precisely the failure that verification must catch, and it did: the verifier,
fetching the served page and recomputing the seal, flagged the mismatch. The
edge had falsified the attested page, and the check surfaced it.

Mitigation and deployment requirement. Registers MUST be served with all
edge-side HTML rewriting disabled, no email obfuscation, no injected scripts,
no analytics beacons on the register's paths. A conforming deployment verifies
this by fetching the *served* page (not the origin file) and confirming the seal
still holds; a diff of served-versus-origin surfaces any edge rewriting. Where a
register is hosted on a client's own zone whose settings are outside the
operator's control, the register SHOULD additionally be verifiable at a
direct-origin URL (for example the underlying platform host), so that register
integrity can be checked independently of client-zone configuration. This
turns edge tampering from a silent corruption into a detected, attributable
condition.

### Threat: compromise of the signing key

If the register's signing key were compromised, an attacker could produce
validly signed commitments for altered content.

Mitigation. The signing key is held in a cloud hardware security module and is
not exportable; signing happens through the HSM rather than with key material
present in application code or configuration. This does not make compromise
impossible, but it removes the most common exposure (a key sitting in a file or
environment variable). Key compromise and rotation are handled by the revocation
and compromise section below, together with the transparency log's role in
bounding the window and scope of any misuse: because every legitimate commitment
is publicly logged, a divergent history is detectable.

### Threat: misreading provenance as truth

A subtler risk is not a technical attack but a category error: a consumer, or an
AI system, treats a verified register entry as a verified *fact* about the world.
The register's own framing must resist this, because the same property that makes
it trustworthy (it says only what it can prove) is undermined if it is presented
as proving more.

Mitigation. The register states its fidelity boundary explicitly in its
human- and machine-readable surfaces, and the reference verifier reports what it
checked (seal integrity, commitment, anchor) without asserting anything about the
truth of the underlying claims. This is the same boundary the transparency-log
standards draw for registration receipts: proof of what was recorded, not proof
that the recorded statement is true.

### Non-goals

The register does not defend against, and does not claim to: the truthfulness of
cited sources; suppression or non-publication of a fact (it attests what is
registered, not what is omitted); or an entity publishing a register of
misleading-but-accurately-transcribed claims. These are outside the fidelity
guarantee by design. Defending the boundary honestly is itself a security
property: it prevents the register's cryptographic assurances from being
mistaken for assurances they do not provide.
## Revocation and compromise

Two different things can need to be undone in a register: a single entry may need
to be withdrawn, or the signing key itself may be compromised. These are separate
problems with separate procedures, and conflating them is a common mistake. This
section defines both, and states honestly what each can and cannot achieve given
that the register anchors to an append-only public log.

A guiding constraint applies throughout: nothing can un-anchor what was anchored.
The transparency log is append-only by design, which is what makes it
trustworthy. Every procedure below therefore operates on what the register
*serves* going forward and on how a consumer *interprets* past anchors, never on
erasing history. Revocation in this register means "cease to vouch for," not
"make it as though it never happened."

### Entry-level revocation

An individual entry may need to be withdrawn: a source is retracted, a fact is
found to have been mis-transcribed, or a lawful request requires it to stop being
served.

Procedure. The entry is marked retired in the vault. The served register is
produced from a query that returns, per entry, only the latest version and only
where that version is not retired, so the next release no longer serves the
withdrawn entry, and its seal no longer contributes to the new release
commitment. Prior releases and their anchors are unaffected: an old release,
verified against its own commitment, still contains the entry, because that is a
true record of what was registered at that time. What changes is only what the
register serves and vouches for from the retirement forward.

This is the same mechanism the freshness model uses for supersession and the data
protection section uses for erasure. Entry-level revocation is therefore not a
special capability but an application of the register's normal lifecycle: the
served register always reflects the current, vouched-for state, while the log
preserves the history.

Where a retirement corrects an error rather than reflecting a source change, the
entry SHOULD be marked with a status that distinguishes correction from ordinary
supersession, so a reader can tell "this was withdrawn because it was wrong" from
"this was replaced by a newer value."

### Key compromise

The more serious case is compromise of the signing key, which would let an
attacker produce validly signed commitments for content the operator never
approved.

Exposure is limited by design. The key is held in a cloud hardware security
module and is used for signing through the module rather than being present in
application code, configuration, or environment. This does not make compromise
impossible, but it removes the most common cause: a key sitting in a file or
variable that leaks.

Procedure on suspected compromise:

1. Rotate. A new signing key is generated in the hardware security module and
   the public key published at the register's key endpoint is updated. All
   subsequent releases are signed with the new key.
2. Publish a revocation statement. The register publishes, at a well-known
   location, a signed statement identifying the compromised key by its
   fingerprint and the time from which it should no longer be trusted. Because
   the public key endpoint and the register's own facts are themselves part of
   the record, this statement is verifiable.
3. Re-anchor current state under the new key. The current register is re-released
   and re-anchored, so that a consumer verifying present state does so against a
   commitment signed by the uncompromised key.

What the transparency log gives here is the ability to bound the damage. Every
legitimate commitment the operator ever made is publicly logged in order. A
consumer, or an auditor, can therefore distinguish commitments that appear in the
log's genuine history from any an attacker produced out of band, and can
establish the time window in which the compromised key was valid. The log does
not prevent a compromised-key signature from existing, but it makes the
legitimate history externally checkable, which is what lets a revocation
statement be trusted rather than merely asserted.

### What revocation cannot do

Revocation cannot retract a past anchor, and does not try to. An entry that was
registered and anchored remains, in the log, a true statement that it was
registered at that time. If that entry was later found to be wrong, the honest
record is precisely "this was registered, and later corrected or withdrawn," not
a rewritten history in which it never appeared. This is a deliberate property:
the same append-only log that makes the register tamper-evident also means the
register keeps an honest account of its own corrections. A consumer who wants the
current, vouched-for state reads the served register; a consumer who wants the
full history, including what was later revoked, reads the log.
## Data protection and the immutability of the register

A register is an append-only, sealed, and externally anchored record. That
permanence is the point: a reader must be able to verify that an entry has not
been altered since it was anchored. Permanence and the data-protection right to
erasure are in evident tension, and this section states how the Data Fidelity
Register is designed so that the tension rarely arises and, where it does, has a
defined resolution.

### Design posture: data minimization

The register is an instrument for verifiable company facts drawn from official
published sources: financial figures, regulatory identifiers, certifications,
operational policies. It is not a personal-data store and is not designed to
profile individuals. The governing rule is minimization: a register carries
personal data only where that data is already public official-record
information about a person acting in a professional capacity (for example, a
legal representative named in a public filing), only to the extent needed for
the company fact to be meaningful, and never as a standalone profile of the
individual. Where personal data is not needed for a company fact, it is not
registered. This is operating practice, not aspiration: personal data present
in early source material has been removed from a live register rather than
carried into it.

### Lawful basis and professional-capacity data

The limited personal data a register may contain is information a company has
itself published in an official source about a person in their professional
role. Its presence in the register reflects a legitimate interest in the
verifiability of company facts that AI systems will otherwise assemble from
unverified sources, balanced against the minimal and already-public nature of
the data. The register does not introduce personal data that was not already
public, and does not aggregate it into a profile beyond the single company fact
it supports.

### Erasure and supersession

Most change is handled by supersession rather than erasure. When a person's
professional relationship to a company ends, the fact that named them is
superseded by a newer fact from a newer official source; the register serves the
current state, and the superseded entry is marked accordingly rather than
presented as current. For the ordinary case this satisfies the practical concern
(the register does not present outdated personal associations as current)
without deleting a sealed historical record.

Where a valid erasure request concerns personal data that cannot be addressed by
supersession, the register's integrity model is designed to accommodate it. The
key distinction is between the served register and the historical anchor. A
release commitment attests what was registered at a point in time; it does not
oblige the register to serve that entry indefinitely. The intended resolution is
therefore to withdraw the entry from the served register (so it is no longer
presented as a current or historical fact to consumers) while the transparency
log continues to hold the earlier anchor as a truthful record that such an entry
was once registered. Withdrawal from the served layer does not, and cannot,
un-anchor what was previously anchored: an old release, verified against its own
commitment, still contains the entry. Erasure here therefore means ceasing to
serve and present the data, not rewriting history. This mirrors the distinction
the register already draws between the immutable commitment and the mutable
management state around it.

The serving layer supports this withdrawal today. The served register is produced
by a query that returns, per entry, only the latest version and only where that
version is not retired; marking an entry retired therefore removes it from the
next served release while leaving every prior anchor intact. Withdrawal of a
single entry is thus an existing capability, not a change the design would need.

Whether serve-layer withdrawal plus a persistent historical anchor is sufficient
to satisfy a given erasure obligation is a separate question, and one of law
rather than engineering: it is a matter for counsel in the relevant jurisdiction.
The register's contribution is to give counsel a clean, auditable mechanism to
work with, a clear separation between what is served and what is historically
attested, rather than a claim that the design is, by itself, legally sufficient.

### Summary

The register minimizes personal data by design, carries only already-public
professional-capacity data where a company fact requires it, handles the
common case through supersession, and resolves genuine erasure by withdrawing
the served entry without falsifying the historical record. Immutability applies
to the integrity of what was registered, not to an obligation to serve every
entry indefinitely.
## Appendix: schemas and a worked example

This appendix gives the JSON structure of the objects a register publishes and a
concrete worked example, so that an implementer can produce and verify a register
byte-for-byte rather than from prose alone.

### Entry object

Each entry in the served register (`ledger.json`) is a JSON object with the
following fields. Six of these are the sealed substantive fields; the remaining
two (`source_name` and `seal`) are carried for the reader and for verification
but are not part of the seal preimage.

```
{
  "label":       string,        // sealed. The metric or claim.
  "value":       string,        // sealed. The value, as a string.
  "unit":        string | null, // sealed. Unit or scale, or null.
  "time_period": string | null, // sealed. Period the value applies to, or null.
  "context":     string,        // sealed. Disambiguating context.
  "source_url":  string,        // sealed. URL of the public source.
  "source_name": string,        // not sealed. Human label for the source.
  "seal":        string         // not sealed. Lowercase-hex SHA-256 of the
                                // canonicalized six sealed fields.
}
```

The four required sealed fields (`label`, `value`, `context`, `source_url`) MUST
be present as non-null strings. The two nullable sealed fields (`unit`,
`time_period`) MUST be present, as a JSON string or as literal `null`, and MUST
NOT be omitted. The served register is a JSON array of these objects.

### Release object

A release (`release.json`) is a JSON object describing a published set of entries,
its commitment, and its anchor. Its fields are:

```
{
  "company_id":                  string,  // the register's subject organization
  "release_id":                  string,  // unique release identifier
  "generated_at":                string,  // ISO 8601 UTC timestamp
  "row_count":                   number,  // number of entries in the release
  "release_commitment":          string,  // hex Merkle root over the sorted seals
  "previous_release_commitment": string | null, // the prior release's commitment
  "anchor_status":               string,  // "anchored" or "anchor_pending"
  "anchor":                      object | null, // see below; null if pending
  "spec_version":                string,  // the DFR spec version
  "file_hashes":                 object,  // filename -> SHA-256 hex of each artifact
  "release_digest":              string,  // hex digest signed and anchored
  "signer":                      { "name": string, "key_id": string }
}
```

The `anchor` object, present when `anchor_status` is `"anchored"`, records the
transparency-log evidence:

```
{
  "method":                "sigstore-rekor",
  "signature_b64":         string,  // signature over the release digest
  "key_id":                string,  // fingerprint of the signing key
  "algorithm":             string,  // e.g. "EC_SIGN_P256_SHA256"
  "public_key_url":        string,  // where the public key is published
  "rekor_uuid":            string,  // transparency-log entry identifier
  "rekor_log_index":       number,
  "rekor_integrated_time": number,  // log inclusion time
  "rekor_log_id":          string,
  "rekor_entry_url":       string   // direct URL to the log entry
}
```

The `release_digest` is derived from the release fields as defined in the
deterministic derivation section (the company identifier, the file hashes with
keys sorted, the generation timestamp, the previous and current release
commitments, and the entry count). It is the value that is signed and whose
presence in the transparency log the anchor records. The releases form a chain
through `previous_release_commitment`, so that the sequence of a register's
releases is itself verifiable.

### Worked example (test vector)

The following is a real entry from a live register, with its exact canonical
preimage and resulting seal, so that an implementation can be checked against a
known-correct result. An implementation that does not reproduce this seal from
these fields is not conformant.

Sealed fields:

```
label:       Apparat's operating entity has a single shareholder
value:       Oui
context:     Associé unique : Oui
source_url:  https://data.inpi.fr/entreprises/105829188
unit:        (null)
time_period: 2026
```

Canonical preimage. The six fields are placed in alphabetical key order and
serialized compactly, with no whitespace between tokens, nulls as literal `null`,
and non-ASCII characters emitted as raw UTF-8 rather than escaped. For this entry
the preimage is exactly:

```
{"context":"Associé unique : Oui","label":"Apparat's operating entity has a single shareholder","source_url":"https://data.inpi.fr/entreprises/105829188","time_period":"2026","unit":null,"value":"Oui"}
```

Note the accented character in `context` appears as the raw UTF-8 character `é`,
not as an escaped `\u00e9`. This is significant: escaping non-ASCII characters
would change the bytes and therefore the seal, so a conforming implementation
MUST serialize raw UTF-8, not ASCII-escaped output.

Seal. The SHA-256 of the UTF-8 bytes of that preimage, in lowercase hexadecimal,
is:

```
8bc8c04caf29999a681b15683f4b8821b2d65cd32c104f605f9eb5aeec2c471b
```

which is the value published for this entry. An implementation that assembles the
six fields in alphabetical order, serializes them compactly as raw UTF-8 with the
null present, and computes SHA-256 will reproduce this seal exactly.

## Appendix: relationship to SCITT (RFC 9943)

The Supply Chain Integrity, Transparency, and Trust architecture (SCITT,
RFC 9943, Standards Track, June 2026) defines a general architecture for
single-issuer signed-statement transparency: an issuer signs a statement about
an artifact, registers it with a Transparency Service, and receives a receipt
proving the statement was recorded on an append-only ledger. The Data Fidelity
Register is a narrower, domain-specific instrument, but it sits in the same
family and shares SCITT's central discipline. This appendix maps the two and
states the compatibility position plainly.

### Shared boundary: transparency attests registration, not truth

SCITT and the DFR draw the same line, which is the most important point of
alignment. In SCITT's own terms, a valid receipt does not prove that a
statement's claim is true; it proves that a signed statement was registered and
that the receipt verifies under the relevant profile. The DFR's fidelity
principle is the same boundary stated for a different domain: a register attests
that each entry faithfully reflects its cited public source, not that the source
is true. Both systems make a claim about the record, not about the world. A
reader who over-reads either, treating a receipt or a seal as proof of truth
rather than proof of faithful registration, misunderstands both in the same
way.

### Terminology map

The DFR and SCITT name closely related things differently. The correspondence is
approximate, not exact, because the DFR predates alignment work and optimizes for
a different consumer (AI retrieval of company facts, rather than machine-to-
machine supply-chain verification).

- SCITT *statement* (signed content about an artifact) corresponds to a DFR
  *sealed entry* (a fact sealed over its six substantive fields).
- SCITT *artifact* (the thing a statement is about) corresponds to the DFR
  *cited public source* the entry reflects.
- SCITT *Transparency Service* (registers statements, enforces a policy,
  maintains the ledger) corresponds in function to the *transparency log* the
  DFR anchors into (Sigstore Rekor), though the DFR uses a general-purpose log
  rather than a domain-specific Transparency Service.
- SCITT *receipt* (proof a statement was registered) corresponds to the DFR
  *anchor record* (the Rekor inclusion proof for a release commitment).
- SCITT *ledger* (linear, irrevocable history) corresponds to the append-only
  transparency log plus the release chain (each release referencing the prior
  commitment).

### Compatibility position: aligned, not conformant

The DFR is structurally aligned with SCITT but is deliberately not a conformant
SCITT profile, and v0.2 does not claim conformance. Three differences make this
a considered position rather than an omission:

1. Encoding. SCITT statements and receipts are COSE/CBOR
   (`application/scitt-statement+cose`, `application/scitt-receipt+cose`). The
   DFR publishes JSON and JSON-LD, chosen because the register's primary
   consumers are AI retrieval systems and web crawlers that read JSON natively,
   not COSE verifiers. Adopting COSE would serve conformance at the cost of the
   consumer the register exists for.
2. Transparency Service. SCITT expects a Transparency Service that enforces a
   registration policy and issues COSE receipts. The DFR anchors into a
   general-purpose transparency log (Rekor) and verifies inclusion directly.
   This is functionally analogous but not a SCITT Transparency Service.
3. Scope. SCITT is a general supply-chain architecture; the DFR is a single
   domain (verifiable company facts for the AI era) with a fixed six-field seal
   and a fidelity semantics SCITT does not define.

The intent is interoperability of principle, not of wire format: a party who
understands SCITT will recognize the DFR's model immediately, and the shared
"transparency attests registration, not truth" boundary means the two compose
cleanly in a stack. A future DFR revision MAY define a conformant SCITT profile
(COSE-encoded entries, a Transparency Service binding) if a consumer requires
it; until such a consumer exists, JSON-first serving is the deliberate choice.
