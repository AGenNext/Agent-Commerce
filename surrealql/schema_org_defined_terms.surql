-- Schema.org DefinedTerm / Enumeration / accepted-value metamodel
-- Grounds controlled values, statuses, enumerations, and vocabularies in the KG.

-- ============================================================
-- Defined term sets and terms
-- Schema.org: DefinedTermSet, DefinedTerm, Enumeration
-- ============================================================

DEFINE TABLE defined_term_sets SCHEMAFULL;
DEFINE FIELD schema_context ON defined_term_sets TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON defined_term_sets TYPE string DEFAULT 'DefinedTermSet';
DEFINE FIELD schema_url ON defined_term_sets TYPE string VALUE 'https://schema.org/DefinedTermSet';
DEFINE FIELD name ON defined_term_sets TYPE string;
DEFINE FIELD url ON defined_term_sets TYPE string;
DEFINE FIELD description ON defined_term_sets TYPE option<string>;
DEFINE FIELD source_url ON defined_term_sets TYPE option<string>;
DEFINE FIELD created_at ON defined_term_sets TYPE datetime DEFAULT time::now();
DEFINE INDEX defined_term_sets_name_unique ON defined_term_sets FIELDS name UNIQUE;
DEFINE INDEX defined_term_sets_url_unique ON defined_term_sets FIELDS url UNIQUE;

DEFINE TABLE defined_terms SCHEMAFULL;
DEFINE FIELD schema_context ON defined_terms TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON defined_terms TYPE string DEFAULT 'DefinedTerm';
DEFINE FIELD schema_url ON defined_terms TYPE string VALUE 'https://schema.org/DefinedTerm';
DEFINE FIELD name ON defined_terms TYPE string;
DEFINE FIELD termCode ON defined_terms TYPE string;
DEFINE FIELD url ON defined_terms TYPE string;
DEFINE FIELD inDefinedTermSet ON defined_terms TYPE record<defined_term_sets>;
DEFINE FIELD sameAs ON defined_terms TYPE option<string>;
DEFINE FIELD description ON defined_terms TYPE option<string>;
DEFINE FIELD created_at ON defined_terms TYPE datetime DEFAULT time::now();
DEFINE INDEX defined_terms_code_unique ON defined_terms FIELDS inDefinedTermSet, termCode UNIQUE;
DEFINE INDEX defined_terms_url_unique ON defined_terms FIELDS url UNIQUE;

DEFINE TABLE field_accepted_values SCHEMAFULL;
DEFINE FIELD field ON field_accepted_values TYPE record<app_fields>;
DEFINE FIELD term_set ON field_accepted_values TYPE record<defined_term_sets>;
DEFINE FIELD required ON field_accepted_values TYPE bool DEFAULT false;
DEFINE FIELD notes ON field_accepted_values TYPE option<string>;
DEFINE FIELD created_at ON field_accepted_values TYPE datetime DEFAULT time::now();
DEFINE INDEX field_accepted_values_unique ON field_accepted_values FIELDS field, term_set UNIQUE;

DEFINE TABLE has_defined_term TYPE RELATION IN defined_term_sets OUT defined_terms SCHEMAFULL;
DEFINE FIELD created_at ON has_defined_term TYPE datetime DEFAULT time::now();

DEFINE TABLE field_accepts_term_set TYPE RELATION IN app_fields OUT defined_term_sets SCHEMAFULL;
DEFINE FIELD required ON field_accepts_term_set TYPE bool DEFAULT false;
DEFINE FIELD created_at ON field_accepts_term_set TYPE datetime DEFAULT time::now();

DEFINE TABLE field_accepts_term TYPE RELATION IN app_fields OUT defined_terms SCHEMAFULL;
DEFINE FIELD created_at ON field_accepts_term TYPE datetime DEFAULT time::now();

-- ============================================================
-- Schema.org / app controlled vocabularies
-- ============================================================

UPSERT defined_term_sets:ActionStatusType CONTENT {
  name: 'ActionStatusType',
  url: 'https://schema.org/ActionStatusType',
  source_url: 'https://schema.org/ActionStatusType',
  description: 'Schema.org action status enumeration values.'
};

