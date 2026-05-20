-- Schema.org-aligned commerce schema for Agent-Commerce
-- Keeps SurrealDB-native relations while preserving JSON-LD compatibility.

-- ============================================================
-- Core commercial actors
-- Schema.org: Organization, OnlineBusiness, LocalBusiness, Person
-- ============================================================

DEFINE TABLE merchants SCHEMAFULL;
DEFINE FIELD schema_context ON merchants TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON merchants TYPE string DEFAULT 'OnlineBusiness';
DEFINE FIELD schema_url ON merchants TYPE string VALUE string::concat('https://schema.org/', schema_type);
DEFINE FIELD name ON merchants TYPE string;
DEFINE FIELD description ON merchants TYPE option<string>;
DEFINE FIELD url ON merchants TYPE option<string>;
DEFINE FIELD logo ON merchants TYPE option<string>;
DEFINE FIELD email ON merchants TYPE option<string>;
DEFINE FIELD telephone ON merchants TYPE option<string>;
DEFINE FIELD tenant_id ON merchants TYPE string;
DEFINE FIELD address ON merchants TYPE option<object>;
DEFINE FIELD geo ON merchants TYPE option<object>;
DEFINE FIELD created_at ON merchants TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON merchants TYPE datetime VALUE time::now();
DEFINE INDEX merchants_tenant ON merchants FIELDS tenant_id;
DEFINE INDEX merchants_schema_url ON merchants FIELDS schema_url;
DEFINE INDEX merchants_name_search ON merchants FIELDS name SEARCH ANALYZER ascii BM25;

DEFINE TABLE brands SCHEMAFULL;
DEFINE FIELD schema_context ON brands TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON brands TYPE string DEFAULT 'Brand';
DEFINE FIELD schema_url ON brands TYPE string VALUE 'https://schema.org/Brand';
DEFINE FIELD name ON brands TYPE string;
DEFINE FIELD logo ON brands TYPE option<string>;
DEFINE FIELD url ON brands TYPE option<string>;
DEFINE FIELD tenant_id ON brands TYPE option<string>;
DEFINE FIELD created_at ON brands TYPE datetime DEFAULT time::now();
DEFINE INDEX brands_name_unique ON brands FIELDS name UNIQUE;
DEFINE INDEX brands_schema_url ON brands FIELDS schema_url;

DEFINE TABLE products SCHEMAFULL;
DEFINE FIELD schema_context ON products TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON products TYPE string DEFAULT 'Product' ASSERT $value IN ['Product', 'ProductModel', 'ProductGroup', 'IndividualProduct'];
DEFINE FIELD schema_url ON products TYPE string VALUE string::concat('https://schema.org/', schema_type);
DEFINE FIELD name ON products TYPE string;
DEFINE FIELD description ON products TYPE option<string>;
DEFINE FIELD sku ON products TYPE option<string>;
DEFINE FIELD gtin ON products TYPE option<string>;
DEFINE FIELD mpn ON products TYPE option<string>;
DEFINE FIELD category ON products TYPE option<string>;
DEFINE FIELD image ON products TYPE option<array<string>>;
DEFINE FIELD brand ON products TYPE option<record<brands>>;
DEFINE FIELD manufacturer ON products TYPE option<record<merchants>>;
DEFINE FIELD tenant_id ON products TYPE string;
DEFINE FIELD seller ON products TYPE record<merchants>;
DEFINE FIELD product_group_id ON products TYPE option<string>;
DEFINE FIELD variant_attributes ON products TYPE option<object>;
DEFINE FIELD embedding ON products TYPE option<array<float>>;
DEFINE FIELD is_active ON products TYPE bool DEFAULT true;
DEFINE FIELD created_at ON products TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON products TYPE datetime VALUE time::now();
DEFINE INDEX products_sku_unique ON products FIELDS sku UNIQUE;
DEFINE INDEX products_tenant ON products FIELDS tenant_id;
DEFINE INDEX products_schema_url ON products FIELDS schema_url;
DEFINE INDEX products_name_search ON products FIELDS name SEARCH ANALYZER ascii BM25;
DEFINE INDEX products_description_search ON products FIELDS description SEARCH ANALYZER ascii BM25;
DEFINE INDEX products_category ON products FIELDS category;

