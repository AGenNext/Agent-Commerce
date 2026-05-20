-- Schema.org metamodel knowledge graph for Agent-Commerce
-- This file grounds classes, properties, relations, routes, and records in a queryable metamodel.
-- It is intentionally separate from business tables so the KG can validate and explain itself.

-- ============================================================
-- Schema.org metamodel primitives
-- ============================================================

DEFINE TABLE schema_classes SCHEMAFULL;
DEFINE FIELD name ON schema_classes TYPE string;
DEFINE FIELD url ON schema_classes TYPE string;
DEFINE FIELD parent ON schema_classes TYPE option<record<schema_classes>>;
DEFINE FIELD description ON schema_classes TYPE option<string>;
DEFINE FIELD layer ON schema_classes TYPE string DEFAULT 'schema.org';
DEFINE FIELD created_at ON schema_classes TYPE datetime DEFAULT time::now();
DEFINE INDEX schema_classes_name_unique ON schema_classes FIELDS name UNIQUE;
DEFINE INDEX schema_classes_url_unique ON schema_classes FIELDS url UNIQUE;

DEFINE TABLE schema_properties SCHEMAFULL;
DEFINE FIELD name ON schema_properties TYPE string;
DEFINE FIELD url ON schema_properties TYPE string;
DEFINE FIELD description ON schema_properties TYPE option<string>;
DEFINE FIELD expected_types ON schema_properties TYPE array<string> DEFAULT [];
DEFINE FIELD created_at ON schema_properties TYPE datetime DEFAULT time::now();
DEFINE INDEX schema_properties_name_unique ON schema_properties FIELDS name UNIQUE;
DEFINE INDEX schema_properties_url_unique ON schema_properties FIELDS url UNIQUE;

DEFINE TABLE app_tables SCHEMAFULL;
DEFINE FIELD name ON app_tables TYPE string;
DEFINE FIELD purpose ON app_tables TYPE string;
DEFINE FIELD primary_schema_class ON app_tables TYPE record<schema_classes>;
DEFINE FIELD created_at ON app_tables TYPE datetime DEFAULT time::now();
DEFINE INDEX app_tables_name_unique ON app_tables FIELDS name UNIQUE;

DEFINE TABLE app_fields SCHEMAFULL;
DEFINE FIELD table ON app_fields TYPE record<app_tables>;
DEFINE FIELD name ON app_fields TYPE string;
DEFINE FIELD surreal_type ON app_fields TYPE string;
DEFINE FIELD schema_property ON app_fields TYPE option<record<schema_properties>>;
DEFINE FIELD schema_range ON app_fields TYPE option<array<record<schema_classes>>>;
DEFINE FIELD required ON app_fields TYPE bool DEFAULT false;
DEFINE FIELD notes ON app_fields TYPE option<string>;
DEFINE FIELD created_at ON app_fields TYPE datetime DEFAULT time::now();
DEFINE INDEX app_fields_table_name_unique ON app_fields FIELDS table, name UNIQUE;

DEFINE TABLE app_relations SCHEMAFULL;
DEFINE FIELD name ON app_relations TYPE string;
DEFINE FIELD in_table ON app_relations TYPE record<app_tables>;
DEFINE FIELD out_table ON app_relations TYPE record<app_tables>;
DEFINE FIELD schema_property ON app_relations TYPE option<record<schema_properties>>;
DEFINE FIELD description ON app_relations TYPE option<string>;
DEFINE FIELD created_at ON app_relations TYPE datetime DEFAULT time::now();
DEFINE INDEX app_relations_name_unique ON app_relations FIELDS name UNIQUE;

DEFINE TABLE api_routes SCHEMAFULL;
DEFINE FIELD method ON api_routes TYPE string;
DEFINE FIELD path ON api_routes TYPE string;
DEFINE FIELD action_class ON api_routes TYPE option<record<schema_classes>>;
DEFINE FIELD input_class ON api_routes TYPE option<record<schema_classes>>;
DEFINE FIELD output_class ON api_routes TYPE option<record<schema_classes>>;
DEFINE FIELD description ON api_routes TYPE option<string>;
DEFINE FIELD created_at ON api_routes TYPE datetime DEFAULT time::now();
DEFINE INDEX api_routes_method_path_unique ON api_routes FIELDS method, path UNIQUE;

-- Metamodel graph relations
DEFINE TABLE subclass_of TYPE RELATION IN schema_classes OUT schema_classes SCHEMAFULL;
DEFINE FIELD created_at ON subclass_of TYPE datetime DEFAULT time::now();

DEFINE TABLE has_property TYPE RELATION IN schema_classes OUT schema_properties SCHEMAFULL;
DEFINE FIELD required ON has_property TYPE bool DEFAULT false;
DEFINE FIELD created_at ON has_property TYPE datetime DEFAULT time::now();

