-- Catalog onboarding flow
-- SurrealDB-first implementation. No FastAPI route is required.
-- Grounding:
-- - Product draft/import: https://schema.org/Product
-- - Offer draft/import: https://schema.org/Offer
-- - Import/create workflow: https://schema.org/CreateAction
-- - Review/update workflow: https://schema.org/UpdateAction

-- ============================================================
-- Catalog onboarding records
-- ============================================================

DEFINE TABLE catalog_import_batches SCHEMAFULL;
DEFINE FIELD schema_context ON catalog_import_batches TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON catalog_import_batches TYPE string DEFAULT 'CreateAction';
DEFINE FIELD schema_url ON catalog_import_batches TYPE string VALUE 'https://schema.org/CreateAction';
DEFINE FIELD tenant_id ON catalog_import_batches TYPE string;
DEFINE FIELD merchant ON catalog_import_batches TYPE record<merchants>;
DEFINE FIELD submitted_by ON catalog_import_batches TYPE record<users>;
DEFINE FIELD source_type ON catalog_import_batches TYPE string DEFAULT 'manual';
DEFINE FIELD source_url ON catalog_import_batches TYPE option<string>;
DEFINE FIELD status ON catalog_import_batches TYPE string DEFAULT 'draft';
DEFINE FIELD total_items ON catalog_import_batches TYPE int DEFAULT 0;
DEFINE FIELD valid_items ON catalog_import_batches TYPE int DEFAULT 0;
DEFINE FIELD invalid_items ON catalog_import_batches TYPE int DEFAULT 0;
DEFINE FIELD review_notes ON catalog_import_batches TYPE option<string>;
DEFINE FIELD created_at ON catalog_import_batches TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON catalog_import_batches TYPE datetime VALUE time::now();
DEFINE INDEX catalog_import_batches_tenant ON catalog_import_batches FIELDS tenant_id;
DEFINE INDEX catalog_import_batches_merchant ON catalog_import_batches FIELDS merchant;
DEFINE INDEX catalog_import_batches_status ON catalog_import_batches FIELDS status;

DEFINE TABLE product_drafts SCHEMAFULL;
DEFINE FIELD schema_context ON product_drafts TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON product_drafts TYPE string DEFAULT 'Product' ASSERT $value IN ['Product', 'ProductModel', 'ProductGroup', 'IndividualProduct'];
DEFINE FIELD schema_url ON product_drafts TYPE string VALUE string::concat('https://schema.org/', schema_type);
DEFINE FIELD batch ON product_drafts TYPE record<catalog_import_batches>;
DEFINE FIELD tenant_id ON product_drafts TYPE string;
DEFINE FIELD merchant ON product_drafts TYPE record<merchants>;
DEFINE FIELD name ON product_drafts TYPE string;
DEFINE FIELD description ON product_drafts TYPE option<string>;
DEFINE FIELD sku ON product_drafts TYPE option<string>;
DEFINE FIELD gtin ON product_drafts TYPE option<string>;
DEFINE FIELD mpn ON product_drafts TYPE option<string>;
DEFINE FIELD brand ON product_drafts TYPE option<record<brands>>;
DEFINE FIELD category ON product_drafts TYPE option<string>;
DEFINE FIELD image ON product_drafts TYPE option<array<string>>;
DEFINE FIELD product_group_id ON product_drafts TYPE option<string>;
DEFINE FIELD variant_attributes ON product_drafts TYPE option<object>;
DEFINE FIELD validation_status ON product_drafts TYPE string DEFAULT 'pending';
DEFINE FIELD validation_errors ON product_drafts TYPE array<object> DEFAULT [];
DEFINE FIELD publish_status ON product_drafts TYPE string DEFAULT 'draft';
DEFINE FIELD product ON product_drafts TYPE option<record<products>>;
DEFINE FIELD created_at ON product_drafts TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON product_drafts TYPE datetime VALUE time::now();
DEFINE INDEX product_drafts_batch ON product_drafts FIELDS batch;
DEFINE INDEX product_drafts_merchant ON product_drafts FIELDS merchant;
DEFINE INDEX product_drafts_status ON product_drafts FIELDS publish_status;
DEFINE INDEX product_drafts_validation_status ON product_drafts FIELDS validation_status;
DEFINE INDEX product_drafts_sku ON product_drafts FIELDS sku;

