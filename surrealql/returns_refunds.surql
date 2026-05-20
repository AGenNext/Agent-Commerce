-- Returns and refunds
-- SurrealDB-first implementation.
-- Grounding:
-- - Return workflow: https://schema.org/ReturnAction
-- - Merchant return policy: https://schema.org/MerchantReturnPolicy
-- - Refunds: https://schema.org/RefundTypeEnumeration

DEFINE TABLE return_requests SCHEMAFULL;
DEFINE FIELD schema_context ON return_requests TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON return_requests TYPE string DEFAULT 'ReturnAction';
DEFINE FIELD schema_url ON return_requests TYPE string VALUE 'https://schema.org/ReturnAction';
DEFINE FIELD tenant_id ON return_requests TYPE string;
DEFINE FIELD order ON return_requests TYPE record<orders>;
DEFINE FIELD customer ON return_requests TYPE record<users>;
DEFINE FIELD merchant ON return_requests TYPE record<merchants>;
DEFINE FIELD reason ON return_requests TYPE string;
DEFINE FIELD status ON return_requests TYPE string DEFAULT 'requested';
DEFINE FIELD review_notes ON return_requests TYPE option<string>;
DEFINE FIELD approved_at ON return_requests TYPE option<datetime>;
DEFINE FIELD received_at ON return_requests TYPE option<datetime>;
DEFINE FIELD refund_total ON return_requests TYPE decimal DEFAULT 0;
DEFINE FIELD created_at ON return_requests TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON return_requests TYPE datetime VALUE time::now();
DEFINE INDEX return_requests_order ON return_requests FIELDS order;
DEFINE INDEX return_requests_customer ON return_requests FIELDS customer;
DEFINE INDEX return_requests_status ON return_requests FIELDS status;

DEFINE TABLE return_items SCHEMAFULL;
DEFINE FIELD return_request ON return_items TYPE record<return_requests>;
DEFINE FIELD order_item_ref ON return_items TYPE option<string>;
DEFINE FIELD product ON return_items TYPE record<products>;
DEFINE FIELD quantity ON return_items TYPE int DEFAULT 1;
DEFINE FIELD unit_refund_amount ON return_items TYPE decimal DEFAULT 0;
DEFINE FIELD line_refund_total ON return_items TYPE decimal VALUE quantity * unit_refund_amount;
DEFINE FIELD condition_notes ON return_items TYPE option<string>;
DEFINE FIELD created_at ON return_items TYPE datetime DEFAULT time::now();
DEFINE INDEX return_items_request ON return_items FIELDS return_request;

DEFINE TABLE refund_intents SCHEMAFULL;
DEFINE FIELD schema_context ON refund_intents TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON refund_intents TYPE string DEFAULT 'MoneyTransfer';
DEFINE FIELD schema_url ON refund_intents TYPE string VALUE 'https://schema.org/MoneyTransfer';
DEFINE FIELD tenant_id ON refund_intents TYPE string;
DEFINE FIELD return_request ON refund_intents TYPE record<return_requests>;
DEFINE FIELD payment ON refund_intents TYPE option<record<payments>>;
DEFINE FIELD provider ON refund_intents TYPE string;
DEFINE FIELD amount ON refund_intents TYPE decimal;
DEFINE FIELD currency ON refund_intents TYPE string DEFAULT 'USD';
DEFINE FIELD refund_type ON refund_intents TYPE string DEFAULT 'FullRefund';
DEFINE FIELD status ON refund_intents TYPE string DEFAULT 'created';
DEFINE FIELD provider_reference ON refund_intents TYPE option<string>;
DEFINE FIELD created_at ON refund_intents TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON refund_intents TYPE datetime VALUE time::now();
DEFINE INDEX refund_intents_request ON refund_intents FIELDS return_request;
DEFINE INDEX refund_intents_status ON refund_intents FIELDS status;

DEFINE TABLE merchant_return_policies SCHEMAFULL;
DEFINE FIELD schema_context ON merchant_return_policies TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON merchant_return_policies TYPE string DEFAULT 'MerchantReturnPolicy';
DEFINE FIELD schema_url ON merchant_return_policies TYPE string VALUE 'https://schema.org/MerchantReturnPolicy';
DEFINE FIELD tenant_id ON merchant_return_policies TYPE string;
DEFINE FIELD merchant ON merchant_return_policies TYPE record<merchants>;
DEFINE FIELD returnPolicyCategory ON merchant_return_policies TYPE string;
DEFINE FIELD merchantReturnDays ON merchant_return_policies TYPE int DEFAULT 30;
DEFINE FIELD returnFees ON merchant_return_policies TYPE option<string>;
DEFINE FIELD refundType ON merchant_return_policies TYPE option<string>;
DEFINE FIELD updated_at ON merchant_return_policies TYPE datetime VALUE time::now();
DEFINE INDEX merchant_return_policies_merchant ON merchant_return_policies FIELDS merchant UNIQUE;

DEFINE FUNCTION fn::create_return_request($data: object) {
  LET $request = CREATE return_requests CONTENT {
    tenant_id: $data.tenant_id,
    order: $data.order,
    customer: $auth.id,
    merchant: $data.merchant,
    reason: $data.reason,
    status: 'requested'
  };
  CREATE commerce_actions CONTENT {
    schema_context: 'https://schema.org',
    schema_type: 'ReturnAction',
    schema_url: 'https://schema.org/ReturnAction',
    agent: $auth.id,
    object: $request.id,
    result: [$request.id],
    actionStatus: 'https://schema.org/PotentialActionStatus',
    tenant_id: $data.tenant_id,
    metadata: { flow: 'returns' }
  };
  RETURN $request;
};

DEFINE FUNCTION fn::approve_return_request($return_request: record<return_requests>, $review_notes: option<string>) {
  IF $auth.role != 'admin' { THROW 'Admin role required'; };
  UPDATE $return_request MERGE {
    status: 'approved',
    review_notes: $review_notes,
    approved_at: time::now()
  };
  RETURN SELECT * FROM $return_request;
};

DEFINE FUNCTION fn::create_refund_intent($return_request: record<return_requests>, $provider: string, $amount: decimal, $currency: string) {
  LET $rr = (SELECT * FROM $return_request)[0];
  LET $intent = CREATE refund_intents CONTENT {
    tenant_id: $rr.tenant_id,
    return_request: $return_request,
    provider: $provider,
    amount: $amount,
    currency: $currency,
    status: 'created'
  };
  RETURN $intent;
};

DEFINE FUNCTION fn::mark_refund_completed($refund_intent: record<refund_intents>, $provider_reference: option<string>) {
  LET $intent = (SELECT * FROM $refund_intent)[0];
  UPDATE $refund_intent MERGE {
    status: 'completed',
    provider_reference: $provider_reference
  };
  UPDATE $intent.return_request MERGE {
    status: 'refunded',
    refund_total: $intent.amount
  };
  CREATE commerce_actions CONTENT {
    schema_context: 'https://schema.org',
    schema_type: 'ReturnAction',
    schema_url: 'https://schema.org/ReturnAction',
    agent: $auth.id,
    object: $intent.return_request,
    actionStatus: 'https://schema.org/CompletedActionStatus',
    metadata: { flow: 'returns', refund_intent: $refund_intent }
  };
  RETURN SELECT * FROM $intent.return_request;
};
