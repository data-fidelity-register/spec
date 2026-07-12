# Data Fidelity Register (DFR) Specification

**Version:** 0.1 (draft)
**Date:** 2026-07-12
**Editor:** Thomas Meister (Der Apparat, SASU)
**First reference implementation:** Apparat
**Specification text licence:** CC BY 4.0
**Reference verifier licence:** MIT

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they appear in all capitals.

---

# Part I. Purpose and overview

## 1. The problem

Facts about an organisation reach the public through machines. A person asking what a company's headcount is, when it was founded, what its accreditation covers, or how much financing it has provided, will often ask a search engine, an assistant, or a language model. Business directories, procurement systems, financial data vendors, knowledge graphs and API consumers all do the same thing at scale. The answer they return is assembled from whatever they found, and what they found is usually not the organisation's own record.

This is not a new problem. Machine-mediated retrieval of corporate facts has been unreliable for as long as it has existed. What has changed is that the consequences are now immediate and visible: an answer is synthesised and presented as settled, rather than returned as a list of links a reader would evaluate. AI did not create this problem. It made it impossible to ignore.

Three failures follow, and an organisation can currently correct none of them.

**Substitution.** A machine answering a question about an organisation frequently cites a third party: a directory, an aggregator, a news article, a competitor's comparison page. The figure it returns may be stale, approximate, or wrong, and the organisation's own published source is nowhere in the answer.

**Silent drift.** Published figures change. Reports are superseded, certifications lapse, registrations are renewed. A machine that captured a figure two years ago has no way to know it has moved, and no way to tell that its copy is no longer what the organisation publishes.

**No way to check.** Even where a machine cites the organisation directly, nothing binds the value it quotes to the document that value came from. A number in a web page can be edited, and no reader, human or machine, can tell whether it is the number that was originally published.

Underneath all three lies a single absence. **There is no machine-readable record of an organisation's own facts that a third party can verify without trusting the organisation, or trusting whoever compiled the record.**

## 2. What a DFR is

A **Data Fidelity Register** is a set of facts an organisation publishes about itself, in which every fact is bound to the public source it came from, and every fact is cryptographically sealed so that any independent party can check it has not been altered since it was sealed.

The register is published on a domain the organisation controls, in formats machines read directly. It is a citable, verifiable, **publisher-provided source**: the organisation's own record, in a form that can be checked rather than merely believed.

Two properties do the work.

**Each fact is bound to a source.** An entry is not a bare value. It carries the URL of the public document the value came from, and the surrounding text that situates it, so that a value can be traced back to what was actually published.

**Each fact is verifiable by anyone.** Every entry is sealed with a cryptographic hash over its content and its source. The seals in a release are committed to with a single hash. That commitment, together with the release metadata, is signed and anchored in a public transparency log. Any party can recompute all of it from the published files, using open standards and open-source code, and confirm that what they are reading is what was sealed. **Neither the organisation nor the party that built the register has to be trusted.**

## 3. The fidelity principle

A DFR attests **fidelity to a cited source, not the veracity of that source.**

Each entry binds a value to a source URL. The seal proves that the value, as published, is the value that was sealed: that it has not been altered since sealing, and that the binding between value and source is intact. The seal makes no claim that the source is correct, that the organisation's statement is true, or that the record is complete. A publisher can seal a faithful record of a false statement. The seal will verify, and the statement will still be false.

This is deliberate, and it is the format's central honesty. The comparison is a certificate authority: a CA attests that a key belongs to a domain, not that the domain is trustworthy. A DFR attests that a value was published against a source, not that the source is right. Verifiability of provenance is a narrower claim than correctness of fact, and it is the only claim a format can honestly make about data it did not itself observe.

Everything else in this document is machinery in service of that principle. It lets anyone check fidelity, and it refrains from implying anything more.

## 4. Why a URL, and not the document

A DFR binds a fact to a **stable public citation**, not to a snapshot of the document that citation points to. This is the first question a technical reader asks, so it is answered here rather than later.

The alternative would be to hash the source document itself and to preserve every historical version of it, which is what content-addressable storage and web archives do. DFR does not do this, for three reasons. It is a different problem, already addressed by archival systems that DFR does not seek to replace. It imposes an obligation, namely storing and serving copies of every source, that most publishers cannot accept and some are not licensed to discharge. And it changes the claim: a register that stored its sources would be asserting something about *documents*, where DFR asserts something narrower and more defensible about *citations*.

The cost of this choice is real and is stated plainly. **A seal attests that a value was published against a given URL at the time of sealing. It attests nothing about the document served at that URL today.** If a source is revised or withdrawn, every seal continues to verify while pointing at a document that may no longer say what it said. Consumers for whom the current content of a source is material MUST fetch and read the source. See §17.

## 5. What a publisher publishes, and why

A DFR is delivered as a small set of files at stable paths on the entity's own domain. Each exists for a distinct reason.

