# Digital Commerce Ecosystem

> **Enabling Indian business to go global** — open, digital-native business transformation.

A model for a GoIDC-style *global digital identity & commerce ecosystem*, layered on
top of the existing Agent-Commerce security and commerce schemas. It adds the pieces
that turn a storefront into an identity-driven, referral-powered network: digital
identity profiles ("AI business cards"), membership programs and tiers, prepaid
activation **E-pins**, and a **referral network** with commission accounting.

Schema: [`surrealql/digital_identity_ecosystem.surql`](../surrealql/digital_identity_ecosystem.surql)

## What GoIDC offers (research summary)

`goidc.in` brands itself as a *"Global Digital Identity Ecosystem"* — secure, borderless,
and AI-driven — aimed at connecting professionals, businesses, and investors worldwide.
Direct page fetch returns `403 Forbidden` to automated clients, so the following is
assembled from web search and indexed copies of the site:

| Offering | What it is |
|----------|------------|
| **AI digital business cards** | Shareable digital identity profiles with clickable links, social handles, multimedia, real-time updates, and engagement tracking. |
| **E-pins** | Prepaid, single-use activation codes ("1 E-pin") used to activate a membership. |
| **Membership tiers** | Pricing plans (e.g. *Personal* / *Get Started*) gated by E-pins. |
| **Referral / passive income** | "Passive income – up to ₹2.5cr"; a click-and-earn referral network. |
| **Shop** | `goidc.in/shop/` selling E-pins / plans. |
| **Support** | 24/7 customer support. |

> ⚠️ **Caution flag.** The combination of *prepaid E-pins + membership tiers + large
> "passive income" promises + a referral tree* is characteristic of a **referral / MLM
> (multi-level-marketing) model**. The schema here models the mechanics **neutrally**
> (referral as a legitimate single-level affiliate pattern), but the income claims on the
> live site should be treated with skepticism and verified independently before any
> financial engagement. No independent third-party reviews of GoIDC surfaced during research.

## Domain model

```mermaid
erDiagram
    users ||--o{ identity_profiles : owns
    users ||--o{ memberships : holds
    users ||--o{ epins : "issued / redeems"
    users ||--o{ referral_commissions : "earns"
    users ||--o{ referred : "sponsors (graph)"

    identity_profiles ||--o{ profile_views : "tracks engagement"
    identity_profiles }o--|| merchants : "represents (optional)"

    membership_programs ||--o{ membership_tiers : "defines"
    membership_tiers ||--o{ memberships : "instantiated as"
    membership_tiers ||--o{ epins : "activates"

    epins ||--o| memberships : "redeemed into"
    epins }o--o| payments : "purchased via"

    memberships ||--o{ referral_commissions : "triggers"

    users {
        string username
        string email
        string role
        string tenant_id
    }
    identity_profiles {
        string handle UK
        string display_name
        array  links
        array  credentials
        bool   is_verified
        int    view_count
    }
    membership_tiers {
        string name
        decimal price
        int     epins_required
        decimal referral_rate
    }
    epins {
        string code UK
        string status
        decimal face_value
    }
    memberships {
        string membershipNumber UK
        string status
        datetime expires_at
    }
    referral_commissions {
        decimal rate
        decimal amount
        string  status
    }
```

## Entities

| Table | Schema.org grounding | Purpose |
|-------|----------------------|---------|
| `identity_profiles` | [ProfilePage](https://schema.org/ProfilePage) / [Person](https://schema.org/Person) | The digital ID / AI business card: handle, links, credentials, verification. |
| `profile_views` | — | Engagement events (view, link tap, save contact, share). |
| `membership_programs` | [MemberProgram](https://schema.org/MemberProgram) | A membership scheme owned by a tenant. |
| `membership_tiers` | [MemberProgramTier](https://schema.org/MemberProgramTier) | Priced plans, E-pin requirement, and referral rate. |
| `memberships` | [ProgramMembership](https://schema.org/ProgramMembership) | A user's active membership in a tier. |
| `epins` | voucher-style | Prepaid single-use activation codes. |
| `referred` (relation) | — | Graph edge: sponsor → member. |
| `referral_commissions` | [MoneyTransfer](https://schema.org/MoneyTransfer) | Commission credited to a referrer. |

## Lifecycle (activation + referral payout)

```mermaid
sequenceDiagram
    participant Buyer
    participant Shop
    participant DB as SurrealDB
    Buyer->>Shop: Purchase E-pin (payment)
    Shop->>DB: CREATE epins { status: unused }
    Buyer->>DB: fn::redeem_epin(code, member)
    DB->>DB: CREATE memberships { status: active }
    DB->>DB: UPDATE epins { status: redeemed }
    DB->>DB: fn::record_referral_commission(membership)
    DB->>DB: find sponsor via `referred` (depth 1)
    DB->>DB: CREATE referral_commissions { status: pending }
    Note over DB: Commission settled via existing payout_batches flow
```

## Design notes

- **Reuses existing layers.** Identities come from `security.surql`'s `users`; merchants,
  payments, and the `settlement_ledger_entries` / `payout_batches` machinery in
  `settlements_payouts.surql` handle the actual money movement. `referral_commissions`
  is intentionally shaped like a settlement entry so payouts share one pipeline.
- **Multi-tenant + RLS.** Every table carries `tenant_id` and SurrealDB `PERMISSIONS`
  matching the repo's conventions (owner/admin/tenant scoping).
- **Single-level by default.** `referred.depth` and `referral_commissions.level` leave
  room for multi-level structures, but the shipped function credits only the **direct**
  sponsor — deliberately conservative given the MLM caution above.

## Apply

Add after the commerce and settlement migrations:

```bash
python scripts/apply_surreal_migrations.py
```