UPSERT defined_terms:PotentialActionStatus CONTENT { name: 'PotentialActionStatus', termCode: 'PotentialActionStatus', url: 'https://schema.org/PotentialActionStatus', inDefinedTermSet: defined_term_sets:ActionStatusType };
UPSERT defined_terms:ActiveActionStatus CONTENT { name: 'ActiveActionStatus', termCode: 'ActiveActionStatus', url: 'https://schema.org/ActiveActionStatus', inDefinedTermSet: defined_term_sets:ActionStatusType };
UPSERT defined_terms:CompletedActionStatus CONTENT { name: 'CompletedActionStatus', termCode: 'CompletedActionStatus', url: 'https://schema.org/CompletedActionStatus', inDefinedTermSet: defined_term_sets:ActionStatusType };
UPSERT defined_terms:FailedActionStatus CONTENT { name: 'FailedActionStatus', termCode: 'FailedActionStatus', url: 'https://schema.org/FailedActionStatus', inDefinedTermSet: defined_term_sets:ActionStatusType };

UPSERT defined_term_sets:ItemAvailability CONTENT {
  name: 'ItemAvailability',
  url: 'https://schema.org/ItemAvailability',
  source_url: 'https://schema.org/ItemAvailability',
  description: 'Schema.org item availability enumeration values for Offer.availability.'
};

UPSERT defined_terms:InStock CONTENT { name: 'InStock', termCode: 'InStock', url: 'https://schema.org/InStock', inDefinedTermSet: defined_term_sets:ItemAvailability };
UPSERT defined_terms:OutOfStock CONTENT { name: 'OutOfStock', termCode: 'OutOfStock', url: 'https://schema.org/OutOfStock', inDefinedTermSet: defined_term_sets:ItemAvailability };
UPSERT defined_terms:PreOrder CONTENT { name: 'PreOrder', termCode: 'PreOrder', url: 'https://schema.org/PreOrder', inDefinedTermSet: defined_term_sets:ItemAvailability };
UPSERT defined_terms:PreSale CONTENT { name: 'PreSale', termCode: 'PreSale', url: 'https://schema.org/PreSale', inDefinedTermSet: defined_term_sets:ItemAvailability };
UPSERT defined_terms:LimitedAvailability CONTENT { name: 'LimitedAvailability', termCode: 'LimitedAvailability', url: 'https://schema.org/LimitedAvailability', inDefinedTermSet: defined_term_sets:ItemAvailability };
UPSERT defined_terms:OnlineOnly CONTENT { name: 'OnlineOnly', termCode: 'OnlineOnly', url: 'https://schema.org/OnlineOnly', inDefinedTermSet: defined_term_sets:ItemAvailability };
UPSERT defined_terms:SoldOut CONTENT { name: 'SoldOut', termCode: 'SoldOut', url: 'https://schema.org/SoldOut', inDefinedTermSet: defined_term_sets:ItemAvailability };
UPSERT defined_terms:Discontinued CONTENT { name: 'Discontinued', termCode: 'Discontinued', url: 'https://schema.org/Discontinued', inDefinedTermSet: defined_term_sets:ItemAvailability };

UPSERT defined_term_sets:OrderStatus CONTENT {
  name: 'OrderStatus',
  url: 'https://schema.org/OrderStatus',
  source_url: 'https://schema.org/OrderStatus',
  description: 'Schema.org order status enumeration values.'
};

UPSERT defined_terms:OrderCancelled CONTENT { name: 'OrderCancelled', termCode: 'OrderCancelled', url: 'https://schema.org/OrderCancelled', inDefinedTermSet: defined_term_sets:OrderStatus };
UPSERT defined_terms:OrderDelivered CONTENT { name: 'OrderDelivered', termCode: 'OrderDelivered', url: 'https://schema.org/OrderDelivered', inDefinedTermSet: defined_term_sets:OrderStatus };
UPSERT defined_terms:OrderInTransit CONTENT { name: 'OrderInTransit', termCode: 'OrderInTransit', url: 'https://schema.org/OrderInTransit', inDefinedTermSet: defined_term_sets:OrderStatus };
UPSERT defined_terms:OrderPaymentDue CONTENT { name: 'OrderPaymentDue', termCode: 'OrderPaymentDue', url: 'https://schema.org/OrderPaymentDue', inDefinedTermSet: defined_term_sets:OrderStatus };
UPSERT defined_terms:OrderPickupAvailable CONTENT { name: 'OrderPickupAvailable', termCode: 'OrderPickupAvailable', url: 'https://schema.org/OrderPickupAvailable', inDefinedTermSet: defined_term_sets:OrderStatus };
UPSERT defined_terms:OrderProblem CONTENT { name: 'OrderProblem', termCode: 'OrderProblem', url: 'https://schema.org/OrderProblem', inDefinedTermSet: defined_term_sets:OrderStatus };
UPSERT defined_terms:OrderProcessing CONTENT { name: 'OrderProcessing', termCode: 'OrderProcessing', url: 'https://schema.org/OrderProcessing', inDefinedTermSet: defined_term_sets:OrderStatus };
UPSERT defined_terms:OrderReturned CONTENT { name: 'OrderReturned', termCode: 'OrderReturned', url: 'https://schema.org/OrderReturned', inDefinedTermSet: defined_term_sets:OrderStatus };