DEFINE TABLE offer_drafts SCHEMAFULL;
DEFINE FIELD schema_context ON offer_drafts TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON offer_drafts TYPE string DEFAULT 'Offer';
DEFINE FIELD schema_url ON offer_drafts TYPE string VALUE 'https://schema.org/Offer';
DEFINE FIELD batch ON offer_drafts TYPE record<catalog_import_batches>;
DEFINE FIELD product_draft ON offer_drafts TYPE record<product_drafts>;
DEFINE FIELD tenant_id ON offer_drafts TYPE string;
DEFINE FIELD merchant ON offer_drafts TYPE record<merchants>;
DEFINE FIELD price ON offer_drafts TYPE decimal;
DEFINE FIELD priceCurrency ON offer_drafts TYPE string DEFAULT 'USD';
DEFINE FIELD availability ON offer_drafts TYPE string DEFAULT 'https://schema.org/InStock';
DEFINE FIELD validFrom ON offer_drafts TYPE option<datetime>;
DEFINE FIELD validThrough ON offer_drafts TYPE option<datetime>;
DEFINE FIELD acceptedPaymentMethod ON offer_drafts TYPE option<array<string>>;
DEFINE FIELD validation_status ON offer_drafts TYPE string DEFAULT 'pending';
DEFINE FIELD validation_errors ON offer_drafts TYPE array<object> DEFAULT [];
DEFINE FIELD publish_status ON offer_drafts TYPE string DEFAULT 'draft';
DEFINE FIELD offer ON offer_drafts TYPE option<record<offers>>;
DEFINE FIELD created_at ON offer_drafts TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON offer_drafts TYPE datetime VALUE time::now();
DEFINE INDEX offer_drafts_batch ON offer_drafts FIELDS batch;
DEFINE INDEX offer_drafts_product_draft ON offer_drafts FIELDS product_draft;
DEFINE INDEX offer_drafts_merchant ON offer_drafts FIELDS merchant;
DEFINE INDEX offer_drafts_status ON offer_drafts FIELDS publish_status;

-- ============================================================
-- Catalog onboarding relations
-- ============================================================

DEFINE TABLE catalog_batch_has_product_draft TYPE RELATION IN catalog_import_batches OUT product_drafts SCHEMAFULL;
DEFINE FIELD created_at ON catalog_batch_has_product_draft TYPE datetime DEFAULT time::now();

DEFINE TABLE product_draft_has_offer_draft TYPE RELATION IN product_drafts OUT offer_drafts SCHEMAFULL;
DEFINE FIELD created_at ON product_draft_has_offer_draft TYPE datetime DEFAULT time::now();

DEFINE TABLE product_draft_published_as TYPE RELATION IN product_drafts OUT products SCHEMAFULL;
DEFINE FIELD created_at ON product_draft_published_as TYPE datetime DEFAULT time::now();

DEFINE TABLE offer_draft_published_as TYPE RELATION IN offer_drafts OUT offers SCHEMAFULL;
DEFINE FIELD created_at ON offer_draft_published_as TYPE datetime DEFAULT time::now();

-- ============================================================
-- Permissions
-- ============================================================

DEFINE TABLE catalog_import_batches PERMISSIONS
  FOR select WHERE $auth.role = 'admin' OR tenant_id = $auth.tenant_id,
  FOR create WHERE $auth.id != NONE,
  FOR update WHERE $auth.role = 'admin' OR tenant_id = $auth.tenant_id,
  FOR delete WHERE $auth.role = 'admin';

DEFINE TABLE product_drafts PERMISSIONS
  FOR select WHERE $auth.role = 'admin' OR tenant_id = $auth.tenant_id,
  FOR create WHERE $auth.id != NONE,
  FOR update WHERE $auth.role = 'admin' OR tenant_id = $auth.tenant_id,
  FOR delete WHERE $auth.role = 'admin';

DEFINE TABLE offer_drafts PERMISSIONS
  FOR select WHERE $auth.role = 'admin' OR tenant_id = $auth.tenant_id,
  FOR create WHERE $auth.id != NONE,
  FOR update WHERE $auth.role = 'admin' OR tenant_id = $auth.tenant_id,
  FOR delete WHERE $auth.role = 'admin';

-- ============================================================
-- Metamodel grounding
-- ============================================================

