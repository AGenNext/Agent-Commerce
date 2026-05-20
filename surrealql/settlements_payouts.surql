-- Marketplace settlements and payouts
-- SurrealDB-first implementation.
-- Grounding:
-- - Money movement: https://schema.org/MoneyTransfer
-- - Payout execution: https://schema.org/PayAction
-- - Settlement invoice: https://schema.org/Invoice

DEFINE TABLE commission_rules SCHEMAFULL;
DEFINE FIELD tenant_id ON commission_rules TYPE string;
DEFINE FIELD merchant ON commission_rules TYPE option<record<merchants>>;
DEFINE FIELD category ON commission_rules TYPE option<string>;
DEFINE FIELD rate ON commission_rules TYPE decimal DEFAULT 0;
DEFINE FIELD fixed_fee ON commission_rules TYPE decimal DEFAULT 0;
DEFINE FIELD currency ON commission_rules TYPE string DEFAULT 'USD';
DEFINE FIELD is_active ON commission_rules TYPE bool DEFAULT true;
DEFINE FIELD created_at ON commission_rules TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON commission_rules TYPE datetime VALUE time::now();
DEFINE INDEX commission_rules_tenant ON commission_rules FIELDS tenant_id;
DEFINE INDEX commission_rules_merchant ON commission_rules FIELDS merchant;

DEFINE TABLE settlement_ledger_entries SCHEMAFULL;
DEFINE FIELD schema_context ON settlement_ledger_entries TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON settlement_ledger_entries TYPE string DEFAULT 'MoneyTransfer';
DEFINE FIELD schema_url ON settlement_ledger_entries TYPE string VALUE 'https://schema.org/MoneyTransfer';
DEFINE FIELD tenant_id ON settlement_ledger_entries TYPE string;
DEFINE FIELD merchant ON settlement_ledger_entries TYPE record<merchants>;
DEFINE FIELD order ON settlement_ledger_entries TYPE option<record<orders>>;
DEFINE FIELD payment ON settlement_ledger_entries TYPE option<record<payments>>;
DEFINE FIELD entry_type ON settlement_ledger_entries TYPE string;
DEFINE FIELD gross_amount ON settlement_ledger_entries TYPE decimal DEFAULT 0;
DEFINE FIELD commission_amount ON settlement_ledger_entries TYPE decimal DEFAULT 0;
DEFINE FIELD fee_amount ON settlement_ledger_entries TYPE decimal DEFAULT 0;
DEFINE FIELD net_amount ON settlement_ledger_entries TYPE decimal DEFAULT 0;
DEFINE FIELD currency ON settlement_ledger_entries TYPE string DEFAULT 'USD';
DEFINE FIELD status ON settlement_ledger_entries TYPE string DEFAULT 'pending';
DEFINE FIELD metadata ON settlement_ledger_entries TYPE object DEFAULT {};
DEFINE FIELD created_at ON settlement_ledger_entries TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON settlement_ledger_entries TYPE datetime VALUE time::now();
DEFINE INDEX settlement_ledger_merchant ON settlement_ledger_entries FIELDS merchant;
DEFINE INDEX settlement_ledger_order ON settlement_ledger_entries FIELDS order;
DEFINE INDEX settlement_ledger_status ON settlement_ledger_entries FIELDS status;

DEFINE TABLE payout_batches SCHEMAFULL;
DEFINE FIELD schema_context ON payout_batches TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON payout_batches TYPE string DEFAULT 'PayAction';
DEFINE FIELD schema_url ON payout_batches TYPE string VALUE 'https://schema.org/PayAction';
DEFINE FIELD tenant_id ON payout_batches TYPE string;
DEFINE FIELD merchant ON payout_batches TYPE record<merchants>;
DEFINE FIELD status ON payout_batches TYPE string DEFAULT 'created';
DEFINE FIELD currency ON payout_batches TYPE string DEFAULT 'USD';
DEFINE FIELD total_amount ON payout_batches TYPE decimal DEFAULT 0;
DEFINE FIELD provider ON payout_batches TYPE option<string>;
DEFINE FIELD provider_reference ON payout_batches TYPE option<string>;
DEFINE FIELD scheduled_at ON payout_batches TYPE option<datetime>;
DEFINE FIELD paid_at ON payout_batches TYPE option<datetime>;
DEFINE FIELD created_at ON payout_batches TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON payout_batches TYPE datetime VALUE time::now();
DEFINE INDEX payout_batches_merchant ON payout_batches FIELDS merchant;
DEFINE INDEX payout_batches_status ON payout_batches FIELDS status;