UPSERT defined_term_sets:MerchantReturnEnumeration CONTENT {
  name: 'MerchantReturnEnumeration',
  url: 'https://schema.org/MerchantReturnEnumeration',
  source_url: 'https://schema.org/MerchantReturnEnumeration',
  description: 'Schema.org merchant return policy category values.'
};

UPSERT defined_terms:MerchantReturnFiniteReturnWindow CONTENT { name: 'MerchantReturnFiniteReturnWindow', termCode: 'MerchantReturnFiniteReturnWindow', url: 'https://schema.org/MerchantReturnFiniteReturnWindow', inDefinedTermSet: defined_term_sets:MerchantReturnEnumeration };
UPSERT defined_terms:MerchantReturnNotPermitted CONTENT { name: 'MerchantReturnNotPermitted', termCode: 'MerchantReturnNotPermitted', url: 'https://schema.org/MerchantReturnNotPermitted', inDefinedTermSet: defined_term_sets:MerchantReturnEnumeration };
UPSERT defined_terms:MerchantReturnUnlimitedWindow CONTENT { name: 'MerchantReturnUnlimitedWindow', termCode: 'MerchantReturnUnlimitedWindow', url: 'https://schema.org/MerchantReturnUnlimitedWindow', inDefinedTermSet: defined_term_sets:MerchantReturnEnumeration };
UPSERT defined_terms:MerchantReturnUnspecified CONTENT { name: 'MerchantReturnUnspecified', termCode: 'MerchantReturnUnspecified', url: 'https://schema.org/MerchantReturnUnspecified', inDefinedTermSet: defined_term_sets:MerchantReturnEnumeration };

UPSERT defined_term_sets:ReturnFeesEnumeration CONTENT {
  name: 'ReturnFeesEnumeration',
  url: 'https://schema.org/ReturnFeesEnumeration',
  source_url: 'https://schema.org/ReturnFeesEnumeration',
  description: 'Schema.org return fee values.'
};

UPSERT defined_terms:FreeReturn CONTENT { name: 'FreeReturn', termCode: 'FreeReturn', url: 'https://schema.org/FreeReturn', inDefinedTermSet: defined_term_sets:ReturnFeesEnumeration };
UPSERT defined_terms:ReturnFeesCustomerResponsibility CONTENT { name: 'ReturnFeesCustomerResponsibility', termCode: 'ReturnFeesCustomerResponsibility', url: 'https://schema.org/ReturnFeesCustomerResponsibility', inDefinedTermSet: defined_term_sets:ReturnFeesEnumeration };
UPSERT defined_terms:ReturnShippingFees CONTENT { name: 'ReturnShippingFees', termCode: 'ReturnShippingFees', url: 'https://schema.org/ReturnShippingFees', inDefinedTermSet: defined_term_sets:ReturnFeesEnumeration };

UPSERT defined_term_sets:RefundTypeEnumeration CONTENT {
  name: 'RefundTypeEnumeration',
  url: 'https://schema.org/RefundTypeEnumeration',
  source_url: 'https://schema.org/RefundTypeEnumeration',
  description: 'Schema.org refund type values.'
};