UPSERT schema_classes:CreateAction CONTENT { name: 'CreateAction', url: 'https://schema.org/CreateAction', parent: schema_classes:Action };
UPSERT schema_classes:UpdateAction CONTENT { name: 'UpdateAction', url: 'https://schema.org/UpdateAction', parent: schema_classes:Action };
RELATE schema_classes:CreateAction->subclass_of->schema_classes:Action;
RELATE schema_classes:UpdateAction->subclass_of->schema_classes:Action;

UPSERT schema_properties:source CONTENT { name: 'source', url: 'https://agennext.dev/schema/source', expected_types: ['URL', 'Text'] };
UPSERT schema_properties:validationStatus CONTENT { name: 'validationStatus', url: 'https://agennext.dev/schema/validationStatus', expected_types: ['DefinedTerm', 'Text'] };
UPSERT schema_properties:publishStatus CONTENT { name: 'publishStatus', url: 'https://agennext.dev/schema/publishStatus', expected_types: ['DefinedTerm', 'Text'] };

UPSERT app_tables:catalog_import_batches CONTENT { name: 'catalog_import_batches', purpose: 'Catalog import and product onboarding batches', primary_schema_class: schema_classes:CreateAction };
UPSERT app_tables:product_drafts CONTENT { name: 'product_drafts', purpose: 'Draft products before publishing', primary_schema_class: schema_classes:Product };
UPSERT app_tables:offer_drafts CONTENT { name: 'offer_drafts', purpose: 'Draft offers before publishing', primary_schema_class: schema_classes:Offer };
RELATE app_tables:catalog_import_batches->table_implements->schema_classes:CreateAction;
RELATE app_tables:product_drafts->table_implements->schema_classes:Product;
RELATE app_tables:offer_drafts->table_implements->schema_classes:Offer;

UPSERT app_fields:catalog_batch_merchant CONTENT { table: app_tables:catalog_import_batches, name: 'merchant', surreal_type: 'record<merchants>', schema_property: schema_properties:seller, schema_range: [schema_classes:Organization], required: true };
UPSERT app_fields:catalog_batch_source_url CONTENT { table: app_tables:catalog_import_batches, name: 'source_url', surreal_type: 'option<string>', schema_property: schema_properties:source };
UPSERT app_fields:catalog_batch_status CONTENT { table: app_tables:catalog_import_batches, name: 'status', surreal_type: 'string', schema_property: schema_properties:actionStatus, required: true };
UPSERT app_fields:product_drafts_name CONTENT { table: app_tables:product_drafts, name: 'name', surreal_type: 'string', schema_property: schema_properties:name, required: true };
UPSERT app_fields:product_drafts_description CONTENT { table: app_tables:product_drafts, name: 'description', surreal_type: 'option<string>', schema_property: schema_properties:description };
UPSERT app_fields:product_drafts_sku CONTENT { table: app_tables:product_drafts, name: 'sku', surreal_type: 'option<string>', schema_property: schema_properties:sku };
UPSERT app_fields:product_drafts_gtin CONTENT { table: app_tables:product_drafts, name: 'gtin', surreal_type: 'option<string>', schema_property: schema_properties:gtin };
UPSERT app_fields:product_drafts_brand CONTENT { table: app_tables:product_drafts, name: 'brand', surreal_type: 'option<record<brands>>', schema_property: schema_properties:brand, schema_range: [schema_classes:Brand] };
UPSERT app_fields:product_drafts_category CONTENT { table: app_tables:product_drafts, name: 'category', surreal_type: 'option<string>', schema_property: schema_properties:category };
UPSERT app_fields:product_drafts_image CONTENT { table: app_tables:product_drafts, name: 'image', surreal_type: 'option<array<string>>', schema_property: schema_properties:image };
UPSERT app_fields:product_drafts_validation_status CONTENT { table: app_tables:product_drafts, name: 'validation_status', surreal_type: 'string', schema_property: schema_properties:validationStatus };
UPSERT app_fields:product_drafts_publish_status CONTENT { table: app_tables:product_drafts, name: 'publish_status', surreal_type: 'string', schema_property: schema_properties:publishStatus };
UPSERT app_fields:offer_drafts_price CONTENT { table: app_tables:offer_drafts, name: 'price', surreal_type: 'decimal', schema_property: schema_properties:price, required: true };
UPSERT app_fields:offer_drafts_priceCurrency CONTENT { table: app_tables:offer_drafts, name: 'priceCurrency', surreal_type: 'string', schema_property: schema_properties:priceCurrency, required: true };
UPSERT app_fields:offer_drafts_availability CONTENT { table: app_tables:offer_drafts, name: 'availability', surreal_type: 'string', schema_property: schema_properties:availability };

