# Indicators vs Observables

OpenCTI's knowledge is built from STIX Cyber Observables (SCOs) and Indicators (SDOs), and
the two are easy to conflate because they often describe the same underlying fact — an IP,
a domain, a file. The distinction matters: it separates "what was seen" from "what that means."

## Observable: a raw fact, no judgment

An **Observable** (`stix-cyber-observable`) represents an immutable fact that was observed —
an IPv4 address, a domain name, an email address, a file hash. Observables "don't inherently
imply malicious intent"; they are raw data points, not verdicts. A `1.2.3.4` observable could
be a C2 server or your own office gateway — the observable alone doesn't say which.

An **Artefact** is a specialized observable that can carry an actual file (e.g. a malware
sample), uploaded directly or via an encrypted archive.

## Indicator: a detection statement

An **Indicator** is a detection object: it asserts that a pattern of observable data is
associated with malicious or suspicious activity. It is built around a **pattern**
(commonly a STIX pattern, though Sigma, YARA, and other formats are also supported) and
carries fields an observable doesn't have:

- **Validity window** — `valid_from` and `valid_until` dates bound when the indicator is
  considered relevant.
- **Revoked** — a boolean marking the indicator as no longer active/trustworthy.
- **Detection** — a boolean flag indicating the indicator is intended to drive automated
  detection (vs. being informational only); it lets analysts filter for indicators that
  should actually feed detection tooling.
- **Kill chain phase(s)** and **indicator types** — categorical context for where in an
  attack the pattern applies.
- **Confidence** and **score** — see below.
- **`x_opencti_main_observable_type`** — the observable type the pattern is built on
  (e.g. `IPv4-Addr`, `Domain-Name`, `StixFile`).

In short: the observable is the noun, the indicator is the claim "this noun is bad, here's
the pattern that matches it, and here's how confident/valid that claim is."

| | Observable | Indicator |
|---|---|---|
| What it is | A raw fact seen (IP, domain, hash, ...) | A detection statement (a pattern) |
| Implies malicious intent | No | Yes — that's its purpose |
| Has a pattern | No | Yes (`pattern`, `pattern_type`) |
| Has validity dates | No | Yes (`valid_from`, `valid_until`) |
| Has `revoked` / `detection` flags | No | Yes |
| Main type field | `entity_type` (e.g. `IPv4-Addr`) | `x_opencti_main_observable_type` |
| Linked via | — | `based-on` → one or more observables |

### Why keep them separate

Splitting the fact from the judgment lets OpenCTI (and analysts) reuse the same observable
across many indicators, avoid asserting maliciousness on data that's merely been *seen*
(e.g. an observable pulled from a benign report), and independently track how confident the
platform is that a given pattern is still worth acting on — without having to re-litigate
whether the underlying IP/domain/hash itself "exists."

## The `based-on` relationship

An indicator is linked to the observable(s) it was derived from via a **`based-on`**
relationship (indicator → observable). On an indicator's Overview tab, OpenCTI shows the
observables it is composed of; on an observable's Overview tab, OpenCTI shows the indicators
built on it. This is what lets an analyst pivot from "I have this IP" to "is there a
detection statement about it" and back.

## STIX pattern examples

Indicator patterns for `pattern_type = "stix"` follow STIX 2.1 patterning syntax — an
observable-type/property equality (or comparison) expression in square brackets:

```
[ipv4-addr:value = '1.2.3.4']
[domain-name:value = 'evil.com']
[file:hashes.'SHA-256' = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855']
[url:value = 'http://evil.example/payload']
[domain-name:value = 'evil.com' AND ipv4-addr:value = '1.2.3.4']
```

The last example shows a compound pattern (two observation predicates joined with `AND`),
still expressed as a single indicator with one main observable type. The
`x_opencti_main_observable_type` field on the indicator should match the primary observable
type referenced in the pattern (`IPv4-Addr`, `Domain-Name`, `StixFile`, etc.).

## Scoring, decay, and the detection flag

Both observables and indicators carry a numeric **score** (`x_opencti_score` on observables;
score on indicators), 0-100, reflecting how confident OpenCTI is that the object is
malicious. Indicators start at an initial score — provided by the data source, or 50 by
default.

Over time an indicator's score decreases according to a **decay rule**: a curve (defined by
a decay factor and a lifetime in days) with configured **reaction points** — thresholds at
which the score is stepped down. For example, a rule with reaction points at 60 and 40 will
step an indicator created at score 80 down to 60, then 40, as it ages. The decay rule that
applies is chosen and locked in at indicator creation time and does not change on later
updates. If no `valid_until` is supplied, OpenCTI computes one from the decay rule's revoke
score — the point at which the curve would bring the indicator to the "revoke" threshold.

When an indicator's score decays to (or is manually set at/below) its rule's **revoke
score**, or when `valid_until` passes, the indicator is automatically marked **revoked** and
its **detection** flag is set to `false` — it stops being treated as something that should
drive active detection. Un-revoking without an explicit new score resets the score back to
the value it had at creation (or 50 with no applicable decay rule).

## In this MCP

- `observables_create` makes an observable. For file hashes, use key
  `File.hashes.SHA-256` (the tool also accepts `StixFile.*` and normalizes it to `File.*`);
  pass `additional_hashes` (`"SHA-1:...", "MD5:..."`) to attach extra hashes to the same
  file observable.
- `indicators_create` makes an indicator: `pattern` (the STIX pattern string),
  `pattern_type` (e.g. `"stix"`), and `x_opencti_main_observable_type` (e.g. `"IPv4-Addr"`)
  are required, plus optional `valid_from`, `confidence`, `marking_ids`, `label_ids`.
- `observables_by_value` looks up an observable by its exact value (IP, domain, hash, etc.)
  before deciding whether to create a new one or reuse an existing one.
- To connect an existing indicator to an existing observable, use `relationships_create`
  with `relationship_type="based-on"`, `from_id` = the indicator's id, `to_id` = the
  observable's id.

### Typical flow: "I have an IOC, is it known — and can I flag it as malicious?"

1. `observables_by_value(value="1.2.3.4")` — check whether the observable already exists
   before creating a duplicate.
2. If nothing comes back, `observables_create(observable_key="IPv4-Addr.value",
   observable_value="1.2.3.4")` to record the raw fact.
3. `indicators_create(name="...", pattern="[ipv4-addr:value = '1.2.3.4']",
   pattern_type="stix", x_opencti_main_observable_type="IPv4-Addr")` to assert it's
   malicious.
4. `relationships_create(from_id=<indicator id>, to_id=<observable id>,
   relationship_type="based-on")` to link the two, so the indicator's "based-on" tab shows
   the observable and vice versa.

## Source

> OpenCTI docs (latest), distilled 2026-07-10.

- https://docs.opencti.io/latest/usage/exploring-observations/
- https://docs.opencti.io/latest/usage/indicators-lifecycle/
- https://docs.opencti.io/latest/administration/decay-rules/