UPSERT defined_terms:ExchangeRefund CONTENT { name: 'ExchangeRefund', termCode: 'ExchangeRefund', url: 'https://schema.org/ExchangeRefund', inDefinedTermSet: defined_term_sets:RefundTypeEnumeration };
UPSERT defined_terms:FullRefund CONTENT { name: 'FullRefund', termCode: 'FullRefund', url: 'https://schema.org/FullRefund', inDefinedTermSet: defined_term_sets:RefundTypeEnumeration };
UPSERT defined_terms:StoreCreditRefund CONTENT { name: 'StoreCreditRefund', termCode: 'StoreCreditRefund', url: 'https://schema.org/StoreCreditRefund', inDefinedTermSet: defined_term_sets:RefundTypeEnumeration };

-- App-specific but grounded as DefinedTermSet, not loose strings.
UPSERT defined_term_sets:PaymentStatus CONTENT {
  name: 'PaymentStatus',
  url: 'https://agennext.dev/defined-terms/PaymentStatus',
  description: 'Agent-Commerce payment lifecycle statuses.'
};

UPSERT defined_terms:PaymentCreated CONTENT { name: 'created', termCode: 'created', url: 'https://agennext.dev/defined-terms/payment-status/created', inDefinedTermSet: defined_term_sets:PaymentStatus };
UPSERT defined_terms:PaymentPending CONTENT { name: 'pending', termCode: 'pending', url: 'https://agennext.dev/defined-terms/payment-status/pending', inDefinedTermSet: defined_term_sets:PaymentStatus };
UPSERT defined_terms:PaymentAuthorized CONTENT { name: 'authorized', termCode: 'authorized', url: 'https://agennext.dev/defined-terms/payment-status/authorized', inDefinedTermSet: defined_term_sets:PaymentStatus };
UPSERT defined_terms:PaymentCaptured CONTENT { name: 'captured', termCode: 'captured', url: 'https://agennext.dev/defined-terms/payment-status/captured', inDefinedTermSet: defined_term_sets:PaymentStatus };
UPSERT defined_terms:PaymentFailed CONTENT { name: 'failed', termCode: 'failed', url: 'https://agennext.dev/defined-terms/payment-status/failed', inDefinedTermSet: defined_term_sets:PaymentStatus };
UPSERT defined_terms:PaymentRefunded CONTENT { name: 'refunded', termCode: 'refunded', url: 'https://agennext.dev/defined-terms/payment-status/refunded', inDefinedTermSet: defined_term_sets:PaymentStatus };

UPSERT defined_term_sets:CurrencyCode CONTENT {
  name: 'CurrencyCode',
  url: 'https://schema.org/priceCurrency',
  description: 'ISO 4217 currency codes accepted for priceCurrency/currency fields.'
};

UPSERT defined_terms:USD CONTENT { name: 'USD', termCode: 'USD', url: 'https://en.wikipedia.org/wiki/ISO_4217#USD', inDefinedTermSet: defined_term_sets:CurrencyCode };
UPSERT defined_terms:INR CONTENT { name: 'INR', termCode: 'INR', url: 'https://en.wikipedia.org/wiki/ISO_4217#INR', inDefinedTermSet: defined_term_sets:CurrencyCode };
UPSERT defined_terms:EUR CONTENT { name: 'EUR', termCode: 'EUR', url: 'https://en.wikipedia.org/wiki/ISO_4217#EUR', inDefinedTermSet: defined_term_sets:CurrencyCode };
UPSERT defined_terms:GBP CONTENT { name: 'GBP', termCode: 'GBP', url: 'https://en.wikipedia.org/wiki/ISO_4217#GBP', inDefinedTermSet: defined_term_sets:CurrencyCode };