DEFINE TABLE offers SCHEMAFULL;
DEFINE FIELD schema_context ON offers TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON offers TYPE string DEFAULT 'Offer' ASSERT $value IN ['Offer', 'AggregateOffer', 'Demand', 'PriceSpecification'];
DEFINE FIELD schema_url ON offers TYPE string VALUE string::concat('https://schema.org/', schema_type);
DEFINE FIELD itemOffered ON offers TYPE record<products>;
DEFINE FIELD seller ON offers TYPE record<merchants>;
DEFINE FIELD tenant_id ON offers TYPE string;
DEFINE FIELD price ON offers TYPE decimal;
DEFINE FIELD priceCurrency ON offers TYPE string DEFAULT 'USD';
DEFINE FIELD availability ON offers TYPE string DEFAULT 'https://schema.org/InStock';
DEFINE FIELD validFrom ON offers TYPE option<datetime>;
DEFINE FIELD validThrough ON offers TYPE option<datetime>;
DEFINE FIELD url ON offers TYPE option<string>;
DEFINE FIELD acceptedPaymentMethod ON offers TYPE option<array<string>>;
DEFINE FIELD eligibleQuantity ON offers TYPE option<object>;
DEFINE FIELD created_at ON offers TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON offers TYPE datetime VALUE time::now();
DEFINE INDEX offers_product ON offers FIELDS itemOffered;
DEFINE INDEX offers_seller ON offers FIELDS seller;
DEFINE INDEX offers_tenant ON offers FIELDS tenant_id;
DEFINE INDEX offers_schema_url ON offers FIELDS schema_url;
DEFINE INDEX offers_price ON offers FIELDS price;

DEFINE TABLE orders SCHEMAFULL;
DEFINE FIELD schema_context ON orders TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON orders TYPE string DEFAULT 'Order';
DEFINE FIELD schema_url ON orders TYPE string VALUE 'https://schema.org/Order';
DEFINE FIELD orderNumber ON orders TYPE string;
DEFINE FIELD orderStatus ON orders TYPE string DEFAULT 'https://schema.org/OrderProcessing';
DEFINE FIELD customer ON orders TYPE record<users>;
DEFINE FIELD merchant ON orders TYPE record<merchants>;
DEFINE FIELD tenant_id ON orders TYPE string;
DEFINE FIELD acceptedOffer ON orders TYPE option<array<record<offers>>>;
DEFINE FIELD orderedItem ON orders TYPE array<object>;
DEFINE FIELD price ON orders TYPE decimal;
DEFINE FIELD priceCurrency ON orders TYPE string DEFAULT 'USD';
DEFINE FIELD paymentMethod ON orders TYPE option<string>;
DEFINE FIELD paymentStatus ON orders TYPE string DEFAULT 'pending';
DEFINE FIELD billingAddress ON orders TYPE option<object>;
DEFINE FIELD deliveryAddress ON orders TYPE option<object>;
DEFINE FIELD orderDate ON orders TYPE datetime DEFAULT time::now();
DEFINE FIELD created_at ON orders TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON orders TYPE datetime VALUE time::now();
DEFINE INDEX orders_number_unique ON orders FIELDS orderNumber UNIQUE;
DEFINE INDEX orders_customer ON orders FIELDS customer;
DEFINE INDEX orders_merchant ON orders FIELDS merchant;
DEFINE INDEX orders_tenant ON orders FIELDS tenant_id;
DEFINE INDEX orders_schema_url ON orders FIELDS schema_url;
DEFINE INDEX orders_status ON orders FIELDS orderStatus;

DEFINE TABLE invoices SCHEMAFULL;
DEFINE FIELD schema_context ON invoices TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON invoices TYPE string DEFAULT 'Invoice';
DEFINE FIELD schema_url ON invoices TYPE string VALUE 'https://schema.org/Invoice';
DEFINE FIELD accountId ON invoices TYPE option<string>;
DEFINE FIELD billingPeriod ON invoices TYPE option<object>;
DEFINE FIELD broker ON invoices TYPE option<record>;
DEFINE FIELD category ON invoices TYPE option<string>;
DEFINE FIELD confirmationNumber ON invoices TYPE option<string>;
DEFINE FIELD customer ON invoices TYPE record<users>;
DEFINE FIELD minimumPaymentDue ON invoices TYPE option<decimal>;
DEFINE FIELD paymentDueDate ON invoices TYPE option<datetime>;
DEFINE FIELD paymentMethod ON invoices TYPE option<string>;
DEFINE FIELD paymentMethodId ON invoices TYPE option<string>;
DEFINE FIELD paymentStatus ON invoices TYPE string DEFAULT 'pending';
DEFINE FIELD provider ON invoices TYPE record<merchants>;
DEFINE FIELD referencesOrder ON invoices TYPE record<orders>;
DEFINE FIELD scheduledPaymentDate ON invoices TYPE option<datetime>;
DEFINE FIELD totalPaymentDue ON invoices TYPE decimal;
DEFINE FIELD created_at ON invoices TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON invoices TYPE datetime VALUE time::now();
DEFINE INDEX invoices_order ON invoices FIELDS referencesOrder;
DEFINE INDEX invoices_schema_url ON invoices FIELDS schema_url;
DEFINE INDEX invoices_customer ON invoices FIELDS customer;
DEFINE INDEX invoices_provider ON invoices FIELDS provider;
DEFINE INDEX invoices_payment_status ON invoices FIELDS paymentStatus;
DEFINE INDEX invoices_confirmation_number ON invoices FIELDS confirmationNumber;