RELATE app_fields:catalog_batch_merchant->field_maps_to->schema_properties:seller;
RELATE app_fields:catalog_batch_source_url->field_maps_to->schema_properties:source;
RELATE app_fields:catalog_batch_status->field_maps_to->schema_properties:actionStatus;
RELATE app_fields:product_drafts_name->field_maps_to->schema_properties:name;
RELATE app_fields:product_drafts_description->field_maps_to->schema_properties:description;
RELATE app_fields:product_drafts_sku->field_maps_to->schema_properties:sku;
RELATE app_fields:product_drafts_gtin->field_maps_to->schema_properties:gtin;
RELATE app_fields:product_drafts_brand->field_maps_to->schema_properties:brand;
RELATE app_fields:product_drafts_category->field_maps_to->schema_properties:category;
RELATE app_fields:product_drafts_image->field_maps_to->schema_properties:image;
RELATE app_fields:offer_drafts_price->field_maps_to->schema_properties:price;
RELATE app_fields:offer_drafts_priceCurrency->field_maps_to->schema_properties:priceCurrency;
RELATE app_fields:offer_drafts_availability->field_maps_to->schema_properties:availability;

UPSERT app_relations:catalog_batch_has_product_draft CONTENT { name: 'catalog_batch_has_product_draft', in_table: app_tables:catalog_import_batches, out_table: app_tables:product_drafts, schema_property: schema_properties:result, description: 'Catalog import batch contains product draft' };
UPSERT app_relations:product_draft_has_offer_draft CONTENT { name: 'product_draft_has_offer_draft', in_table: app_tables:product_drafts, out_table: app_tables:offer_drafts, schema_property: schema_properties:offers, description: 'Product draft has offer draft' };
UPSERT app_relations:product_draft_published_as CONTENT { name: 'product_draft_published_as', in_table: app_tables:product_drafts, out_table: app_tables:products, schema_property: schema_properties:result, description: 'Product draft published as product' };
UPSERT app_relations:offer_draft_published_as CONTENT { name: 'offer_draft_published_as', in_table: app_tables:offer_drafts, out_table: app_tables:offers, schema_property: schema_properties:result, description: 'Offer draft published as offer' };
RELATE app_relations:catalog_batch_has_product_draft->relation_maps_to->schema_properties:result;
RELATE app_relations:product_draft_has_offer_draft->relation_maps_to->schema_properties:offers;
RELATE app_relations:product_draft_published_as->relation_maps_to->schema_properties:result;
RELATE app_relations:offer_draft_published_as->relation_maps_to->schema_properties:result;

-- ============================================================
-- DefinedTerms / accepted values
-- ============================================================

UPSERT defined_term_sets:CatalogOnboardingStatus CONTENT { name: 'CatalogOnboardingStatus', url: 'https://agennext.dev/defined-terms/CatalogOnboardingStatus', description: 'Catalog onboarding batch lifecycle statuses.' };
UPSERT defined_terms:CatalogDraft CONTENT { name: 'draft', termCode: 'draft', url: 'https://agennext.dev/defined-terms/catalog-onboarding-status/draft', inDefinedTermSet: defined_term_sets:CatalogOnboardingStatus };
UPSERT defined_terms:CatalogSubmitted CONTENT { name: 'submitted', termCode: 'submitted', url: 'https://agennext.dev/defined-terms/catalog-onboarding-status/submitted', inDefinedTermSet: defined_term_sets:CatalogOnboardingStatus };
UPSERT defined_terms:CatalogInReview CONTENT { name: 'in_review', termCode: 'in_review', url: 'https://agennext.dev/defined-terms/catalog-onboarding-status/in-review', inDefinedTermSet: defined_term_sets:CatalogOnboardingStatus };
UPSERT defined_terms:CatalogApproved CONTENT { name: 'approved', termCode: 'approved', url: 'https://agennext.dev/defined-terms/catalog-onboarding-status/approved', inDefinedTermSet: defined_term_sets:CatalogOnboardingStatus };
UPSERT defined_terms:CatalogRejected CONTENT { name: 'rejected', termCode: 'rejected', url: 'https://agennext.dev/defined-terms/catalog-onboarding-status/rejected', inDefinedTermSet: defined_term_sets:CatalogOnboardingStatus };
UPSERT defined_terms:CatalogPublished CONTENT { name: 'published', termCode: 'published', url: 'https://agennext.dev/defined-terms/catalog-onboarding-status/published', inDefinedTermSet: defined_term_sets:CatalogOnboardingStatus };
RELATE defined_term_sets:CatalogOnboardingStatus->has_defined_term->defined_terms:CatalogDraft;
RELATE defined_term_sets:CatalogOnboardingStatus->has_defined_term->defined_terms:CatalogSubmitted;
RELATE defined_term_sets:CatalogOnboardingStatus->has_defined_term->defined_terms:CatalogInReview;
RELATE defined_term_sets:CatalogOnboardingStatus->has_defined_term->defined_terms:CatalogApproved;
RELATE defined_term_sets:CatalogOnboardingStatus->has_defined_term->defined_terms:CatalogRejected;
RELATE defined_term_sets:CatalogOnboardingStatus->has_defined_term->defined_terms:CatalogPublished;

