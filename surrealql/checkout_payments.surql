-- Checkout and payment orchestration
-- SurrealDB-first implementation.
-- Grounding:
-- - Buy flow: https://schema.org/BuyAction
-- - Order placement: https://schema.org/OrderAction
-- - Payment: https://schema.org/PayAction / https://schema.org/MoneyTransfer
-- - Order: https://schema.org/Order
-- - Invoice: https://schema.org/Invoice

DEFINE TABLE checkout_sessions SCHEMAFULL;
DEFINE FIELD schema_context ON checkout_sessions TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON checkout_sessions TYPE string DEFAULT 'BuyAction';
DEFINE FIELD schema_url ON checkout_sessions TYPE string VALUE 'https://schema.org/BuyAction';
DEFINE FIELD tenant_id ON checkout_sessions TYPE string;
DEFINE FIELD customer ON checkout_sessions TYPE record<users>;
DEFINE FIELD merchant ON checkout_sessions TYPE record<merchants>;
DEFINE FIELD status ON checkout_sessions TYPE string DEFAULT 'open';
DEFINE FIELD currency ON checkout_sessions TYPE string DEFAULT 'USD';
DEFINE FIELD subtotal ON checkout_sessions TYPE decimal DEFAULT 0;
DEFINE FIELD discount_total ON checkout_sessions TYPE decimal DEFAULT 0;
DEFINE FIELD tax_total ON checkout_sessions TYPE decimal DEFAULT 0;
DEFINE FIELD shipping_total ON checkout_sessions TYPE decimal DEFAULT 0;
DEFINE FIELD grand_total ON checkout_sessions TYPE decimal DEFAULT 0;
DEFINE FIELD order ON checkout_sessions TYPE option<record<orders>>;
DEFINE FIELD expires_at ON checkout_sessions TYPE option<datetime>;
DEFINE FIELD metadata ON checkout_sessions TYPE object DEFAULT {};
DEFINE FIELD created_at ON checkout_sessions TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON checkout_sessions TYPE datetime VALUE time::now();
DEFINE INDEX checkout_sessions_customer ON checkout_sessions FIELDS customer;
DEFINE INDEX checkout_sessions_merchant ON checkout_sessions FIELDS merchant;
DEFINE INDEX checkout_sessions_status ON checkout_sessions FIELDS status;

DEFINE TABLE checkout_items SCHEMAFULL;
DEFINE FIELD session ON checkout_items TYPE record<checkout_sessions>;
DEFINE FIELD offer ON checkout_items TYPE record<offers>;
DEFINE FIELD product ON checkout_items TYPE record<products>;
DEFINE FIELD quantity ON checkout_items TYPE int DEFAULT 1;
DEFINE FIELD unit_price ON checkout_items TYPE decimal;
DEFINE FIELD currency ON checkout_items TYPE string DEFAULT 'USD';
DEFINE FIELD line_total ON checkout_items TYPE decimal VALUE unit_price * quantity;
DEFINE FIELD created_at ON checkout_items TYPE datetime DEFAULT time::now();
DEFINE INDEX checkout_items_session ON checkout_items FIELDS session;
DEFINE INDEX checkout_items_offer ON checkout_items FIELDS offer;

DEFINE TABLE payment_intents SCHEMAFULL;
DEFINE FIELD schema_context ON payment_intents TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON payment_intents TYPE string DEFAULT 'PayAction';
DEFINE FIELD schema_url ON payment_intents TYPE string VALUE 'https://schema.org/PayAction';
DEFINE FIELD tenant_id ON payment_intents TYPE string;
DEFINE FIELD session ON payment_intents TYPE record<checkout_sessions>;
DEFINE FIELD customer ON payment_intents TYPE record<users>;
DEFINE FIELD merchant ON payment_intents TYPE record<merchants>;
DEFINE FIELD provider ON payment_intents TYPE string;
DEFINE FIELD amount ON payment_intents TYPE decimal;
DEFINE FIELD currency ON payment_intents TYPE string DEFAULT 'USD';
DEFINE FIELD status ON payment_intents TYPE string DEFAULT 'created';
DEFINE FIELD idempotency_key ON payment_intents TYPE string;
DEFINE FIELD provider_reference ON payment_intents TYPE option<string>;
DEFINE FIELD metadata ON payment_intents TYPE object DEFAULT {};
DEFINE FIELD created_at ON payment_intents TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON payment_intents TYPE datetime VALUE time::now();
DEFINE INDEX payment_intents_session ON payment_intents FIELDS session;
DEFINE INDEX payment_intents_idempotency UNIQUE ON payment_intents FIELDS idempotency_key;
DEFINE INDEX payment_intents_status ON payment_intents FIELDS status;