DEFINE TABLE payment_methods SCHEMAFULL;
DEFINE FIELD schema_context ON payment_methods TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON payment_methods TYPE string DEFAULT 'PaymentMethod';
DEFINE FIELD schema_url ON payment_methods TYPE string VALUE 'https://schema.org/PaymentMethod';
DEFINE FIELD name ON payment_methods TYPE string;
DEFINE FIELD provider ON payment_methods TYPE string;
DEFINE FIELD tenant_id ON payment_methods TYPE option<string>;
DEFINE FIELD is_active ON payment_methods TYPE bool DEFAULT true;
DEFINE FIELD created_at ON payment_methods TYPE datetime DEFAULT time::now();
DEFINE INDEX payment_methods_provider ON payment_methods FIELDS provider;
DEFINE INDEX payment_methods_schema_url ON payment_methods FIELDS schema_url;

DEFINE TABLE payments SCHEMAFULL;
DEFINE FIELD tenant_id ON payments TYPE string;
DEFINE FIELD order ON payments TYPE record<orders>;
DEFINE FIELD provider ON payments TYPE string;
DEFINE FIELD amount ON payments TYPE decimal;
DEFINE FIELD currency ON payments TYPE string DEFAULT 'USD';
DEFINE FIELD status ON payments TYPE string DEFAULT 'created';
DEFINE FIELD idempotency_key ON payments TYPE string;
DEFINE FIELD provider_reference ON payments TYPE option<string>;
DEFINE FIELD metadata ON payments TYPE object DEFAULT {};
DEFINE FIELD created_at ON payments TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON payments TYPE datetime VALUE time::now();
DEFINE INDEX payments_idempotency_unique ON payments FIELDS idempotency_key UNIQUE;
DEFINE INDEX payments_order ON payments FIELDS order;
DEFINE INDEX payments_status ON payments FIELDS status;

DEFINE TABLE deliveries SCHEMAFULL;
DEFINE FIELD schema_context ON deliveries TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON deliveries TYPE string DEFAULT 'ParcelDelivery';
DEFINE FIELD schema_url ON deliveries TYPE string VALUE 'https://schema.org/ParcelDelivery';
DEFINE FIELD partOfOrder ON deliveries TYPE record<orders>;
DEFINE FIELD provider ON deliveries TYPE option<string>;
DEFINE FIELD trackingNumber ON deliveries TYPE option<string>;
DEFINE FIELD trackingUrl ON deliveries TYPE option<string>;
DEFINE FIELD deliveryStatus ON deliveries TYPE string DEFAULT 'created';
DEFINE FIELD expectedArrivalFrom ON deliveries TYPE option<datetime>;
DEFINE FIELD expectedArrivalUntil ON deliveries TYPE option<datetime>;
DEFINE FIELD originAddress ON deliveries TYPE option<object>;
DEFINE FIELD deliveryAddress ON deliveries TYPE option<object>;
DEFINE FIELD created_at ON deliveries TYPE datetime DEFAULT time::now();
DEFINE INDEX deliveries_order ON deliveries FIELDS partOfOrder;
DEFINE INDEX deliveries_schema_url ON deliveries FIELDS schema_url;