UPSERT defined_term_sets:CatalogValidationStatus CONTENT { name: 'CatalogValidationStatus', url: 'https://agennext.dev/defined-terms/CatalogValidationStatus', description: 'Catalog draft validation statuses.' };
UPSERT defined_terms:CatalogValidationPending CONTENT { name: 'pending', termCode: 'pending', url: 'https://agennext.dev/defined-terms/catalog-validation-status/pending', inDefinedTermSet: defined_term_sets:CatalogValidationStatus };
UPSERT defined_terms:CatalogValidationValid CONTENT { name: 'valid', termCode: 'valid', url: 'https://agennext.dev/defined-terms/catalog-validation-status/valid', inDefinedTermSet: defined_term_sets:CatalogValidationStatus };
UPSERT defined_terms:CatalogValidationInvalid CONTENT { name: 'invalid', termCode: 'invalid', url: 'https://agennext.dev/defined-terms/catalog-validation-status/invalid', inDefinedTermSet: defined_term_sets:CatalogValidationStatus };
RELATE defined_term_sets:CatalogValidationStatus->has_defined_term->defined_terms:CatalogValidationPending;
RELATE defined_term_sets:CatalogValidationStatus->has_defined_term->defined_terms:CatalogValidationValid;
RELATE defined_term_sets:CatalogValidationStatus->has_defined_term->defined_terms:CatalogValidationInvalid;

UPSERT field_accepted_values:catalog_batch_status CONTENT { field: app_fields:catalog_batch_status, term_set: defined_term_sets:CatalogOnboardingStatus, required: true };
UPSERT field_accepted_values:product_drafts_validation_status CONTENT { field: app_fields:product_drafts_validation_status, term_set: defined_term_sets:CatalogValidationStatus, required: true };
UPSERT field_accepted_values:product_drafts_publish_status CONTENT { field: app_fields:product_drafts_publish_status, term_set: defined_term_sets:CatalogOnboardingStatus, required: true };
UPSERT field_accepted_values:offer_drafts_availability CONTENT { field: app_fields:offer_drafts_availability, term_set: defined_term_sets:ItemAvailability, required: true };
RELATE app_fields:catalog_batch_status->field_accepts_term_set->defined_term_sets:CatalogOnboardingStatus SET required = true;
RELATE app_fields:product_drafts_validation_status->field_accepts_term_set->defined_term_sets:CatalogValidationStatus SET required = true;
RELATE app_fields:product_drafts_publish_status->field_accepts_term_set->defined_term_sets:CatalogOnboardingStatus SET required = true;
RELATE app_fields:offer_drafts_availability->field_accepts_term_set->defined_term_sets:ItemAvailability SET required = true;

-- ============================================================
-- SurrealDB functions for catalog onboarding workflow
-- ============================================================