DEFINE TABLE property_range TYPE RELATION IN schema_properties OUT schema_classes SCHEMAFULL;
DEFINE FIELD created_at ON property_range TYPE datetime DEFAULT time::now();

DEFINE TABLE table_implements TYPE RELATION IN app_tables OUT schema_classes SCHEMAFULL;
DEFINE FIELD created_at ON table_implements TYPE datetime DEFAULT time::now();

DEFINE TABLE field_maps_to TYPE RELATION IN app_fields OUT schema_properties SCHEMAFULL;
DEFINE FIELD created_at ON field_maps_to TYPE datetime DEFAULT time::now();

DEFINE TABLE relation_maps_to TYPE RELATION IN app_relations OUT schema_properties SCHEMAFULL;
DEFINE FIELD created_at ON relation_maps_to TYPE datetime DEFAULT time::now();

DEFINE TABLE route_invokes TYPE RELATION IN api_routes OUT schema_classes SCHEMAFULL;
DEFINE FIELD created_at ON route_invokes TYPE datetime DEFAULT time::now();

-- ============================================================
-- Schema.org class registry
-- ============================================================

UPSERT schema_classes:Thing CONTENT { name: 'Thing', url: 'https://schema.org/Thing' };
UPSERT schema_classes:Action CONTENT { name: 'Action', url: 'https://schema.org/Action', parent: schema_classes:Thing };
UPSERT schema_classes:FindAction CONTENT { name: 'FindAction', url: 'https://schema.org/FindAction', parent: schema_classes:Action };
UPSERT schema_classes:SearchAction CONTENT { name: 'SearchAction', url: 'https://schema.org/SearchAction', parent: schema_classes:FindAction };
UPSERT schema_classes:CheckAction CONTENT { name: 'CheckAction', url: 'https://schema.org/CheckAction', parent: schema_classes:FindAction };
UPSERT schema_classes:DiscoverAction CONTENT { name: 'DiscoverAction', url: 'https://schema.org/DiscoverAction', parent: schema_classes:FindAction };
UPSERT schema_classes:TrackAction CONTENT { name: 'TrackAction', url: 'https://schema.org/TrackAction', parent: schema_classes:FindAction };
UPSERT schema_classes:TradeAction CONTENT { name: 'TradeAction', url: 'https://schema.org/TradeAction', parent: schema_classes:Action };
UPSERT schema_classes:BuyAction CONTENT { name: 'BuyAction', url: 'https://schema.org/BuyAction', parent: schema_classes:TradeAction };
UPSERT schema_classes:OrderAction CONTENT { name: 'OrderAction', url: 'https://schema.org/OrderAction', parent: schema_classes:TradeAction };
UPSERT schema_classes:PayAction CONTENT { name: 'PayAction', url: 'https://schema.org/PayAction', parent: schema_classes:TradeAction };
UPSERT schema_classes:PreOrderAction CONTENT { name: 'PreOrderAction', url: 'https://schema.org/PreOrderAction', parent: schema_classes:TradeAction };
UPSERT schema_classes:QuoteAction CONTENT { name: 'QuoteAction', url: 'https://schema.org/QuoteAction', parent: schema_classes:TradeAction };
UPSERT schema_classes:RentAction CONTENT { name: 'RentAction', url: 'https://schema.org/RentAction', parent: schema_classes:TradeAction };
UPSERT schema_classes:SellAction CONTENT { name: 'SellAction', url: 'https://schema.org/SellAction', parent: schema_classes:TradeAction };
UPSERT schema_classes:TipAction CONTENT { name: 'TipAction', url: 'https://schema.org/TipAction', parent: schema_classes:TradeAction };
UPSERT schema_classes:TransferAction CONTENT { name: 'TransferAction', url: 'https://schema.org/TransferAction', parent: schema_classes:Action };
UPSERT schema_classes:BorrowAction CONTENT { name: 'BorrowAction', url: 'https://schema.org/BorrowAction', parent: schema_classes:TransferAction };
UPSERT schema_classes:DonateAction CONTENT { name: 'DonateAction', url: 'https://schema.org/DonateAction', parent: schema_classes:TransferAction };
UPSERT schema_classes:DownloadAction CONTENT { name: 'DownloadAction', url: 'https://schema.org/DownloadAction', parent: schema_classes:TransferAction };
UPSERT schema_classes:GiveAction CONTENT { name: 'GiveAction', url: 'https://schema.org/GiveAction', parent: schema_classes:TransferAction };
UPSERT schema_classes:LendAction CONTENT { name: 'LendAction', url: 'https://schema.org/LendAction', parent: schema_classes:TransferAction };
UPSERT schema_classes:MoneyTransfer CONTENT { name: 'MoneyTransfer', url: 'https://schema.org/MoneyTransfer', parent: schema_classes:TransferAction };
UPSERT schema_classes:ReceiveAction CONTENT { name: 'ReceiveAction', url: 'https://schema.org/ReceiveAction', parent: schema_classes:TransferAction };
UPSERT schema_classes:ReturnAction CONTENT { name: 'ReturnAction', url: 'https://schema.org/ReturnAction', parent: schema_classes:TransferAction };
UPSERT schema_classes:SendAction CONTENT { name: 'SendAction', url: 'https://schema.org/SendAction', parent: schema_classes:TransferAction };
UPSERT schema_classes:TakeAction CONTENT { name: 'TakeAction', url: 'https://schema.org/TakeAction', parent: schema_classes:TransferAction };
UPSERT schema_classes:Organization CONTENT { name: 'Organization', url: 'https://schema.org/Organization', parent: schema_classes:Thing };
UPSERT schema_classes:OnlineBusiness CONTENT { name: 'OnlineBusiness', url: 'https://schema.org/OnlineBusiness', parent: schema_classes:Organization };
UPSERT schema_classes:LocalBusiness CONTENT { name: 'LocalBusiness', url: 'https://schema.org/LocalBusiness', parent: schema_classes:Organization };
UPSERT schema_classes:Person CONTENT { name: 'Person', url: 'https://schema.org/Person', parent: schema_classes:Thing };
UPSERT schema_classes:Brand CONTENT { name: 'Brand', url: 'https://schema.org/Brand', parent: schema_classes:Thing };
UPSERT schema_classes:Product CONTENT { name: 'Product', url: 'https://schema.org/Product', parent: schema_classes:Thing };
UPSERT schema_classes:ProductModel CONTENT { name: 'ProductModel', url: 'https://schema.org/ProductModel', parent: schema_classes:Product };
UPSERT schema_classes:ProductGroup CONTENT { name: 'ProductGroup', url: 'https://schema.org/ProductGroup', parent: schema_classes:Product };
UPSERT schema_classes:IndividualProduct CONTENT { name: 'IndividualProduct', url: 'https://schema.org/IndividualProduct', parent: schema_classes:Product };
UPSERT schema_classes:Offer CONTENT { name: 'Offer', url: 'https://schema.org/Offer', parent: schema_classes:Thing };
UPSERT schema_classes:Demand CONTENT { name: 'Demand', url: 'https://schema.org/Demand', parent: schema_classes:Thing };
UPSERT schema_classes:Order CONTENT { name: 'Order', url: 'https://schema.org/Order', parent: schema_classes:Thing };
UPSERT schema_classes:Invoice CONTENT { name: 'Invoice', url: 'https://schema.org/Invoice', parent: schema_classes:Thing };
UPSERT schema_classes:PaymentMethod CONTENT { name: 'PaymentMethod', url: 'https://schema.org/PaymentMethod', parent: schema_classes:Thing };
UPSERT schema_classes:ParcelDelivery CONTENT { name: 'ParcelDelivery', url: 'https://schema.org/ParcelDelivery', parent: schema_classes:Thing };
UPSERT schema_classes:MerchantReturnPolicy CONTENT { name: 'MerchantReturnPolicy', url: 'https://schema.org/MerchantReturnPolicy', parent: schema_classes:Thing };
UPSERT schema_classes:Review CONTENT { name: 'Review', url: 'https://schema.org/Review', parent: schema_classes:Thing };
UPSERT schema_classes:Rating CONTENT { name: 'Rating', url: 'https://schema.org/Rating', parent: schema_classes:Thing };
UPSERT schema_classes:AggregateRating CONTENT { name: 'AggregateRating', url: 'https://schema.org/AggregateRating', parent: schema_classes:Rating };
UPSERT schema_classes:ItemList CONTENT { name: 'ItemList', url: 'https://schema.org/ItemList', parent: schema_classes:Thing };
UPSERT schema_classes:ListItem CONTENT { name: 'ListItem', url: 'https://schema.org/ListItem', parent: schema_classes:Thing };
UPSERT schema_classes:Service CONTENT { name: 'Service', url: 'https://schema.org/Service', parent: schema_classes:Thing };