DEFINE TABLE return_policies SCHEMAFULL;
DEFINE FIELD schema_context ON return_policies TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON return_policies TYPE string DEFAULT 'MerchantReturnPolicy';
DEFINE FIELD schema_url ON return_policies TYPE string VALUE 'https://schema.org/MerchantReturnPolicy';
DEFINE FIELD merchant ON return_policies TYPE record<merchants>;
DEFINE FIELD tenant_id ON return_policies TYPE string;
DEFINE FIELD applicableCountry ON return_policies TYPE option<string>;
DEFINE FIELD returnPolicyCategory ON return_policies TYPE option<string>;
DEFINE FIELD merchantReturnDays ON return_policies TYPE option<int>;
DEFINE FIELD returnFees ON return_policies TYPE option<string>;
DEFINE FIELD refundType ON return_policies TYPE option<string>;
DEFINE FIELD created_at ON return_policies TYPE datetime DEFAULT time::now();
DEFINE INDEX return_policies_merchant ON return_policies FIELDS merchant;
DEFINE INDEX return_policies_schema_url ON return_policies FIELDS schema_url;

DEFINE TABLE reviews SCHEMAFULL;
DEFINE FIELD schema_context ON reviews TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON reviews TYPE string DEFAULT 'Review';
DEFINE FIELD schema_url ON reviews TYPE string VALUE 'https://schema.org/Review';
DEFINE FIELD itemReviewed ON reviews TYPE record<products>;
DEFINE FIELD author ON reviews TYPE record<users>;
DEFINE FIELD reviewRating ON reviews TYPE object;
DEFINE FIELD reviewBody ON reviews TYPE option<string>;
DEFINE FIELD tenant_id ON reviews TYPE string;
DEFINE FIELD created_at ON reviews TYPE datetime DEFAULT time::now();
DEFINE INDEX reviews_product ON reviews FIELDS itemReviewed;
DEFINE INDEX reviews_author ON reviews FIELDS author;
DEFINE INDEX reviews_schema_url ON reviews FIELDS schema_url;

DEFINE TABLE sells TYPE RELATION IN merchants OUT products SCHEMAFULL;
DEFINE FIELD tenant_id ON sells TYPE string;
DEFINE FIELD created_at ON sells TYPE datetime DEFAULT time::now();

DEFINE TABLE has_offer TYPE RELATION IN merchants OUT offers SCHEMAFULL;
DEFINE FIELD tenant_id ON has_offer TYPE string;
DEFINE FIELD created_at ON has_offer TYPE datetime DEFAULT time::now();

DEFINE TABLE order_contains TYPE RELATION IN orders OUT products SCHEMAFULL;
DEFINE FIELD quantity ON order_contains TYPE int DEFAULT 1;
DEFINE FIELD unit_price ON order_contains TYPE decimal;
DEFINE FIELD created_at ON order_contains TYPE datetime DEFAULT time::now();

DEFINE TABLE fulfilled_by TYPE RELATION IN orders OUT deliveries SCHEMAFULL;
DEFINE FIELD created_at ON fulfilled_by TYPE datetime DEFAULT time::now();

DEFINE TABLE merchants PERMISSIONS
  FOR select WHERE $auth.role = 'admin' OR tenant_id = $auth.tenant_id,
  FOR create, update, delete WHERE $auth.role = 'admin';

DEFINE TABLE products PERMISSIONS
  FOR select WHERE is_active = true OR $auth.role = 'admin' OR tenant_id = $auth.tenant_id,
  FOR create, update WHERE $auth.role IN ['admin', 'merchant'] AND tenant_id = $auth.tenant_id,
  FOR delete WHERE $auth.role = 'admin';

DEFINE TABLE offers PERMISSIONS
  FOR select WHERE $auth.role = 'admin' OR tenant_id = $auth.tenant_id,
  FOR create, update WHERE $auth.role IN ['admin', 'merchant'] AND tenant_id = $auth.tenant_id,
  FOR delete WHERE $auth.role = 'admin';

DEFINE TABLE orders PERMISSIONS
  FOR select WHERE $auth.role = 'admin' OR tenant_id = $auth.tenant_id OR customer = $auth.id,
  FOR create WHERE $auth.id != NONE,
  FOR update WHERE $auth.role IN ['admin', 'merchant'] AND tenant_id = $auth.tenant_id,
  FOR delete WHERE $auth.role = 'admin';

DEFINE TABLE payments PERMISSIONS
  FOR select WHERE $auth.role = 'admin' OR tenant_id = $auth.tenant_id,
  FOR create WHERE $auth.id != NONE,
  FOR update WHERE $auth.role = 'admin',
  FOR delete WHERE false;

DEFINE TABLE invoices PERMISSIONS
  FOR select WHERE $auth.role = 'admin' OR customer = $auth.id,
  FOR create WHERE $auth.id != NONE,
  FOR update WHERE $auth.role = 'admin',
  FOR delete WHERE false;