DEFINE FUNCTION fn::create_catalog_import_batch($data: object) {
  LET $batch = CREATE catalog_import_batches CONTENT {
    tenant_id: $data.tenant_id,
    merchant: $data.merchant,
    submitted_by: $auth.id,
    source_type: $data.source_type ?? 'manual',
    source_url: $data.source_url,
    status: 'draft'
  };

  CREATE commerce_actions CONTENT {
    schema_context: 'https://schema.org',
    schema_type: 'CreateAction',
    schema_url: 'https://schema.org/CreateAction',
    schema_parent: 'https://schema.org/Action',
    agent: $auth.id,
    object: $batch.id,
    result: [$batch.id],
    actionStatus: 'https://schema.org/CompletedActionStatus',
    tenant_id: $data.tenant_id,
    metadata: { flow: 'catalog_onboarding' }
  };

  RETURN $batch;
};

DEFINE FUNCTION fn::add_product_draft($batch_id: record<catalog_import_batches>, $data: object) {
  LET $batch_rows = SELECT * FROM $batch_id;
  IF array::len($batch_rows) = 0 { THROW 'Catalog import batch not found'; };
  LET $batch = $batch_rows[0];

  LET $draft = CREATE product_drafts CONTENT {
    batch: $batch_id,
    tenant_id: $batch.tenant_id,
    merchant: $batch.merchant,
    name: $data.name,
    description: $data.description,
    sku: $data.sku,
    gtin: $data.gtin,
    mpn: $data.mpn,
    brand: $data.brand,
    category: $data.category,
    image: $data.image,
    product_group_id: $data.product_group_id,
    variant_attributes: $data.variant_attributes,
    validation_status: IF $data.name != NONE THEN 'valid' ELSE 'invalid' END,
    validation_errors: IF $data.name != NONE THEN [] ELSE [{ field: 'name', message: 'Product name is required' }] END
  };

  RELATE $batch_id->catalog_batch_has_product_draft->$draft.id;
  UPDATE $batch_id SET total_items += 1;
  RETURN $draft;
};

DEFINE FUNCTION fn::add_offer_draft($product_draft_id: record<product_drafts>, $data: object) {
  LET $product_rows = SELECT * FROM $product_draft_id;
  IF array::len($product_rows) = 0 { THROW 'Product draft not found'; };
  LET $product = $product_rows[0];

  LET $offer_draft = CREATE offer_drafts CONTENT {
    batch: $product.batch,
    product_draft: $product_draft_id,
    tenant_id: $product.tenant_id,
    merchant: $product.merchant,
    price: $data.price,
    priceCurrency: $data.priceCurrency ?? 'USD',
    availability: $data.availability ?? 'https://schema.org/InStock',
    validFrom: $data.validFrom,
    validThrough: $data.validThrough,
    acceptedPaymentMethod: $data.acceptedPaymentMethod,
    validation_status: IF $data.price != NONE AND $data.price > 0 THEN 'valid' ELSE 'invalid' END,
    validation_errors: IF $data.price != NONE AND $data.price > 0 THEN [] ELSE [{ field: 'price', message: 'Offer price must be greater than zero' }] END
  };

  RELATE $product_draft_id->product_draft_has_offer_draft->$offer_draft.id;
  RETURN $offer_draft;
};

DEFINE FUNCTION fn::submit_catalog_import_batch($batch_id: record<catalog_import_batches>) {
  LET $invalid_products = SELECT * FROM product_drafts WHERE batch = $batch_id AND validation_status = 'invalid';
  LET $invalid_offers = SELECT * FROM offer_drafts WHERE batch = $batch_id AND validation_status = 'invalid';
  IF array::len($invalid_products) > 0 OR array::len($invalid_offers) > 0 {
    UPDATE $batch_id MERGE { status: 'rejected', invalid_items: array::len($invalid_products) + array::len($invalid_offers) };
    THROW 'Catalog batch contains invalid product or offer drafts';
  };

  UPDATE $batch_id MERGE { status: 'submitted' };
  RETURN SELECT * FROM $batch_id;
};