DEFINE TABLE promotion_redemptions SCHEMAFULL;
DEFINE FIELD session ON promotion_redemptions TYPE record<checkout_sessions>;
DEFINE FIELD code ON promotion_redemptions TYPE string;
DEFINE FIELD amount ON promotion_redemptions TYPE decimal DEFAULT 0;
DEFINE FIELD created_at ON promotion_redemptions TYPE datetime DEFAULT time::now();
DEFINE INDEX promotion_redemptions_session ON promotion_redemptions FIELDS session;

DEFINE TABLE tax_lines SCHEMAFULL;
DEFINE FIELD session ON tax_lines TYPE record<checkout_sessions>;
DEFINE FIELD name ON tax_lines TYPE string;
DEFINE FIELD rate ON tax_lines TYPE decimal DEFAULT 0;
DEFINE FIELD amount ON tax_lines TYPE decimal DEFAULT 0;
DEFINE FIELD created_at ON tax_lines TYPE datetime DEFAULT time::now();
DEFINE INDEX tax_lines_session ON tax_lines FIELDS session;

DEFINE TABLE checkout_session_has_item TYPE RELATION IN checkout_sessions OUT checkout_items SCHEMAFULL;
DEFINE FIELD created_at ON checkout_session_has_item TYPE datetime DEFAULT time::now();

DEFINE TABLE checkout_session_has_payment_intent TYPE RELATION IN checkout_sessions OUT payment_intents SCHEMAFULL;
DEFINE FIELD created_at ON checkout_session_has_payment_intent TYPE datetime DEFAULT time::now();

DEFINE TABLE checkout_session_created_order TYPE RELATION IN checkout_sessions OUT orders SCHEMAFULL;
DEFINE FIELD created_at ON checkout_session_created_order TYPE datetime DEFAULT time::now();

DEFINE TABLE checkout_sessions PERMISSIONS
  FOR select WHERE $auth.role = 'admin' OR tenant_id = $auth.tenant_id OR customer = $auth.id,
  FOR create WHERE $auth.id != NONE,
  FOR update WHERE $auth.role = 'admin' OR customer = $auth.id,
  FOR delete WHERE $auth.role = 'admin';

DEFINE TABLE checkout_items PERMISSIONS
  FOR select WHERE $auth.role = 'admin' OR session.customer = $auth.id,
  FOR create WHERE $auth.id != NONE,
  FOR update WHERE $auth.role = 'admin' OR session.customer = $auth.id,
  FOR delete WHERE $auth.role = 'admin' OR session.customer = $auth.id;

DEFINE TABLE payment_intents PERMISSIONS
  FOR select WHERE $auth.role = 'admin' OR customer = $auth.id,
  FOR create WHERE $auth.id != NONE,
  FOR update WHERE $auth.role = 'admin',
  FOR delete WHERE false;

UPSERT schema_classes:BuyAction CONTENT { name: 'BuyAction', url: 'https://schema.org/BuyAction', parent: schema_classes:TradeAction };
UPSERT schema_classes:OrderAction CONTENT { name: 'OrderAction', url: 'https://schema.org/OrderAction', parent: schema_classes:TradeAction };
UPSERT schema_classes:PayAction CONTENT { name: 'PayAction', url: 'https://schema.org/PayAction', parent: schema_classes:TradeAction };
UPSERT schema_classes:MoneyTransfer CONTENT { name: 'MoneyTransfer', url: 'https://schema.org/MoneyTransfer', parent: schema_classes:TransferAction };

