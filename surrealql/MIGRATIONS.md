# SurrealQL Migration Order

Apply migrations in this order because later files depend on metamodel tables and defined terms created earlier.

1. `schema_org_metamodel.surql`
2. `schema_org_defined_terms.surql`
3. `security.surql`
4. `commerce_schema_org.surql`
5. `commerce_actions_schema_org.surql`
6. `invoice_metamodel.surql`

Use:

```bash
python scripts/apply_surreal_migrations.py
```

The migration runner uses this manifest order first and falls back to sorted `*.surql` files for any additional migrations not listed here.