DEFINE FUNCTION fn::publish_catalog_import_batch($batch_id: record<catalog_import_batches>) {
  IF $auth.role != 'admin' { THROW 'Admin role required to publish catalog batch'; };

  LET $batch_rows = SELECT * FROM $batch_id;
  IF array::len($batch_rows) = 0 { THROW 'Catalog import batch not found'; };
  LET $batch = $batch_rows[0];

  LET $drafts = SELECT * FROM product_drafts WHERE batch = $batch_id AND validation_status = 'valid';

  FOR $draft IN $drafts {
    LET $product = CREATE products CONTENT {
      schema_context: 'https://schema.org',
      schema_type: $draft.schema_type,
      name: $draft.name,
      description: $draft.description,
      sku: $draft.sku,
      gtin: $draft.gtin,
      mpn: $draft.mpn,
      category: $draft.category,
      image: $draft.image,
      brand: $draft.brand,
      tenant_id: $draft.tenant_id,
      seller: $draft.merchant,
      product_group_id: $draft.product_group_id,
      variant_attributes: $draft.variant_attributes,
      is_active: true
    };

    UPDATE $draft.id MERGE { publish_status: 'published', product: $product.id };
    RELATE $draft.id->product_draft_published_as->$product.id;

    LET $offers = SELECT * FROM offer_drafts WHERE product_draft = $draft.id AND validation_status = 'valid';
    FOR $offer_draft IN $offers {
      LET $offer = CREATE offers CONTENT {
        schema_context: 'https://schema.org',
        schema_type: 'Offer',
        itemOffered: $product.id,
        seller: $offer_draft.merchant,
        tenant_id: $offer_draft.tenant_id,
        price: $offer_draft.price,
        priceCurrency: $offer_draft.priceCurrency,
        availability: $offer_draft.availability,
        validFrom: $offer_draft.validFrom,
        validThrough: $offer_draft.validThrough,
        acceptedPaymentMethod: $offer_draft.acceptedPaymentMethod
      };
      UPDATE $offer_draft.id MERGE { publish_status: 'published', offer: $offer.id };
      RELATE $offer_draft.id->offer_draft_published_as->$offer.id;
      RELATE $product.id->has_offer->$offer.id SET tenant_id = $offer_draft.tenant_id;
    };
  };

  UPDATE $batch_id MERGE { status: 'published', valid_items: array::len($drafts) };

  CREATE commerce_actions CONTENT {
    schema_context: 'https://schema.org',
    schema_type: 'CreateAction',
    schema_url: 'https://schema.org/CreateAction',
    schema_parent: 'https://schema.org/Action',
    agent: $auth.id,
    object: $batch_id,
    actionStatus: 'https://schema.org/CompletedActionStatus',
    tenant_id: $batch.tenant_id,
    metadata: { flow: 'catalog_onboarding', decision: 'published' }
  };

  RETURN SELECT * FROM $batch_id;
};

-- ============================================================
-- Validation rules
-- ============================================================

UPSERT kg_validation_rules:catalog_batch_required_fields CONTENT {
  name: 'catalog_batch_required_fields',
  description: 'Catalog import batches must include tenant_id, merchant, submitted_by, and status.',
  severity: 'error',
  query: 'SELECT * FROM catalog_import_batches WHERE tenant_id = NONE OR merchant = NONE OR submitted_by = NONE OR status = NONE;'
};

UPSERT kg_validation_rules:product_draft_required_fields CONTENT {
  name: 'product_draft_required_fields',
  description: 'Product drafts must include batch, tenant_id, merchant, name, validation_status, and publish_status.',
  severity: 'error',
  query: 'SELECT * FROM product_drafts WHERE batch = NONE OR tenant_id = NONE OR merchant = NONE OR name = NONE OR validation_status = NONE OR publish_status = NONE;'
};

UPSERT kg_validation_rules:offer_draft_required_fields CONTENT {
  name: 'offer_draft_required_fields',
  description: 'Offer drafts must include batch, product_draft, tenant_id, merchant, price, priceCurrency, availability, validation_status, and publish_status.',
  severity: 'error',
  query: 'SELECT * FROM offer_drafts WHERE batch = NONE OR product_draft = NONE OR tenant_id = NONE OR merchant = NONE OR price = NONE OR priceCurrency = NONE OR availability = NONE OR validation_status = NONE OR publish_status = NONE;'
};

UPSERT kg_validation_rules:catalog_status_values_are_defined CONTENT {
  name: 'catalog_status_values_are_defined',
  description: 'Catalog batch and draft publish statuses should be one of the CatalogOnboardingStatus DefinedTerms.',
  severity: 'error',
  query: 'SELECT * FROM catalog_import_batches WHERE status NOT IN (SELECT VALUE termCode FROM defined_terms WHERE inDefinedTermSet = defined_term_sets:CatalogOnboardingStatus);'
};