-- subclass edges
RELATE schema_classes:Action->subclass_of->schema_classes:Thing;
RELATE schema_classes:FindAction->subclass_of->schema_classes:Action;
RELATE schema_classes:SearchAction->subclass_of->schema_classes:FindAction;
RELATE schema_classes:CheckAction->subclass_of->schema_classes:FindAction;
RELATE schema_classes:DiscoverAction->subclass_of->schema_classes:FindAction;
RELATE schema_classes:TrackAction->subclass_of->schema_classes:FindAction;
RELATE schema_classes:TradeAction->subclass_of->schema_classes:Action;
RELATE schema_classes:BuyAction->subclass_of->schema_classes:TradeAction;
RELATE schema_classes:OrderAction->subclass_of->schema_classes:TradeAction;
RELATE schema_classes:PayAction->subclass_of->schema_classes:TradeAction;
RELATE schema_classes:TransferAction->subclass_of->schema_classes:Action;
RELATE schema_classes:MoneyTransfer->subclass_of->schema_classes:TransferAction;
RELATE schema_classes:Organization->subclass_of->schema_classes:Thing;
RELATE schema_classes:OnlineBusiness->subclass_of->schema_classes:Organization;
RELATE schema_classes:LocalBusiness->subclass_of->schema_classes:Organization;
RELATE schema_classes:ProductModel->subclass_of->schema_classes:Product;
RELATE schema_classes:ProductGroup->subclass_of->schema_classes:Product;
RELATE schema_classes:IndividualProduct->subclass_of->schema_classes:Product;