UPSERT app_tables:checkout_sessions CONTENT { name: 'checkout_sessions', purpose: 'Checkout and cart sessions', primary_schema_class: schema_classes:BuyAction };
UPSERT app_tables:checkout_items CONTENT { name: 'checkout_items', purpose: 'Line items in checkout sessions', primary_schema_class: schema_classes:Offer };
UPSERT app_tables:payment_intents CONTENT { name: 'payment_intents', purpose: 'Payment authorization/capture intents', primary_schema_class: schema_classes:PayAction };
RELATE app_tables:checkout_sessions->table_implements->schema_classes:BuyAction;
RELATE app_tables:payment_intents->table_implements->schema_classes:PayAction;

UPSERT defined_term_sets:CheckoutSessionStatus CONTENT { name: 'CheckoutSessionStatus', url: 'https://agennext.dev/defined-terms/CheckoutSessionStatus', description: 'Checkout session lifecycle statuses.' };
UPSERT defined_terms:CheckoutOpen CONTENT { name: 'open', termCode: 'open', url: 'https://agennext.dev/defined-terms/checkout-status/open', inDefinedTermSet: defined_term_sets:CheckoutSessionStatus };
UPSERT defined_terms:CheckoutPaymentPending CONTENT { name: 'payment_pending', termCode: 'payment_pending', url: 'https://agennext.dev/defined-terms/checkout-status/payment-pending', inDefinedTermSet: defined_term_sets:CheckoutSessionStatus };
UPSERT defined_terms:CheckoutCompleted CONTENT { name: 'completed', termCode: 'completed', url: 'https://agennext.dev/defined-terms/checkout-status/completed', inDefinedTermSet: defined_term_sets:CheckoutSessionStatus };
UPSERT defined_terms:CheckoutAbandoned CONTENT { name: 'abandoned', termCode: 'abandoned', url: 'https://agennext.dev/defined-terms/checkout-status/abandoned', inDefinedTermSet: defined_term_sets:CheckoutSessionStatus };

DEFINE FUNCTION fn::create_checkout_session($data: object) {
  RETURN CREATE checkout_sessions CONTENT {
    tenant_id: $data.tenant_id,
    customer: $auth.id,
    merchant: $data.merchant,
    currency: $data.currency ?? 'USD',
    status: 'open',
    expires_at: $data.expires_at,
    metadata: $data.metadata ?? {}
  };
};

DEFINE FUNCTION fn::add_checkout_item($session: record<checkout_sessions>, $offer: record<offers>, $quantity: int) {
  LET $offer_rows = SELECT * FROM $offer;
  IF array::len($offer_rows) = 0 { THROW 'Offer not found'; };
  LET $o = $offer_rows[0];
  LET $item = CREATE checkout_items CONTENT {
    session: $session,
    offer: $offer,
    product: $o.itemOffered,
    quantity: $quantity,
    unit_price: $o.price,
    currency: $o.priceCurrency
  };
  RELATE $session->checkout_session_has_item->$item.id;
  RETURN fn::recalculate_checkout_session($session);
};

DEFINE FUNCTION fn::recalculate_checkout_session($session: record<checkout_sessions>) {
  LET $items = SELECT * FROM checkout_items WHERE session = $session;
  LET $subtotal = math::sum($items.line_total);
  LET $discounts = SELECT * FROM promotion_redemptions WHERE session = $session;
  LET $taxes = SELECT * FROM tax_lines WHERE session = $session;
  LET $discount_total = math::sum($discounts.amount);
  LET $tax_total = math::sum($taxes.amount);
  LET $grand_total = math::max(0, $subtotal - $discount_total + $tax_total);
  UPDATE $session MERGE { subtotal: $subtotal, discount_total: $discount_total, tax_total: $tax_total, grand_total: $grand_total };
  RETURN SELECT * FROM $session;
};