| File | Audience | Purpose |
| :-- | :-- | :-- |
| `ledger.json` | Machines | **The canonical register.** The sealed facts. This is the source of truth. Everything else is derived from it or describes it. |
| `release.json` | Machines, auditors | **The proof.** The release commitment, the chain to the previous release, the signature, and the transparency-log anchor. |
| `ledger-jsonld.json` | Machines, general web | **The interpretable surface.** The same facts in Schema.org vocabulary, which generic systems parse without any knowledge of DFR. |
| `latest.md` | Humans | **The readable rendering.** A person following a citation into a register needs to be able to read it. |
| `llm.txt` | Machines | **The plain-language description.** Documentary prose stating what the register is, what it covers, and where the canonical files are. |

The division of labour matters, and it is the part most easily misunderstood.

**`ledger.json` is authoritative. The derived files are not.** JSON-LD makes the facts legible to any system that speaks Schema.org, which is most of them, but it carries no cryptographic binding of its own: Schema.org has no notion of a seal. The same is true of `latest.md` and `llm.txt`. They exist so that a register is *usable* by humans and by machines that will not implement a verifier.

This creates an obvious hazard. A publisher, or an attacker with write access, could leave `ledger.json` mathematically pristine and alter the derived files, so that everything verifies while the consumers who actually read the register are shown something else. **DFR closes this by bringing the derived files under the signature.** The digest of every published file is included in the signed release digest (§11), so a modified `latest.md` or `ledger-jsonld.json` is detectable by exactly the same verification that checks the seals. The derived files are not authoritative, but they are not unprotected either.

## 6. Roles

DFR distinguishes four roles. They may be held by one party or by several, and the specification is neutral between those arrangements. It is not neutral about *stating which is which*, because the obligations differ.

| Role | Responsibility |
| :-- | :-- |
| **Entity** | The organisation the facts are about. Controls the domain on which the register is published. |
| **Builder** | Produces the register: gathers the facts, seals the entries, computes the commitment. |
| **Signer** | Holds the signing key. Signs the release digest and submits it to the transparency log. **Carries the key-rotation obligation of §12.2.** |
| **Publisher** | Hosts the published files on the entity-controlled domain. |

Two arrangements are common. In **self-publication**, one organisation holds all four roles. In **service publication**, an entity engages a builder, who is typically also the signer, while the entity remains the publisher on its own domain. The reference implementation, Apparat, operates as builder and signer for entities that publish on their own domains.

An implementation MUST declare the signer in `release.json` (§11.3). A verifier MUST NOT infer that the entity signed a release, nor that the entity has reviewed or endorsed its contents, from the fact that the register is published on the entity's domain.

**What a signature establishes, and what it does not.** A valid signature establishes that the holder of the signing key produced the release. It does not, by itself, establish that the entity authorised that key. §13 defines an OPTIONAL delegation record by which an entity may make such authorisation explicit and verifiable. Where no delegation record is published, a verifier learns only that a given key signed a register that is hosted on the entity's domain, and the strength of that inference rests on the entity's control of its domain and nothing more.

## 7. Non-goals

DFR does not attempt to:

- **Certify that facts are true.** It attests fidelity to a cited source (§3).
- **Preserve historical versions of source documents.** It binds to citations, not to snapshots (§4). It does not replace web archives or content-addressable storage.
- **Prevent an organisation from publishing false, incomplete, or selectively chosen facts.** Conformance is a floor, not a quality guarantee (§16).
- **Rank, score, or adjudicate between sources.**
- **Establish the legal identity of an organisation.** Identity rests on domain control and on the ordinary trust of TLS.
- **Replace digital signatures on documents,** or statutory disclosure obligations, or audit.
- **Compel any consumer to prefer a register over other sources.** A search engine, a model, or a regulator may have good reasons to cross-check. DFR makes a publisher's own record checkable. It does not tell anyone what to do with it.

## 8. Scope and profiles

**In scope.** The register format: the structure of an entry, the seal, the release commitment, the release digest, the anchor, the files a publisher exposes, and the procedure a verifier follows. Also, precisely, what the format does and does not attest.

**Out of scope.** How facts are extracted from sources, how sources are selected or judged authoritative, how the context of a fact is phrased, and how a register is produced operationally. Those are matters of practice, not of format. A register conforms if its published artifacts satisfy Part II, irrespective of how it was produced.

**Profiles.** The seal, commitment, digest, anchor and verification procedure are independent of the subject matter of the facts they cover. What is domain-specific is the data model of §9, which describes a fact about an organisation drawn from a document that organisation publishes. Version 0.1 therefore defines the **organisational disclosure profile**. Other profiles are possible on the same cryptographic layer and may be specified later. A profile covering subject matter whose sources are themselves versioned and legally load-bearing would need to address the limitation of §4, which this profile does not.

---

# Part II. Technical specification

## 9. Data model

A register is a JSON array of entry objects. Each entry is a flat JSON object.

### 9.1 Sealed fields

Six fields, and only these, are covered by the seal. Four are REQUIRED and non-null. Two are nullable.

| Field | Requirement | Type |
| :-- | :-- | :-- |
| `context` | REQUIRED, non-null | string |
| `label` | REQUIRED, non-null | string |
| `source_url` | REQUIRED, non-null | string |
| `value` | REQUIRED, non-null | string |
| `time_period` | nullable | string or `null` |
| `unit` | nullable | string or `null` |