-- Term set membership graph
RELATE defined_term_sets:ActionStatusType->has_defined_term->defined_terms:PotentialActionStatus;
RELATE defined_term_sets:ActionStatusType->has_defined_term->defined_terms:ActiveActionStatus;
RELATE defined_term_sets:ActionStatusType->has_defined_term->defined_terms:CompletedActionStatus;
RELATE defined_term_sets:ActionStatusType->has_defined_term->defined_terms:FailedActionStatus;
RELATE defined_term_sets:ItemAvailability->has_defined_term->defined_terms:InStock;
RELATE defined_term_sets:ItemAvailability->has_defined_term->defined_terms:OutOfStock;
RELATE defined_term_sets:ItemAvailability->has_defined_term->defined_terms:PreOrder;
RELATE defined_term_sets:ItemAvailability->has_defined_term->defined_terms:PreSale;
RELATE defined_term_sets:ItemAvailability->has_defined_term->defined_terms:LimitedAvailability;
RELATE defined_term_sets:ItemAvailability->has_defined_term->defined_terms:OnlineOnly;
RELATE defined_term_sets:ItemAvailability->has_defined_term->defined_terms:SoldOut;
RELATE defined_term_sets:ItemAvailability->has_defined_term->defined_terms:Discontinued;
RELATE defined_term_sets:OrderStatus->has_defined_term->defined_terms:OrderCancelled;
RELATE defined_term_sets:OrderStatus->has_defined_term->defined_terms:OrderDelivered;
RELATE defined_term_sets:OrderStatus->has_defined_term->defined_terms:OrderInTransit;
RELATE defined_term_sets:OrderStatus->has_defined_term->defined_terms:OrderPaymentDue;
RELATE defined_term_sets:OrderStatus->has_defined_term->defined_terms:OrderPickupAvailable;
RELATE defined_term_sets:OrderStatus->has_defined_term->defined_terms:OrderProblem;
RELATE defined_term_sets:OrderStatus->has_defined_term->defined_terms:OrderProcessing;
RELATE defined_term_sets:OrderStatus->has_defined_term->defined_terms:OrderReturned;

-- Field accepted-value bindings. These assume app_fields from schema_org_metamodel.surql exist.
UPSERT field_accepted_values:commerce_actions_actionStatus CONTENT { field: app_fields:actions_actionStatus, term_set: defined_term_sets:ActionStatusType, required: true };
UPSERT field_accepted_values:offers_availability CONTENT { field: app_fields:offers_availability, term_set: defined_term_sets:ItemAvailability, required: false };
UPSERT field_accepted_values:orders_orderStatus CONTENT { field: app_fields:orders_orderStatus, term_set: defined_term_sets:OrderStatus, required: false };
UPSERT field_accepted_values:orders_priceCurrency CONTENT { field: app_fields:offers_priceCurrency, term_set: defined_term_sets:CurrencyCode, required: true };

RELATE app_fields:actions_actionStatus->field_accepts_term_set->defined_term_sets:ActionStatusType SET required = true;
RELATE app_fields:offers_availability->field_accepts_term_set->defined_term_sets:ItemAvailability;
RELATE app_fields:orders_orderStatus->field_accepts_term_set->defined_term_sets:OrderStatus;
RELATE app_fields:offers_priceCurrency->field_accepts_term_set->defined_term_sets:CurrencyCode SET required = true;

-- Validation rules for accepted values.
UPSERT kg_validation_rules:action_status_values_are_defined CONTENT {
  name: 'action_status_values_are_defined',
  description: 'commerce_actions.actionStatus should be one of the Schema.org ActionStatusType URLs.',
  severity: 'error',
  query: 'SELECT * FROM commerce_actions WHERE actionStatus NOT IN (SELECT VALUE url FROM defined_terms WHERE inDefinedTermSet = defined_term_sets:ActionStatusType);'
};

UPSERT kg_validation_rules:offer_availability_values_are_defined CONTENT {
  name: 'offer_availability_values_are_defined',
  description: 'offers.availability should be one of the Schema.org ItemAvailability URLs.',
  severity: 'error',
  query: 'SELECT * FROM offers WHERE availability NOT IN (SELECT VALUE url FROM defined_terms WHERE inDefinedTermSet = defined_term_sets:ItemAvailability);'
};

UPSERT kg_validation_rules:order_status_values_are_defined CONTENT {
  name: 'order_status_values_are_defined',
  description: 'orders.orderStatus should be one of the Schema.org OrderStatus URLs.',
  severity: 'error',
  query: 'SELECT * FROM orders WHERE orderStatus NOT IN (SELECT VALUE url FROM defined_terms WHERE inDefinedTermSet = defined_term_sets:OrderStatus);'
};

-- Permissions
DEFINE TABLE defined_term_sets PERMISSIONS FOR select WHERE true, FOR create, update, delete WHERE $auth.role = 'admin';
DEFINE TABLE defined_terms PERMISSIONS FOR select WHERE true, FOR create, update, delete WHERE $auth.role = 'admin';
DEFINE TABLE field_accepted_values PERMISSIONS FOR select WHERE true, FOR create, update, delete WHERE $auth.role = 'admin';