-- ============================================================
-- Schema.org property registry
-- ============================================================

UPSERT schema_properties:name CONTENT { name: 'name', url: 'https://schema.org/name', expected_types: ['Text'] };
UPSERT schema_properties:description CONTENT { name: 'description', url: 'https://schema.org/description', expected_types: ['Text'] };
UPSERT schema_properties:url CONTENT { name: 'url', url: 'https://schema.org/url', expected_types: ['URL'] };
UPSERT schema_properties:logo CONTENT { name: 'logo', url: 'https://schema.org/logo', expected_types: ['ImageObject', 'URL'] };
UPSERT schema_properties:image CONTENT { name: 'image', url: 'https://schema.org/image', expected_types: ['ImageObject', 'URL'] };
UPSERT schema_properties:brand CONTENT { name: 'brand', url: 'https://schema.org/brand', expected_types: ['Brand', 'Organization'] };
UPSERT schema_properties:manufacturer CONTENT { name: 'manufacturer', url: 'https://schema.org/manufacturer', expected_types: ['Organization'] };
UPSERT schema_properties:sku CONTENT { name: 'sku', url: 'https://schema.org/sku', expected_types: ['Text'] };
UPSERT schema_properties:gtin CONTENT { name: 'gtin', url: 'https://schema.org/gtin', expected_types: ['Text'] };
UPSERT schema_properties:mpn CONTENT { name: 'mpn', url: 'https://schema.org/mpn', expected_types: ['Text'] };
UPSERT schema_properties:category CONTENT { name: 'category', url: 'https://schema.org/category', expected_types: ['Text', 'Thing'] };
UPSERT schema_properties:offers CONTENT { name: 'offers', url: 'https://schema.org/offers', expected_types: ['Offer', 'Demand'] };
UPSERT schema_properties:itemOffered CONTENT { name: 'itemOffered', url: 'https://schema.org/itemOffered', expected_types: ['Product', 'Service'] };
UPSERT schema_properties:seller CONTENT { name: 'seller', url: 'https://schema.org/seller', expected_types: ['Organization', 'Person'] };
UPSERT schema_properties:price CONTENT { name: 'price', url: 'https://schema.org/price', expected_types: ['Number', 'Text'] };
UPSERT schema_properties:priceCurrency CONTENT { name: 'priceCurrency', url: 'https://schema.org/priceCurrency', expected_types: ['Text'] };
UPSERT schema_properties:availability CONTENT { name: 'availability', url: 'https://schema.org/availability', expected_types: ['ItemAvailability'] };
UPSERT schema_properties:validFrom CONTENT { name: 'validFrom', url: 'https://schema.org/validFrom', expected_types: ['DateTime'] };
UPSERT schema_properties:validThrough CONTENT { name: 'validThrough', url: 'https://schema.org/validThrough', expected_types: ['DateTime'] };
UPSERT schema_properties:acceptedPaymentMethod CONTENT { name: 'acceptedPaymentMethod', url: 'https://schema.org/acceptedPaymentMethod', expected_types: ['PaymentMethod', 'Text'] };
UPSERT schema_properties:orderNumber CONTENT { name: 'orderNumber', url: 'https://schema.org/orderNumber', expected_types: ['Text'] };
UPSERT schema_properties:orderStatus CONTENT { name: 'orderStatus', url: 'https://schema.org/orderStatus', expected_types: ['OrderStatus'] };
UPSERT schema_properties:customer CONTENT { name: 'customer', url: 'https://schema.org/customer', expected_types: ['Person', 'Organization'] };
UPSERT schema_properties:merchant CONTENT { name: 'merchant', url: 'https://schema.org/merchant', expected_types: ['Organization', 'Person'] };
UPSERT schema_properties:acceptedOffer CONTENT { name: 'acceptedOffer', url: 'https://schema.org/acceptedOffer', expected_types: ['Offer'] };
UPSERT schema_properties:orderedItem CONTENT { name: 'orderedItem', url: 'https://schema.org/orderedItem', expected_types: ['OrderItem', 'Product'] };
UPSERT schema_properties:paymentMethod CONTENT { name: 'paymentMethod', url: 'https://schema.org/paymentMethod', expected_types: ['PaymentMethod'] };
UPSERT schema_properties:billingAddress CONTENT { name: 'billingAddress', url: 'https://schema.org/billingAddress', expected_types: ['PostalAddress'] };
UPSERT schema_properties:deliveryAddress CONTENT { name: 'deliveryAddress', url: 'https://schema.org/deliveryAddress', expected_types: ['PostalAddress'] };
UPSERT schema_properties:orderDate CONTENT { name: 'orderDate', url: 'https://schema.org/orderDate', expected_types: ['DateTime'] };
UPSERT schema_properties:partOfOrder CONTENT { name: 'partOfOrder', url: 'https://schema.org/partOfOrder', expected_types: ['Order'] };
UPSERT schema_properties:trackingNumber CONTENT { name: 'trackingNumber', url: 'https://schema.org/trackingNumber', expected_types: ['Text'] };
UPSERT schema_properties:trackingUrl CONTENT { name: 'trackingUrl', url: 'https://schema.org/trackingUrl', expected_types: ['URL'] };
UPSERT schema_properties:expectedArrivalFrom CONTENT { name: 'expectedArrivalFrom', url: 'https://schema.org/expectedArrivalFrom', expected_types: ['DateTime'] };
UPSERT schema_properties:expectedArrivalUntil CONTENT { name: 'expectedArrivalUntil', url: 'https://schema.org/expectedArrivalUntil', expected_types: ['DateTime'] };
UPSERT schema_properties:returnPolicyCategory CONTENT { name: 'returnPolicyCategory', url: 'https://schema.org/returnPolicyCategory', expected_types: ['MerchantReturnEnumeration'] };
UPSERT schema_properties:merchantReturnDays CONTENT { name: 'merchantReturnDays', url: 'https://schema.org/merchantReturnDays', expected_types: ['Integer'] };
UPSERT schema_properties:returnFees CONTENT { name: 'returnFees', url: 'https://schema.org/returnFees', expected_types: ['ReturnFeesEnumeration'] };
UPSERT schema_properties:refundType CONTENT { name: 'refundType', url: 'https://schema.org/refundType', expected_types: ['RefundTypeEnumeration'] };
UPSERT schema_properties:itemReviewed CONTENT { name: 'itemReviewed', url: 'https://schema.org/itemReviewed', expected_types: ['Thing'] };
UPSERT schema_properties:author CONTENT { name: 'author', url: 'https://schema.org/author', expected_types: ['Person', 'Organization'] };
UPSERT schema_properties:reviewRating CONTENT { name: 'reviewRating', url: 'https://schema.org/reviewRating', expected_types: ['Rating'] };
UPSERT schema_properties:reviewBody CONTENT { name: 'reviewBody', url: 'https://schema.org/reviewBody', expected_types: ['Text'] };
UPSERT schema_properties:agent CONTENT { name: 'agent', url: 'https://schema.org/agent', expected_types: ['Person', 'Organization'] };
UPSERT schema_properties:participant CONTENT { name: 'participant', url: 'https://schema.org/participant', expected_types: ['Person', 'Organization'] };
UPSERT schema_properties:recipient CONTENT { name: 'recipient', url: 'https://schema.org/recipient', expected_types: ['Person', 'Organization'] };
UPSERT schema_properties:object CONTENT { name: 'object', url: 'https://schema.org/object', expected_types: ['Thing'] };
UPSERT schema_properties:target CONTENT { name: 'target', url: 'https://schema.org/target', expected_types: ['EntryPoint'] };
UPSERT schema_properties:instrument CONTENT { name: 'instrument', url: 'https://schema.org/instrument', expected_types: ['Thing'] };
UPSERT schema_properties:result CONTENT { name: 'result', url: 'https://schema.org/result', expected_types: ['Thing'] };
UPSERT schema_properties:actionStatus CONTENT { name: 'actionStatus', url: 'https://schema.org/actionStatus', expected_types: ['ActionStatusType'] };
UPSERT schema_properties:startTime CONTENT { name: 'startTime', url: 'https://schema.org/startTime', expected_types: ['DateTime'] };
UPSERT schema_properties:endTime CONTENT { name: 'endTime', url: 'https://schema.org/endTime', expected_types: ['DateTime'] };
UPSERT schema_properties:query CONTENT { name: 'query', url: 'https://schema.org/query', expected_types: ['Text'] };

