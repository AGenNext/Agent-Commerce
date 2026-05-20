-- Schema.org-aligned commerce schema for Agent-Commerce
-- Keeps SurrealDB-native relations while preserving JSON-LD compatibility.

-- ============================================================
-- Core commercial actors
-- Schema.org: Organization, OnlineBusiness, LocalBusiness, Person
-- ============================================================

DEFINE TABLE merchants SCHEMAFULL;
DEFINE FIELD schema_context ON merchants TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON merchants TYPE string DEFAULT 'OnlineBusiness';
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
DEFINE INDEX merchants_name_search ON merchants FIELDS name SEARCH ANALYZER ascii BM25;

-- ============================================================
-- Catalog
-- Schema.org: Product, ProductModel, ProductGroup, IndividualProduct, Brand
-- ============================================================

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
DEFINE FIELD schema_type ON products TYPE string DEFAULT 'Product';
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
DEFINE INDEX products_name_search ON products FIELDS name SEARCH ANALYZER ascii BM25;
DEFINE INDEX products_description_search ON products FIELDS description SEARCH ANALYZER ascii BM25;
DEFINE INDEX products_category ON products FIELDS category;

-- NOTE: Remaining Schema.org-aligned commerce definitions continue in prior version.
-- This patch intentionally grounds Brand first. Subsequent migrations should add
-- schema_url fields to Product, Offer, Order, Invoice, PaymentMethod, ParcelDelivery,
-- MerchantReturnPolicy, Review, Rating, and AggregateRating as needed.