- `context`. A human-readable sentence situating the fact, quoting or closely tracking the source.
- `label`. A short name for the fact.
- `source_url`. The URL of the public source. **This is the authoritative binding.** See §9.2.
- `value`. The fact itself, as a string. Numeric facts are carried as strings (§10.4).
- `time_period`. The period the value refers to, where applicable, for example `"2025"`. `null` otherwise.
- `unit`. The unit of the value, where applicable, for example `"billion EUR"`. `null` otherwise.

`unit` and `time_period` are sealed because they are load-bearing. On a quantitative fact, a value without its unit or its period is not the same fact, and if they were unsealed either could be altered without breaking the seal.

### 9.2 `source_url`

`source_url` MUST be an absolute URL with the `https` scheme, and it MUST resolve publicly, meaning it MUST NOT be a private, link-local, or loopback address, and MUST NOT require authentication to retrieve.

**`source_url` is sealed byte-for-byte, exactly as published. A conformant implementation MUST NOT normalise it** before sealing: not the scheme case, not a trailing slash, not query-parameter order, not percent-encoding. Two URLs that differ by a single byte are two different URLs and produce two different seals. This is deliberate. Any normalisation rule would have to be implemented identically by every party, and disagreement about normalisation is the most common way independent implementations of a canonicalisation scheme silently diverge.

A publisher SHOULD cite a source precisely enough that an independent party can locate the fact within it. See §9.2b on how `context` serves this purpose. A citation that satisfies the letter of this specification while making a fact practically unfindable defeats its purpose. Precision of citation cannot be mechanically tested, so this is a SHOULD. See §16 on the limits of conformance.

### 9.2b `context` as locator

`context` is sealed, and it is the mechanism by which a fact is located within its source.

`context` MUST carry enough of the source text surrounding the fact that an independent party, holding only the register, can open `source_url` and find the fact within the document. Where practical, `context` SHOULD quote the source verbatim.

This is what makes a DFR **traceable** and not merely attributed. The chain a third party can follow, without trusting anyone, is:

```
sealed value  ->  sealed context (searchable in the source)
              ->  sealed source_url (the document)
              ->  sealed_at (when this version was sealed)
              ->  release_digest (signed)
              ->  transparency log entry (immutable, timestamped)
              ->  previous_release_commitment (the prior state)
```

Every link in that chain is either covered by a seal or covered by the signature. Because `context` is sealed, a publisher cannot later weaken the locator without breaking the seal: the pointer into the source is as tamper-evident as the value itself.

The limits are stated rather than concealed. DFR does not guarantee that a given `context` is *sufficient* in a particular case, because sufficiency is a judgement no format can test. And it does not guarantee that the source document still contains what `context` quotes, because it binds a citation and not a snapshot (§4).

### 9.3 Normalisation of nullable fields

The following table is normative. It defines exactly how an implementation MUST treat each possible input to a nullable sealed field (`time_period`, `unit`) before computing the preimage.

| Input | Treatment |
| :-- | :-- |
| JSON `null` | Sealed as `null`. |
| Field absent from the entry | Sealed as `null`. |
| Empty string `""` | Sealed as `null`. |
| The string `"null"` | **MUST be rejected or normalised to `null`.** It MUST NOT be sealed as the string `"null"`. |
| Any other string | Sealed as that string, byte-for-byte. |
| Any non-string, non-null type | **MUST be rejected.** |

**A nullable field is always present in the preimage.** Where its normalised value is `null`, it appears as the JSON literal `null`. It is never omitted. An omitted field and an explicit `null` produce different preimages, so an implementation that drops absent fields will produce seals no conformant verifier can reproduce.

REQUIRED sealed fields admit no normalisation. A REQUIRED field that is absent, `null`, empty, or not a string MUST be rejected, and the entry MUST NOT be sealed.

### 9.4 Unsealed fields

An entry MAY carry fields not covered by the seal. The reference implementation publishes:

- `source_name`. A human-readable name for the source, for display. **Deliberately unsealed.**

An implementation MUST record, in its own store, the time at which each version of an entry was sealed, because without it there is no way to determine which version of an entry is current. It MAY publish that time as `sealed_at`, and it MAY publish a stable entry identifier. Neither is required in a published register: a register publishes only the current version of each entry, so a consumer faces no version ambiguity for the publisher to resolve.

`source_name` is unsealed by design, and the design is stated so it is not mistaken for an omission. The authoritative binding to the source is `source_url`, which the seal covers. `source_name` is a display label, and altering it does not change which source the fact is bound to. The seal covers the fields whose alteration would change the meaning or provenance of a fact, and it deliberately does not cover a label that restates, in friendlier words, what the URL already anchors.

**A verifier MUST NOT treat any unsealed field as load-bearing.** A consumer needing the authoritative source MUST use `source_url`. An interface that displays `source_name` while linking elsewhere can mislead a human reader, and no seal prevents this. It is a property of the consumer, not of the register.

Each entry also carries its own `seal`. By construction, the seal is not part of its own preimage.

## 10. The seal

### 10.1 Definition

```
seal = lowercase_hex( SHA-256( canonical_preimage ) )
```