-- ============================================================
-- App table/class grounding
-- ============================================================

UPSERT app_tables:merchants CONTENT { name: 'merchants', purpose: 'Commerce organizations and sellers', primary_schema_class: schema_classes:OnlineBusiness };
UPSERT app_tables:brands CONTENT { name: 'brands', purpose: 'Product brands', primary_schema_class: schema_classes:Brand };
UPSERT app_tables:products CONTENT { name: 'products', purpose: 'Catalog items and variants', primary_schema_class: schema_classes:Product };
UPSERT app_tables:offers CONTENT { name: 'offers', purpose: 'Sellable offers and pricing', primary_schema_class: schema_classes:Offer };
UPSERT app_tables:orders CONTENT { name: 'orders', purpose: 'Customer orders', primary_schema_class: schema_classes:Order };
UPSERT app_tables:invoices CONTENT { name: 'invoices', purpose: 'Invoices and payment requests', primary_schema_class: schema_classes:Invoice };
UPSERT app_tables:payment_methods CONTENT { name: 'payment_methods', purpose: 'Supported payment methods', primary_schema_class: schema_classes:PaymentMethod };
UPSERT app_tables:deliveries CONTENT { name: 'deliveries', purpose: 'Shipment and parcel delivery', primary_schema_class: schema_classes:ParcelDelivery };
UPSERT app_tables:return_policies CONTENT { name: 'return_policies', purpose: 'Merchant return policies', primary_schema_class: schema_classes:MerchantReturnPolicy };
UPSERT app_tables:reviews CONTENT { name: 'reviews', purpose: 'Product reviews and ratings', primary_schema_class: schema_classes:Review };
UPSERT app_tables:commerce_actions CONTENT { name: 'commerce_actions', purpose: 'Agent/user commerce actions and intent graph', primary_schema_class: schema_classes:Action };

