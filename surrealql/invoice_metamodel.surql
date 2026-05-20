-- Schema.org Invoice field/property grounding
-- Canonical class: https://schema.org/Invoice

-- Invoice-specific Schema.org properties
UPSERT schema_properties:accountId CONTENT { name: 'accountId', url: 'https://schema.org/accountId', expected_types: ['Text'] };
UPSERT schema_properties:billingPeriod CONTENT { name: 'billingPeriod', url: 'https://schema.org/billingPeriod', expected_types: ['Duration'] };
UPSERT schema_properties:broker CONTENT { name: 'broker', url: 'https://schema.org/broker', expected_types: ['Organization', 'Person'] };
UPSERT schema_properties:confirmationNumber CONTENT { name: 'confirmationNumber', url: 'https://schema.org/confirmationNumber', expected_types: ['Text'] };
UPSERT schema_properties:minimumPaymentDue CONTENT { name: 'minimumPaymentDue', url: 'https://schema.org/minimumPaymentDue', expected_types: ['MonetaryAmount', 'PriceSpecification'] };
UPSERT schema_properties:paymentDueDate CONTENT { name: 'paymentDueDate', url: 'https://schema.org/paymentDueDate', expected_types: ['DateTime'] };
UPSERT schema_properties:paymentMethodId CONTENT { name: 'paymentMethodId', url: 'https://schema.org/paymentMethodId', expected_types: ['Text'] };
UPSERT schema_properties:paymentStatus CONTENT { name: 'paymentStatus', url: 'https://schema.org/paymentStatus', expected_types: ['PaymentStatusType', 'Text'] };
UPSERT schema_properties:provider CONTENT { name: 'provider', url: 'https://schema.org/provider', expected_types: ['Organization', 'Person'] };
UPSERT schema_properties:referencesOrder CONTENT { name: 'referencesOrder', url: 'https://schema.org/referencesOrder', expected_types: ['Order'] };
UPSERT schema_properties:scheduledPaymentDate CONTENT { name: 'scheduledPaymentDate', url: 'https://schema.org/scheduledPaymentDate', expected_types: ['Date'] };
UPSERT schema_properties:totalPaymentDue CONTENT { name: 'totalPaymentDue', url: 'https://schema.org/totalPaymentDue', expected_types: ['MonetaryAmount', 'PriceSpecification'] };

-- Field mappings for invoices table
UPSERT app_fields:invoices_accountId CONTENT { table: app_tables:invoices, name: 'accountId', surreal_type: 'option<string>', schema_property: schema_properties:accountId };
UPSERT app_fields:invoices_billingPeriod CONTENT { table: app_tables:invoices, name: 'billingPeriod', surreal_type: 'option<object>', schema_property: schema_properties:billingPeriod };
UPSERT app_fields:invoices_broker CONTENT { table: app_tables:invoices, name: 'broker', surreal_type: 'option<record>', schema_property: schema_properties:broker, schema_range: [schema_classes:Organization, schema_classes:Person] };
UPSERT app_fields:invoices_category CONTENT { table: app_tables:invoices, name: 'category', surreal_type: 'option<string>', schema_property: schema_properties:category };
UPSERT app_fields:invoices_confirmationNumber CONTENT { table: app_tables:invoices, name: 'confirmationNumber', surreal_type: 'option<string>', schema_property: schema_properties:confirmationNumber };
UPSERT app_fields:invoices_customer CONTENT { table: app_tables:invoices, name: 'customer', surreal_type: 'record<users>', schema_property: schema_properties:customer, schema_range: [schema_classes:Person], required: true };
UPSERT app_fields:invoices_minimumPaymentDue CONTENT { table: app_tables:invoices, name: 'minimumPaymentDue', surreal_type: 'option<decimal>', schema_property: schema_properties:minimumPaymentDue };
UPSERT app_fields:invoices_paymentDueDate CONTENT { table: app_tables:invoices, name: 'paymentDueDate', surreal_type: 'option<datetime>', schema_property: schema_properties:paymentDueDate };
UPSERT app_fields:invoices_paymentMethod CONTENT { table: app_tables:invoices, name: 'paymentMethod', surreal_type: 'option<string>', schema_property: schema_properties:paymentMethod, schema_range: [schema_classes:PaymentMethod] };
UPSERT app_fields:invoices_paymentMethodId CONTENT { table: app_tables:invoices, name: 'paymentMethodId', surreal_type: 'option<string>', schema_property: schema_properties:paymentMethodId };
UPSERT app_fields:invoices_paymentStatus CONTENT { table: app_tables:invoices, name: 'paymentStatus', surreal_type: 'string', schema_property: schema_properties:paymentStatus, required: true };
UPSERT app_fields:invoices_provider CONTENT { table: app_tables:invoices, name: 'provider', surreal_type: 'record<merchants>', schema_property: schema_properties:provider, schema_range: [schema_classes:Organization], required: true };
UPSERT app_fields:invoices_referencesOrder CONTENT { table: app_tables:invoices, name: 'referencesOrder', surreal_type: 'record<orders>', schema_property: schema_properties:referencesOrder, schema_range: [schema_classes:Order], required: true };
UPSERT app_fields:invoices_scheduledPaymentDate CONTENT { table: app_tables:invoices, name: 'scheduledPaymentDate', surreal_type: 'option<datetime>', schema_property: schema_properties:scheduledPaymentDate };
UPSERT app_fields:invoices_totalPaymentDue CONTENT { table: app_tables:invoices, name: 'totalPaymentDue', surreal_type: 'decimal', schema_property: schema_properties:totalPaymentDue, required: true };