where `canonical_preimage` is the RFC 8785 canonicalisation (§10.2) of the object containing exactly the six sealed fields of §9.1, normalised per §9.3.

### 10.2 Canonicalisation

The preimage MUST be produced according to **[RFC 8785](https://www.rfc-editor.org/rfc/rfc8785), the JSON Canonicalization Scheme (JCS)**.

For this schema, JCS requires: object keys sorted by UTF-16 code unit, which for the six ASCII field names is plain alphabetical order; compact serialisation with no insignificant whitespace; UTF-8 output; and strings emitted with only the escapes JSON requires, so that non-ASCII characters, including accented text, are preserved raw.

The sealed field order is therefore always:

```
context, label, source_url, time_period, unit, value
```

The reference implementation computes the preimage by calling an RFC 8785 library directly, so that the reference code *is* the canonicalisation standard rather than an approximation of it. Independent implementations MAY use any conformant RFC 8785 implementation.

> **Note on generic JSON serialisers.** For this all-string, pre-ordered schema, a compact key-sorted JSON serialisation happens to be byte-identical to RFC 8785. Implementers MUST NOT assume that equivalence holds for schemas containing numbers, where RFC 8785 imposes a strict numeric canonicalisation that generic serialisers do not. DFR avoids the question by carrying all values as strings.

### 10.3 Worked example

Two synthetic entries, for a fictional "Example Foundation". Any conformant implementation MUST reproduce these seals exactly.

**Entry A, all fields present:**

```json
{
  "context": "Total assets under management as reported in the 2025 annual report",
  "label": "Assets under management",
  "source_url": "https://example.org/annual-report-2025.pdf",
  "value": "4.2",
  "unit": "billion EUR",
  "time_period": "2025",
  "source_name": "Example Foundation 2025 Annual Report"
}
```

Canonical preimage. Note that `source_name` is absent, and the six fields appear in sealed order:

```
{"context":"Total assets under management as reported in the 2025 annual report","label":"Assets under management","source_url":"https://example.org/annual-report-2025.pdf","time_period":"2025","unit":"billion EUR","value":"4.2"}
```

Seal:

```
09b95d606c16a544fa911ecbdd4bbaaca9f8dfaccc5405614dafe83f51bcf812
```

**Entry B, nullable fields absent:**

```json
{
  "context": "Legal form of the entity as stated on its public registry page",
  "label": "Legal form",
  "source_url": "https://example.org/registry",
  "value": "Association loi 1901",
  "source_name": "Public Registry"
}
```

Canonical preimage. Note that `time_period` and `unit` are present as explicit `null`:

```
{"context":"Legal form of the entity as stated on its public registry page","label":"Legal form","source_url":"https://example.org/registry","time_period":null,"unit":null,"value":"Association loi 1901"}
```

Seal:

```
07054cbd108ebda0453eec7e46a66dde14eb38727b06c34a0103c28846ee1f70
```

### 10.4 Why values are strings

Carrying all values as strings makes canonicalisation exact and independent of locale and numeric formatting. The string `"4.2"` seals identically everywhere, whereas a float `4.2` invites representation differences across languages and libraries. The consequence is that DFR has no notion of datatype: interpretation is delegated entirely to the consumer, and a value of `"Many"` for a headcount is formally valid. §16 addresses what conformance does and does not guarantee.

## 11. Releases

A **release** is a published state of a register. Three artifacts describe it: the **release commitment** over the entry seals, the **release digest** over the release metadata, and the **anchor**.

### 11.1 The release commitment

The release commitment is an [RFC 6962](https://www.rfc-editor.org/rfc/rfc6962) (Certificate Transparency) Merkle tree root over the entry seals.

1. **Filter.** Drop any empty or absent seal, and any seal equal to the sentinel `NO_HASH_FOUND`, which marks an entry whose seal could not be computed.
2. **Sort.** Sort the remaining seals in ascending lexicographic order. **Seals are NOT deduplicated.** If two entries seal identically, both leaves are present, and multiplicity is preserved. A verifier MUST sort identically and MUST NOT deduplicate.
3. **Leaf hash.** For each seal `s`: `leaf = SHA-256( 0x00 || UTF-8(s) )`.
4. **Internal node.** For child hashes `L` and `R`, each a raw 32-byte digest: `node = SHA-256( 0x01 || L || R )`.
5. **Tree shape.** Where the number of nodes `n` at a level is not a power of two, split so that the largest power of two strictly less than `n` is on the left and the remainder on the right. This is the RFC 6962 split. There is **no duplicate-last-node step**, which closes the [CVE-2012-2459](https://nvd.nist.gov/vuln/detail/CVE-2012-2459) duplication ambiguity.
6. **Empty register.** `SHA-256("")`, that is `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

Because seals are sorted, the commitment binds the **multiset** of seals, independent of the order in which entries appear in `ledger.json`. It therefore does not attest entry order. Order carries no part of the fidelity claim, though a publisher may still order a register meaningfully for human readers.

RFC 6962 was chosen for the same reason as RFC 8785: it is a reviewed, off-the-shelf construction an adopter can implement from a library, rather than a bespoke tree they would have to reason about before trusting.

**Worked example**, using the two seals of §10.3:

- `leaf(09b95d60…)` = `ded0a03effb770c9c9f1d2499087b74c2b5c06ec37b24d37f659b3cb493df0a7`
- `leaf(07054cbd…)` = `51c818ac1cd033ea8f5a722e026d43fe251da6a3f45e77a28d668c1463146858`
- Sorted, `07054cbd…` precedes `09b95d60…`
- **Release commitment:** `24e1ed213c7c61806cae2d4cae2fbc18d5d9f6b87d978e2292df37ab9ded5696`

### 11.2 The release digest

The release commitment binds the facts. It does not bind *whose* facts they are, *which release preceded* them, or *what else was published alongside* them. The **release digest** binds all of that, and it is the release digest, not the bare commitment, that is signed and anchored.

```
release_digest = lowercase_hex( SHA-256( JCS({
    company_id,
    file_hashes,
    generated_at,
    previous_release_commitment,
    release_commitment,
    row_count,
    spec_version
}) ) )
```

where `file_hashes` is an object mapping each published filename to the lowercase-hex SHA-256 of its bytes as served, for every file of §14 that the publisher publishes, **excluding `release.json` itself**, which cannot contain its own digest.

**Two canonicalisation rules are load-bearing here, and an implementation that ignores either will produce a digest nobody else can reproduce.**

**`row_count` is carried as a string.** In the digest object it is `"74"`, not `74`. RFC 8785 imposes a strict numeric canonicalisation that generic JSON serialisers do not implement, so a numeric field is the one place two independent implementations can silently disagree. Carrying it as a string removes the question. This is the same reasoning that makes entry values strings (§10.4), and it is what allows an implementation to use a plain key-sorted compact serialiser and still be byte-identical to RFC 8785 for this object.

**JCS sorts keys at every level, including inside `file_hashes`.** The nested filenames MUST be sorted by UTF-16 code unit, which is not the order a person would type them. Note that `-` (U+002D) sorts before `.` (U+002E), so `latest.md` precedes `ledger-jsonld.json`, which precedes `ledger.json`. An implementation MUST sort programmatically rather than by hand.

This closes three gaps that a signature over the bare commitment leaves open.

**It binds the entity.** An entry seal covers only its six fields, so a sealed entry is portable: the same sealed row could be lifted into another register and would still verify. The register, not the entry, defines whose facts these are, and the release digest is what makes that binding cryptographic rather than merely structural.

**It binds the chain.** `previous_release_commitment` is what makes the history of a register tamper-evident. A signature that did not cover it would leave the chain unauthenticated and freely editable.

**It binds the derived files.** `file_hashes` brings `ledger-jsonld.json`, `latest.md` and `llm.txt` under the signature (§5), so that the unsealed surfaces most consumers actually read cannot be altered without detection.

### 11.3 `release.json`

A conformant `release.json` MUST contain:

| Field | Requirement | Description |
| :-- | :-- | :-- |
| `spec_version` | REQUIRED | The DFR version the release conforms to, for example `"0.1"`. |
| `company_id` | REQUIRED | The stable identifier of the entity. |
| `release_id` | REQUIRED | A unique identifier for this release. |
| `generated_at` | REQUIRED | UTC timestamp, ISO 8601 with `Z`. |
| `row_count` | REQUIRED | The number of seals committed to, after the filtering of §11.1. |
| `release_commitment` | REQUIRED | The RFC 6962 root of §11.1. |
| `previous_release_commitment` | REQUIRED | The prior release's commitment, or `null` for the first release. |
| `release_digest` | REQUIRED | The digest of §11.2. This is what is signed. |
| `file_hashes` | REQUIRED | Object mapping published filename to lowercase-hex SHA-256 of its bytes. |
| `signer` | REQUIRED | Identifies the party that signed this release (§6). An object with at minimum a human-readable `name` and a `key_id` (§12.2). |
| `anchor_status` | REQUIRED | `"anchored"` or `"anchor_pending"` (§12). |
| `anchor` | REQUIRED | The anchor object (§12.1), or `null` when `anchor_status` is `"anchor_pending"`. |

**Notes.**

- `row_count` counts seals after filtering. Where every entry seals successfully, which is the normal case, it equals the number of entries in `ledger.json`.
- Where a release commits to an unchanged set of entries, `previous_release_commitment` will equal `release_commitment`. This is correct, and records that a release occurred in which the data did not change.
- A `release.json` MAY carry additional fields. A verifier MUST ignore fields it does not recognise, and MUST NOT treat an unrecognised field as load-bearing.

### 11.4 Retention of prior releases

**A publisher MUST keep prior releases retrievable at stable URLs for as long as the register is published.**

This is a MUST because without it the hash chain is decorative. `previous_release_commitment` makes history tamper-evident only if the prior release can still be fetched and checked. A publisher who deletes earlier releases satisfies every other rule in this specification while destroying the property the chain exists to provide.

Anchoring provides a partial backstop: the commitments of deleted releases survive in the transparency log, so it remains provable *that* a release with a given commitment existed at a given time. It does not remain possible to recover *what it contained*. Retention is therefore a publisher obligation and cannot be delegated to the log.

## 12. Anchoring

A release digest SHOULD be signed and anchored in a public, append-only transparency log, so that the existence and time of a release are independently attested. The reference implementation signs the release digest and anchors it in **Sigstore Rekor**.

`anchor_status` is `"anchored"` when signing and log submission both succeeded, and `"anchor_pending"` otherwise. A register with `anchor_status: "anchor_pending"` is still conformant: its seals and commitment verify. It simply carries no signature and no temporal attestation.

### 12.1 The anchor object

When `anchor_status` is `"anchored"`, `anchor` MUST contain:

| Field | Requirement | Description |
| :-- | :-- | :-- |
| `method` | REQUIRED | `"sigstore-rekor"` in the reference implementation. |
| `signature_b64` | REQUIRED | The signature **over `release_digest`**, base64. |
| `algorithm` | REQUIRED | For example `EC_SIGN_P256_SHA256`. |
| `public_key_url` | REQUIRED | URL at which the verifying public key is published. |
| `key_id` | REQUIRED | Identifier of that key (§12.2). |
| `rekor_log_index` | REQUIRED for Rekor | The log index of the entry. |
| `rekor_entry_url` | REQUIRED for Rekor | URL of the log entry. |
| `rekor_uuid` | RECOMMENDED | The entry UUID. |
| `rekor_log_id` | RECOMMENDED | Identifier of the log instance. |
| `rekor_integrated_time` | RECOMMENDED | Unix time of integration into the log. |

**The anchor object MUST NOT contain internal infrastructure identifiers**, such as key-management resource paths or cloud project identifiers. They serve no verification purpose, since a verifier can neither use them nor needs them, and they disclose signer topology gratuitously. The verification-relevant identity of the signing key is carried by `public_key_url` and `key_id`, and by nothing else.

### 12.2 `key_id` and key rotation

`key_id` identifies which public key verifies a release. The reference implementation uses the SHA-256 digest of the DER encoding of the public key, as `sha256:<lowercase-hex>`. Any party can reproduce it:

```
openssl pkey -pubin -in <public-key>.pem -outform DER | sha256sum
```

`key_id` is therefore self-verifying: a verifier hashes the key it fetched and confirms it is the key the release claims to have been signed by. It is not a label the signer merely asserts.

Without it, a release signed under a superseded key becomes unverifiable as soon as `public_key_url` serves a newer key, and it fails silently, in a way indistinguishable from tampering. Accordingly:

- A signer that rotates its key **MUST** keep prior public keys retrievable, so that releases signed under them remain verifiable.
- A verifier **MUST** verify `signature_b64` against the key whose digest matches `key_id`.

## 13. Delegation (OPTIONAL)

A signature establishes that the holder of a key produced a release. It does not establish that the entity authorised that key. Where the builder and signer are not the entity (§6), an entity MAY make that authorisation explicit and verifiable by publishing a **delegation record** on infrastructure it controls.

The delegation record is a statement, published by the entity, that a given key is authorised to sign DFR releases for that entity. It MAY be published as:

- a **DNS TXT record** on the entity's domain, of the form
  `dfr-signer=sha256:<lowercase-hex>`, one record per authorised key; or
- a resource at **`/.well-known/dfr-signers`** on the entity's domain, listing authorised `key_id` values.

DNS is RECOMMENDED where available, because it requires control of the entity's DNS rather than write access to its web server, and therefore survives a compromise of the hosting.

Where a delegation record is published, a verifier SHOULD fetch it and confirm that the `key_id` in `release.json` is authorised. Where none is published, a verifier learns only what §6 states: that a key signed a register hosted on the entity's domain.

This mechanism is OPTIONAL in v0.1. It binds signing authority to domain control, which is the same trust root TLS already relies on. It does not defend against an adversary who controls the entity's DNS, and nothing at this layer can. Detection in that case rests on the transparency log, as it does in Certificate Transparency.

Placing the delegation record under `/.well-known/` is appropriate because it *is* metadata about the origin: a statement about how a machine should treat things published under that domain. This is distinct from the register itself, which is content and is published at a content path (§14).

## 14. Publication requirements

A publisher exposes a register over HTTPS on a domain the entity controls.

| File | Status |
| :-- | :-- |
| `ledger.json` | REQUIRED |
| `release.json` | REQUIRED |
| `ledger-jsonld.json` | REQUIRED in v0.1 |
| `latest.md` | RECOMMENDED |
| `llm.txt` | RECOMMENDED |

Every published file other than `release.json` MUST be listed in `file_hashes` (§11.2).

**Location.** Files are published at stable content paths. A dedicated subdomain, for example `disclosures.<entity-domain>` or `register.<entity-domain>`, is RECOMMENDED as a clear and collision-free convention.

A register is **content**, and is published at a content path. DFR does not place the register under `/.well-known/`. That namespace ([RFC 8615](https://www.rfc-editor.org/rfc/rfc8615)) is reserved for metadata about an origin, meaning information a machine needs in order to interact correctly with the site itself. A register is not metadata about a site: it is substantive content about an entity, which the site happens to host. The delegation record of §13 *is* origin metadata, which is why it may legitimately live there.

**Discoverability** is served by the JSON-LD export, which gives the facts a vocabulary generic systems already interpret, together with ordinary web mechanisms such as sitemaps and links.

## 15. Verification

Any party MAY verify a published register without trusting the entity, the builder, the signer, or the publisher.

### 15.1 Procedure

1. **Fetch** `ledger.json` and `release.json`.
2. **Recompute every entry seal** (§10) from its six sealed fields and compare with the published `seal`.
3. **Recompute the release commitment** (§11.1) over those seals, filtering and sorting and *not* deduplicating, and compare with `release_commitment`.
4. **Fetch every file listed in `file_hashes`**, hash its bytes, and compare with the listed digest.
5. **Recompute the release digest** (§11.2) and compare with `release_digest`.
6. **Verify the signature**, where `anchor_status` is `"anchored"`: fetch the public key from `public_key_url`, confirm its digest matches `key_id` (§12.2), and verify `signature_b64` over `release_digest` using `algorithm`.
7. **Check the anchor**: fetch the transparency-log entry at `rekor_log_index` or `rekor_entry_url` and confirm it commits to the same `release_digest`. See §15.1.1.
8. **Check the chain**, where history matters: fetch the prior release (§11.4) and confirm `previous_release_commitment` matches its `release_commitment`.
9. **Check delegation**, where a delegation record is published (§13): confirm `key_id` is authorised by the entity.
10. **Check freshness** (RECOMMENDED, §15.3).

### 15.1.1 Reading a Rekor entry

A naive check on the anchor produces a **false negative**, and it is worth stating how to avoid it, because a verifier that cries wolf on a valid register is as damaging as one that passes an invalid one.

The Rekor API returns an object keyed by the entry UUID. Its `body` is **base64-encoded**, and the body is a `hashedrekord` whose committed hash lives at `spec.data.hash.value`, with the algorithm at `spec.data.hash.algorithm`. The `release_digest` therefore does **not** appear as plain hex anywhere in the API response. A verifier that searches the raw response for the hex string will find nothing and wrongly report a failure.

A verifier MUST decode the body, read `spec.data.hash.value`, confirm `spec.data.hash.algorithm` is `sha256`, and compare that value with `release_digest`. It SHOULD also confirm that the `logIndex` served matches the `rekor_log_index` recorded in `release.json`.

### 15.2 Error model


A verifier MUST emit a structured result distinguishing:

- **FAIL (fatal).** Any of: an entry seal that does not match; a release commitment that does not match; a file digest that does not match; a release digest that does not match; a signature that does not verify; an anchor that does not commit to the presented `release_digest`; a delegation record that does not authorise the signing key. **A single failing entry fails the register.** A register is verified as a whole, and partial integrity is not a meaningful assurance.
- **WARN (non-fatal).** Any of: `anchor_status` is `"anchor_pending"`; a prior release referenced by the chain cannot be retrieved; no delegation record is published; freshness could not be established. Each of these means an assurance is *absent*, not that an assurance has *failed*.
- **PASS.** All fatal checks passed. A verifier MUST report which non-fatal assurances were absent, and MUST NOT report a register as fully verified where they were.

A verifier MUST identify, in its output, every entry whose seal failed.

### 15.3 Freshness, and a limitation

A verification that passes establishes that the release presented is internally consistent, signed, and anchored. **It does not establish that the release is the current one.**

An old release remains permanently valid: its seals verify, its digest verifies, its signature verifies, and its anchor is genuinely in the log. A publisher who wishes to conceal a later disclosure can therefore serve an earlier release, and a verifier following steps 1 to 9 will report PASS. This is a rollback, and no property internal to a single release can detect it.

Two mitigations are available and a verifier SHOULD apply one:

- **Query the log.** Fetch the transparency-log entries associated with the signer's `key_id` and confirm that the presented `release_digest` is the most recent one for this entity.
- **Signed pointer.** Where an entity publishes a signed statement of its current `release_id`, confirm the presented release matches it.

Where neither is possible, a verifier MUST report freshness as unestablished (WARN). Consumers MUST NOT infer currency from a passing verification alone.

## 16. Conformance

A register conforms to DFR v0.1 if:

1. Every entry carries the four REQUIRED sealed fields as non-null strings, and nullable fields are normalised per §9.3 and present as `null` where absent.
2. `source_url` satisfies §9.2.
3. Every published `seal` equals the SHA-256 of the entry's RFC 8785 six-field preimage (§10).
4. `release.json` carries the fields of §11.3; `release_commitment` equals the RFC 6962 root over the entry seals (§11.1); `release_digest` equals the digest of §11.2; and `file_hashes` matches the files as served.
5. The register is published over HTTPS on an entity-controlled domain with the REQUIRED files of §14, and prior releases are retrievable (§11.4).
6. Where `anchor_status` is `"anchored"`: the anchor carries the fields of §12.1; `signature_b64` verifies over `release_digest` under the key identified by `key_id`; and the log entry commits to the same `release_digest`.

**Conformance is a floor, not a quality guarantee.** This specification constrains *format*, not *disclosure adequacy*. A register may be fully conformant and still be trivial, selective, or uninformative: it may contain one entry, or only uncontroversial facts, or cite every fact to a single three-hundred-page document. Nothing here requires a register to cover any particular class of facts, to be complete relative to an organisation's other public statements, or to be useful. A reader MUST NOT infer from conformance that a register is *complete*, and an implementation MUST NOT describe a conformant register as verified *true*.

**What DFR does and does not trace.** DFR provides a traceability chain, and the chain is precise (§9.2b): a value, bound to a sealed context that locates it in the source, bound to a cited source URL, timestamped at sealing, signed, anchored in an immutable public log, and chained to the register's prior states. Every link is covered by a seal or by the signature, so the chain cannot be weakened after the fact without detection. This is a stronger property than attribution, and it is what "fidelity" in the name refers to.

Two limits bound it, and both are properties of the world rather than of the format:

- **Sufficiency of a citation cannot be tested.** §9.2b requires `context` to locate the fact within its source, but whether a given `context` in fact does so is a judgement, not a computation. Conformance cannot certify it.
- **The chain terminates at a citation, not at a document.** DFR binds to `source_url` and not to a snapshot of it (§4). The chain traces a fact to what was published, at the URL it was published at, at the time it was sealed. It does not preserve the document, and it does not attest to what that URL serves today.

Within those limits, the chain holds end to end and can be verified by anyone, without trusting the entity, the builder, the signer, or the publisher.

An implementation MUST NOT label a non-conformant register as a DFR.

**Test vectors.** A `test_vectors.json` accompanies the reference verifier. It MUST include at minimum: the two entries of §10.3 with their seals; the commitment of §11.1; the empty-register commitment; and a worked `release_digest`. An independent implementation is conformant with respect to the primitives if it reproduces these exactly. The vectors are what catches silent drift between implementations.

## 17. Security and trust considerations

- **The seal proves fidelity, not veracity** (§3). A publisher can seal a faithful record of a false statement. The seal will verify; the statement will remain false.
- **The seal binds a value to a URL, not to source content** (§4). If a source is revised, every seal continues to verify while pointing at a document that may no longer say what it said. Consumers for whom current source content is material MUST fetch the source.
- **A passing verification does not establish currency** (§15.3). An old, genuinely signed, genuinely anchored release can be replayed. Freshness must be established against the log or a signed pointer.
- **Unsealed fields carry no integrity guarantee** (§9.4). A consumer needing the authoritative source MUST use `source_url`. A misleading display of `source_name` is an attack on a consumer interface, and no seal prevents it.
- **The derived files are signed but not authoritative** (§5). `file_hashes` makes their alteration detectable. It does not make them a source of truth, and a consumer that reads only the JSON-LD, without verifying, gains no assurance from DFR.
- **A signature is not an endorsement** (§6). It establishes that a key holder produced a release. Absent a delegation record (§13), it does not establish that the entity authorised that key, nor that the entity reviewed the contents.
- **Compromise of the publication channel is outside the threat model.** An adversary with write access to the entity's domain, and a key of their own, can publish a register that is internally valid. DFR does not prevent this. It makes it *evidentiary*: the fraudulent release is signed under a key that is not the entity's delegated signer, and it is permanently recorded in a public log. Detection rests on the log and on the delegation record, exactly as in Certificate Transparency.
- **The commitment binds a multiset, not an order** (§11.1). Reordering `ledger.json` does not change the commitment. Order forms no part of the fidelity claim. Seals are not deduplicated, so removing a duplicated entry does change the commitment.
- **Key rotation is a signer obligation** (§12.2). A signer who rotates without keeping prior public keys retrievable renders history unverifiable in a way that resembles tampering.
- **Retention is a publisher obligation** (§11.4). Deleting prior releases destroys the chain's value while satisfying every other rule.
- **Canonicalisation is load-bearing** (§10.2). An implementation that deviates from RFC 8785, for instance by assuming a generic JSON serialiser equals JCS on a numeric schema, produces seals nobody else can reproduce. This is why v0.1 carries all values as strings.

## 18. Licence, attribution and governance

- **This specification text** is licensed **CC BY 4.0**. Anyone may use, adapt and redistribute it, provided attribution is retained. Attribution is the single obligation, and it is compatible with French *droit moral*.
- **The reference verifier** is licensed **MIT**.
- Specification and verifier are maintained in a neutral project, the repository organisation `data-fidelity-register`, with two repositories: `spec` (CC BY 4.0) and `verifier` (MIT). Origin is documented, namely that the specification is edited by Thomas Meister of Der Apparat and that the first implementation is Apparat, while ownership of the format is neutral, so that adopters publish in the DFR format rather than in a vendor's format.
- **Nothing in this specification requires a builder.** An entity holding all four roles of §6 can produce, sign and publish a conformant register using the reference verifier and the primitives specified here, with no dependency on Apparat or on any other party.
- The names **Data Fidelity Register** and **DFR** are not licensed by the above. The permissive licences cover use of the format and the code. They do not convey the right to apply the name to a non-conformant variant.

---

*End of DFR Specification v0.1 (draft).*