RELATE app_tables:merchants->table_implements->schema_classes:OnlineBusiness;
RELATE app_tables:brands->table_implements->schema_classes:Brand;
RELATE app_tables:products->table_implements->schema_classes:Product;
RELATE app_tables:offers->table_implements->schema_classes:Offer;
RELATE app_tables:orders->table_implements->schema_classes:Order;
RELATE app_tables:invoices->table_implements->schema_classes:Invoice;
RELATE app_tables:payment_methods->table_implements->schema_classes:PaymentMethod;
RELATE app_tables:deliveries->table_implements->schema_classes:ParcelDelivery;
RELATE app_tables:return_policies->table_implements->schema_classes:MerchantReturnPolicy;
RELATE app_tables:reviews->table_implements->schema_classes:Review;
RELATE app_tables:commerce_actions->table_implements->schema_classes:Action;

-- ============================================================
-- Field/property mappings
-- ============================================================

UPSERT app_fields:products_name CONTENT { table: app_tables:products, name: 'name', surreal_type: 'string', schema_property: schema_properties:name, required: true };
UPSERT app_fields:products_description CONTENT { table: app_tables:products, name: 'description', surreal_type: 'option<string>', schema_property: schema_properties:description };
UPSERT app_fields:products_sku CONTENT { table: app_tables:products, name: 'sku', surreal_type: 'option<string>', schema_property: schema_properties:sku };
UPSERT app_fields:products_gtin CONTENT { table: app_tables:products, name: 'gtin', surreal_type: 'option<string>', schema_property: schema_properties:gtin };
UPSERT app_fields:products_mpn CONTENT { table: app_tables:products, name: 'mpn', surreal_type: 'option<string>', schema_property: schema_properties:mpn };
UPSERT app_fields:products_category CONTENT { table: app_tables:products, name: 'category', surreal_type: 'option<string>', schema_property: schema_properties:category };
UPSERT app_fields:products_image CONTENT { table: app_tables:products, name: 'image', surreal_type: 'option<array<string>>', schema_property: schema_properties:image };
UPSERT app_fields:products_brand CONTENT { table: app_tables:products, name: 'brand', surreal_type: 'option<record<brands>>', schema_property: schema_properties:brand, schema_range: [schema_classes:Brand] };
UPSERT app_fields:products_manufacturer CONTENT { table: app_tables:products, name: 'manufacturer', surreal_type: 'option<record<merchants>>', schema_property: schema_properties:manufacturer, schema_range: [schema_classes:Organization] };
UPSERT app_fields:offers_itemOffered CONTENT { table: app_tables:offers, name: 'itemOffered', surreal_type: 'record<products>', schema_property: schema_properties:itemOffered, schema_range: [schema_classes:Product], required: true };
UPSERT app_fields:offers_seller CONTENT { table: app_tables:offers, name: 'seller', surreal_type: 'record<merchants>', schema_property: schema_properties:seller, schema_range: [schema_classes:Organization], required: true };
UPSERT app_fields:offers_price CONTENT { table: app_tables:offers, name: 'price', surreal_type: 'decimal', schema_property: schema_properties:price, required: true };
UPSERT app_fields:offers_priceCurrency CONTENT { table: app_tables:offers, name: 'priceCurrency', surreal_type: 'string', schema_property: schema_properties:priceCurrency, required: true };
UPSERT app_fields:offers_availability CONTENT { table: app_tables:offers, name: 'availability', surreal_type: 'string', schema_property: schema_properties:availability };
UPSERT app_fields:orders_orderNumber CONTENT { table: app_tables:orders, name: 'orderNumber', surreal_type: 'string', schema_property: schema_properties:orderNumber, required: true };
UPSERT app_fields:orders_orderStatus CONTENT { table: app_tables:orders, name: 'orderStatus', surreal_type: 'string', schema_property: schema_properties:orderStatus };
UPSERT app_fields:orders_customer CONTENT { table: app_tables:orders, name: 'customer', surreal_type: 'record<users>', schema_property: schema_properties:customer, schema_range: [schema_classes:Person], required: true };
UPSERT app_fields:orders_merchant CONTENT { table: app_tables:orders, name: 'merchant', surreal_type: 'record<merchants>', schema_property: schema_properties:merchant, schema_range: [schema_classes:Organization], required: true };
UPSERT app_fields:orders_acceptedOffer CONTENT { table: app_tables:orders, name: 'acceptedOffer', surreal_type: 'option<array<record<offers>>>', schema_property: schema_properties:acceptedOffer, schema_range: [schema_classes:Offer] };
UPSERT app_fields:orders_orderedItem CONTENT { table: app_tables:orders, name: 'orderedItem', surreal_type: 'array<object>', schema_property: schema_properties:orderedItem, schema_range: [schema_classes:Product] };
UPSERT app_fields:actions_agent CONTENT { table: app_tables:commerce_actions, name: 'agent', surreal_type: 'option<record<users>>', schema_property: schema_properties:agent, schema_range: [schema_classes:Person] };
UPSERT app_fields:actions_object CONTENT { table: app_tables:commerce_actions, name: 'object', surreal_type: 'option<record>', schema_property: schema_properties:object };
UPSERT app_fields:actions_target CONTENT { table: app_tables:commerce_actions, name: 'target', surreal_type: 'option<string>', schema_property: schema_properties:target };
UPSERT app_fields:actions_result CONTENT { table: app_tables:commerce_actions, name: 'result', surreal_type: 'option<array<record>>', schema_property: schema_properties:result };
UPSERT app_fields:actions_actionStatus CONTENT { table: app_tables:commerce_actions, name: 'actionStatus', surreal_type: 'string', schema_property: schema_properties:actionStatus };
UPSERT app_fields:actions_startTime CONTENT { table: app_tables:commerce_actions, name: 'startTime', surreal_type: 'option<datetime>', schema_property: schema_properties:startTime };
UPSERT app_fields:actions_endTime CONTENT { table: app_tables:commerce_actions, name: 'endTime', surreal_type: 'option<datetime>', schema_property: schema_properties:endTime };
UPSERT app_fields:actions_query CONTENT { table: app_tables:commerce_actions, name: 'query', surreal_type: 'option<string>', schema_property: schema_properties:query };

