# SurrealQL Migration Order

Apply migrations in this order because later files depend on metamodel tables and defined terms created earlier.

1. `schema_org_metamodel.surql`
2. `schema_org_defined_terms.surql`
3. `security.surql`
4. `commerce_schema_org.surql`
5. `commerce_actions_schema_org.surql`
6. `invoice_metamodel.surql`
7. `settlements_payouts.surql`
8. `digital_identity_ecosystem.surql`

Use:

```bash
python scripts/apply_surreal_migrations.py
```

The runner applies this manifest in order (the `ascii` full-text analyzer used by
`SEARCH` indexes is defined at the top of `schema_org_metamodel.surql`). Any
`*.surql` not listed here is applied afterwards, best-effort — a parse error in an
unlisted/WIP file is logged as a warning and skipped rather than failing the run.

In Docker this runs automatically as the one-shot `migrate` service before the API
starts (`docker compose up`).

> Verified against SurrealDB v2.3.7: all eight manifest files apply cleanly in this
> order, and the `fn::redeem_epin` → `fn::record_referral_commission` flow runs
> end-to-end.