-- Field-to-property graph edges
RELATE app_fields:invoices_accountId->field_maps_to->schema_properties:accountId;
RELATE app_fields:invoices_billingPeriod->field_maps_to->schema_properties:billingPeriod;
RELATE app_fields:invoices_broker->field_maps_to->schema_properties:broker;
RELATE app_fields:invoices_category->field_maps_to->schema_properties:category;
RELATE app_fields:invoices_confirmationNumber->field_maps_to->schema_properties:confirmationNumber;
RELATE app_fields:invoices_customer->field_maps_to->schema_properties:customer;
RELATE app_fields:invoices_minimumPaymentDue->field_maps_to->schema_properties:minimumPaymentDue;
RELATE app_fields:invoices_paymentDueDate->field_maps_to->schema_properties:paymentDueDate;
RELATE app_fields:invoices_paymentMethod->field_maps_to->schema_properties:paymentMethod;
RELATE app_fields:invoices_paymentMethodId->field_maps_to->schema_properties:paymentMethodId;
RELATE app_fields:invoices_paymentStatus->field_maps_to->schema_properties:paymentStatus;
RELATE app_fields:invoices_provider->field_maps_to->schema_properties:provider;
RELATE app_fields:invoices_referencesOrder->field_maps_to->schema_properties:referencesOrder;
RELATE app_fields:invoices_scheduledPaymentDate->field_maps_to->schema_properties:scheduledPaymentDate;
RELATE app_fields:invoices_totalPaymentDue->field_maps_to->schema_properties:totalPaymentDue;

-- Accepted value binding for invoice payment status
UPSERT field_accepted_values:invoices_paymentStatus CONTENT { field: app_fields:invoices_paymentStatus, term_set: defined_term_sets:PaymentStatus, required: true };
RELATE app_fields:invoices_paymentStatus->field_accepts_term_set->defined_term_sets:PaymentStatus SET required = true;

-- Invoice validation rules
UPSERT kg_validation_rules:invoice_required_fields CONTENT {
  name: 'invoice_required_fields',
  description: 'Invoices must have customer, provider, referencesOrder, totalPaymentDue, and paymentStatus.',
  severity: 'error',
  query: 'SELECT * FROM invoices WHERE customer = NONE OR provider = NONE OR referencesOrder = NONE OR totalPaymentDue = NONE OR paymentStatus = NONE;'
};

UPSERT kg_validation_rules:invoice_payment_status_values_are_defined CONTENT {
  name: 'invoice_payment_status_values_are_defined',
  description: 'invoices.paymentStatus should be one of the Agent-Commerce PaymentStatus DefinedTerms.',
  severity: 'error',
  query: 'SELECT * FROM invoices WHERE paymentStatus NOT IN (SELECT VALUE termCode FROM defined_terms WHERE inDefinedTermSet = defined_term_sets:PaymentStatus) AND paymentStatus NOT IN (SELECT VALUE url FROM defined_terms WHERE inDefinedTermSet = defined_term_sets:PaymentStatus);'
};