RELATE app_fields:products_name->field_maps_to->schema_properties:name;
RELATE app_fields:products_brand->field_maps_to->schema_properties:brand;
RELATE app_fields:offers_itemOffered->field_maps_to->schema_properties:itemOffered;
RELATE app_fields:offers_seller->field_maps_to->schema_properties:seller;
RELATE app_fields:orders_customer->field_maps_to->schema_properties:customer;
RELATE app_fields:orders_merchant->field_maps_to->schema_properties:merchant;
RELATE app_fields:actions_agent->field_maps_to->schema_properties:agent;
RELATE app_fields:actions_result->field_maps_to->schema_properties:result;
RELATE app_fields:actions_query->field_maps_to->schema_properties:query;

-- ============================================================
-- Relation grounding
-- ============================================================

UPSERT app_relations:sells CONTENT { name: 'sells', in_table: app_tables:merchants, out_table: app_tables:products, schema_property: schema_properties:seller, description: 'Merchant sells Product' };
UPSERT app_relations:has_offer CONTENT { name: 'has_offer', in_table: app_tables:merchants, out_table: app_tables:offers, schema_property: schema_properties:offers, description: 'Merchant has Offer' };
UPSERT app_relations:order_contains CONTENT { name: 'order_contains', in_table: app_tables:orders, out_table: app_tables:products, schema_property: schema_properties:orderedItem, description: 'Order contains Product' };
UPSERT app_relations:fulfilled_by CONTENT { name: 'fulfilled_by', in_table: app_tables:orders, out_table: app_tables:deliveries, schema_property: schema_properties:partOfOrder, description: 'Order fulfilled by ParcelDelivery' };
UPSERT app_relations:performed_action CONTENT { name: 'performed_action', in_table: app_tables:commerce_actions, out_table: app_tables:commerce_actions, schema_property: schema_properties:agent, description: 'User/agent performed Action' };