DEFINE TABLE payout_items SCHEMAFULL;
DEFINE FIELD batch ON payout_items TYPE record<payout_batches>;
DEFINE FIELD ledger_entry ON payout_items TYPE record<settlement_ledger_entries>;
DEFINE FIELD amount ON payout_items TYPE decimal;
DEFINE FIELD currency ON payout_items TYPE string DEFAULT 'USD';
DEFINE FIELD created_at ON payout_items TYPE datetime DEFAULT time::now();
DEFINE INDEX payout_items_batch ON payout_items FIELDS batch;
DEFINE INDEX payout_items_ledger ON payout_items FIELDS ledger_entry UNIQUE;

DEFINE FUNCTION fn::record_order_settlement($order: record<orders>, $payment: record<payments>) {
  LET $order_rows = SELECT * FROM $order;
  IF array::len($order_rows) = 0 { THROW 'Order not found'; };
  LET $o = $order_rows[0];

  LET $rule_rows = SELECT * FROM commission_rules WHERE tenant_id = $o.tenant_id AND (merchant = $o.merchant OR merchant = NONE) AND is_active = true LIMIT 1;
  LET $rule = IF array::len($rule_rows) > 0 THEN $rule_rows[0] ELSE { rate: 0, fixed_fee: 0 } END;
  LET $commission = $o.price * $rule.rate;
  LET $fee = $rule.fixed_fee;
  LET $net = math::max(0, $o.price - $commission - $fee);

  RETURN CREATE settlement_ledger_entries CONTENT {
    tenant_id: $o.tenant_id,
    merchant: $o.merchant,
    order: $order,
    payment: $payment,
    entry_type: 'order_sale',
    gross_amount: $o.price,
    commission_amount: $commission,
    fee_amount: $fee,
    net_amount: $net,
    currency: $o.priceCurrency,
    status: 'pending'
  };
};

DEFINE FUNCTION fn::create_payout_batch($merchant: record<merchants>, $currency: string) {
  IF $auth.role != 'admin' { THROW 'Admin role required'; };

  LET $entries = SELECT * FROM settlement_ledger_entries WHERE merchant = $merchant AND currency = $currency AND status = 'pending';
  LET $total = math::sum($entries.net_amount);

  LET $batch = CREATE payout_batches CONTENT {
    tenant_id: $auth.tenant_id,
    merchant: $merchant,
    currency: $currency,
    total_amount: $total,
    status: 'created'
  };

  FOR $entry IN $entries {
    CREATE payout_items CONTENT {
      batch: $batch.id,
      ledger_entry: $entry.id,
      amount: $entry.net_amount,
      currency: $entry.currency
    };
    UPDATE $entry.id MERGE { status: 'batched' };
  };

  RETURN $batch;
};

DEFINE FUNCTION fn::mark_payout_paid($batch: record<payout_batches>, $provider: string, $provider_reference: option<string>) {
  IF $auth.role != 'admin' { THROW 'Admin role required'; };

  LET $batch_rows = SELECT * FROM $batch;
  IF array::len($batch_rows) = 0 { THROW 'Payout batch not found'; };
  LET $b = $batch_rows[0];

  UPDATE $batch MERGE {
    status: 'paid',
    provider: $provider,
    provider_reference: $provider_reference,
    paid_at: time::now()
  };

  LET $items = SELECT * FROM payout_items WHERE batch = $batch;
  FOR $item IN $items {
    UPDATE $item.ledger_entry MERGE { status: 'paid' };
  };

  CREATE commerce_actions CONTENT {
    schema_context: 'https://schema.org',
    schema_type: 'PayAction',
    schema_url: 'https://schema.org/PayAction',
    schema_parent: 'https://schema.org/TradeAction',
    agent: $auth.id,
    object: $batch,
    actionStatus: 'https://schema.org/CompletedActionStatus',
    tenant_id: $b.tenant_id,
    metadata: { flow: 'settlement_payout', provider: $provider, provider_reference: $provider_reference }
  };

  RETURN SELECT * FROM $batch;
};