DEFINE FUNCTION fn::create_payment_intent($session: record<checkout_sessions>, $provider: string, $idempotency_key: string) {
  LET $session_rows = SELECT * FROM $session;
  IF array::len($session_rows) = 0 { THROW 'Checkout session not found'; };
  LET $s = $session_rows[0];
  LET $intent = CREATE payment_intents CONTENT {
    tenant_id: $s.tenant_id,
    session: $session,
    customer: $s.customer,
    merchant: $s.merchant,
    provider: $provider,
    amount: $s.grand_total,
    currency: $s.currency,
    status: 'created',
    idempotency_key: $idempotency_key
  };
  RELATE $session->checkout_session_has_payment_intent->$intent.id;
  UPDATE $session MERGE { status: 'payment_pending' };
  RETURN $intent;
};

DEFINE FUNCTION fn::mark_payment_captured($payment_intent: record<payment_intents>, $provider_reference: option<string>) {
  LET $intent_rows = SELECT * FROM $payment_intent;
  IF array::len($intent_rows) = 0 { THROW 'Payment intent not found'; };
  LET $intent = $intent_rows[0];
  UPDATE $payment_intent MERGE { status: 'captured', provider_reference: $provider_reference };
  RETURN fn::place_order_from_checkout($intent.session, $payment_intent);
};

DEFINE FUNCTION fn::place_order_from_checkout($session: record<checkout_sessions>, $payment_intent: record<payment_intents>) {
  LET $session_rows = SELECT * FROM $session;
  IF array::len($session_rows) = 0 { THROW 'Checkout session not found'; };
  LET $s = $session_rows[0];
  LET $items = SELECT * FROM checkout_items WHERE session = $session;
  IF array::len($items) = 0 { THROW 'Checkout has no items'; };

  LET $order = CREATE orders CONTENT {
    schema_context: 'https://schema.org',
    schema_type: 'Order',
    orderNumber: string::concat('ORD-', rand::string(12)),
    orderStatus: 'https://schema.org/OrderProcessing',
    customer: $s.customer,
    merchant: $s.merchant,
    tenant_id: $s.tenant_id,
    acceptedOffer: $items.offer,
    orderedItem: $items,
    price: $s.grand_total,
    priceCurrency: $s.currency,
    paymentStatus: 'captured'
  };

  CREATE invoices CONTENT {
    schema_context: 'https://schema.org',
    schema_type: 'Invoice',
    customer: $s.customer,
    provider: $s.merchant,
    referencesOrder: $order.id,
    totalPaymentDue: $s.grand_total,
    paymentStatus: 'captured',
    scheduledPaymentDate: time::now()
  };

  CREATE payments CONTENT {
    tenant_id: $s.tenant_id,
    order: $order.id,
    provider: $intent.provider,
    amount: $s.grand_total,
    currency: $s.currency,
    status: 'captured',
    idempotency_key: $intent.idempotency_key,
    provider_reference: $intent.provider_reference
  };

  UPDATE $session MERGE { status: 'completed', order: $order.id };
  RELATE $session->checkout_session_created_order->$order.id;

  CREATE commerce_actions CONTENT {
    schema_context: 'https://schema.org',
    schema_type: 'OrderAction',
    schema_url: 'https://schema.org/OrderAction',
    schema_parent: 'https://schema.org/TradeAction',
    agent: $s.customer,
    object: $session,
    result: [$order.id],
    actionStatus: 'https://schema.org/CompletedActionStatus',
    tenant_id: $s.tenant_id,
    metadata: { flow: 'checkout', payment_intent: $payment_intent }
  };

  RETURN $order;
};

UPSERT kg_validation_rules:checkout_session_required_fields CONTENT {
  name: 'checkout_session_required_fields',
  description: 'Checkout sessions must include tenant_id, customer, merchant, status, currency, and grand_total.',
  severity: 'error',
  query: 'SELECT * FROM checkout_sessions WHERE tenant_id = NONE OR customer = NONE OR merchant = NONE OR status = NONE OR currency = NONE OR grand_total = NONE;'
};

UPSERT kg_validation_rules:payment_intent_required_fields CONTENT {
  name: 'payment_intent_required_fields',
  description: 'Payment intents must include session, customer, merchant, provider, amount, currency, status, and idempotency_key.',
  severity: 'error',
  query: 'SELECT * FROM payment_intents WHERE session = NONE OR customer = NONE OR merchant = NONE OR provider = NONE OR amount = NONE OR currency = NONE OR status = NONE OR idempotency_key = NONE;'
};