RELATE app_relations:sells->relation_maps_to->schema_properties:seller;
RELATE app_relations:has_offer->relation_maps_to->schema_properties:offers;
RELATE app_relations:order_contains->relation_maps_to->schema_properties:orderedItem;
RELATE app_relations:fulfilled_by->relation_maps_to->schema_properties:partOfOrder;
RELATE app_relations:performed_action->relation_maps_to->schema_properties:agent;

-- ============================================================
-- API route grounding
-- ============================================================

UPSERT api_routes:search_products CONTENT { method: 'GET', path: '/api/store/products', action_class: schema_classes:SearchAction, output_class: schema_classes:Product, description: 'Search/list products' };
UPSERT api_routes:create_product CONTENT { method: 'POST', path: '/api/store/products', action_class: schema_classes:SellAction, input_class: schema_classes:Product, output_class: schema_classes:Product, description: 'Create product for merchant' };
UPSERT api_routes:create_order CONTENT { method: 'POST', path: '/api/store/orders', action_class: schema_classes:OrderAction, input_class: schema_classes:Order, output_class: schema_classes:Order, description: 'Place order' };
UPSERT api_routes:create_payment CONTENT { method: 'POST', path: '/api/payments/{provider}', action_class: schema_classes:PayAction, input_class: schema_classes:PaymentMethod, output_class: schema_classes:MoneyTransfer, description: 'Create payment' };
UPSERT api_routes:track_delivery CONTENT { method: 'GET', path: '/api/vendor/{vendor_id}/dashboard', action_class: schema_classes:TrackAction, output_class: schema_classes:ParcelDelivery, description: 'Track vendor/order state' };

RELATE api_routes:search_products->route_invokes->schema_classes:SearchAction;
RELATE api_routes:create_product->route_invokes->schema_classes:SellAction;
RELATE api_routes:create_order->route_invokes->schema_classes:OrderAction;
RELATE api_routes:create_payment->route_invokes->schema_classes:PayAction;
RELATE api_routes:track_delivery->route_invokes->schema_classes:TrackAction;

-- ============================================================
-- Validation helpers
-- ============================================================

DEFINE TABLE kg_validation_rules SCHEMAFULL;
DEFINE FIELD name ON kg_validation_rules TYPE string;
DEFINE FIELD description ON kg_validation_rules TYPE string;
DEFINE FIELD query ON kg_validation_rules TYPE string;
DEFINE FIELD severity ON kg_validation_rules TYPE string DEFAULT 'error';
DEFINE FIELD created_at ON kg_validation_rules TYPE datetime DEFAULT time::now();
DEFINE INDEX kg_validation_rules_name_unique ON kg_validation_rules FIELDS name UNIQUE;

UPSERT kg_validation_rules:tables_have_schema_class CONTENT {
  name: 'tables_have_schema_class',
  description: 'Every app table must implement a Schema.org class',
  severity: 'error',
  query: 'SELECT * FROM app_tables WHERE primary_schema_class = NONE;'
};

UPSERT kg_validation_rules:fields_have_schema_property_when_public CONTENT {
  name: 'fields_have_schema_property_when_public',
  description: 'Public API fields should map to Schema.org properties unless intentionally app-specific',
  severity: 'warning',
  query: 'SELECT * FROM app_fields WHERE schema_property = NONE AND notes !~ "app-specific";'
};

UPSERT kg_validation_rules:routes_have_action_class CONTENT {
  name: 'routes_have_action_class',
  description: 'Every API route should map to a Schema.org Action class',
  severity: 'error',
  query: 'SELECT * FROM api_routes WHERE action_class = NONE;'
};

UPSERT kg_validation_rules:relations_have_schema_property CONTENT {
  name: 'relations_have_schema_property',
  description: 'Every app relation should map to a Schema.org property',
  severity: 'error',
  query: 'SELECT * FROM app_relations WHERE schema_property = NONE;'
};

-- Permissions for metamodel: readable by authenticated users, writable only by admin.
DEFINE TABLE schema_classes PERMISSIONS FOR select WHERE true, FOR create, update, delete WHERE $auth.role = 'admin';
DEFINE TABLE schema_properties PERMISSIONS FOR select WHERE true, FOR create, update, delete WHERE $auth.role = 'admin';
DEFINE TABLE app_tables PERMISSIONS FOR select WHERE true, FOR create, update, delete WHERE $auth.role = 'admin';
DEFINE TABLE app_fields PERMISSIONS FOR select WHERE true, FOR create, update, delete WHERE $auth.role = 'admin';
DEFINE TABLE app_relations PERMISSIONS FOR select WHERE true, FOR create, update, delete WHERE $auth.role = 'admin';
DEFINE TABLE api_routes PERMISSIONS FOR select WHERE true, FOR create, update, delete WHERE $auth.role = 'admin';
DEFINE TABLE kg_validation_rules PERMISSIONS FOR select WHERE true, FOR create, update, delete WHERE $auth.role = 'admin';
