-- Vendor onboarding flow
-- SurrealDB-first implementation. No FastAPI route is required.
-- Grounding:
-- - Onboarding application: https://schema.org/RegisterAction
-- - Merchant/vendor: https://schema.org/OnlineBusiness / https://schema.org/Organization
-- - Documents: https://schema.org/DigitalDocument
-- - Workflow steps: https://schema.org/Action

-- ============================================================
-- Vendor onboarding records
-- ============================================================

DEFINE TABLE vendor_onboarding_applications SCHEMAFULL;
DEFINE FIELD schema_context ON vendor_onboarding_applications TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON vendor_onboarding_applications TYPE string DEFAULT 'RegisterAction';
DEFINE FIELD schema_url ON vendor_onboarding_applications TYPE string VALUE 'https://schema.org/RegisterAction';
DEFINE FIELD tenant_id ON vendor_onboarding_applications TYPE string;
DEFINE FIELD applicant ON vendor_onboarding_applications TYPE record<users>;
DEFINE FIELD merchant_name ON vendor_onboarding_applications TYPE string;
DEFINE FIELD legal_name ON vendor_onboarding_applications TYPE option<string>;
DEFINE FIELD email ON vendor_onboarding_applications TYPE string;
DEFINE FIELD telephone ON vendor_onboarding_applications TYPE option<string>;
DEFINE FIELD url ON vendor_onboarding_applications TYPE option<string>;
DEFINE FIELD address ON vendor_onboarding_applications TYPE option<object>;
DEFINE FIELD tax_id ON vendor_onboarding_applications TYPE option<string>;
DEFINE FIELD business_type ON vendor_onboarding_applications TYPE option<string>;
DEFINE FIELD product_categories ON vendor_onboarding_applications TYPE array<string> DEFAULT [];
DEFINE FIELD status ON vendor_onboarding_applications TYPE string DEFAULT 'submitted';
DEFINE FIELD review_notes ON vendor_onboarding_applications TYPE option<string>;
DEFINE FIELD merchant ON vendor_onboarding_applications TYPE option<record<merchants>>;
DEFINE FIELD submitted_at ON vendor_onboarding_applications TYPE datetime DEFAULT time::now();
DEFINE FIELD reviewed_at ON vendor_onboarding_applications TYPE option<datetime>;
DEFINE FIELD created_at ON vendor_onboarding_applications TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON vendor_onboarding_applications TYPE datetime VALUE time::now();
DEFINE INDEX vendor_onboarding_tenant ON vendor_onboarding_applications FIELDS tenant_id;
DEFINE INDEX vendor_onboarding_applicant ON vendor_onboarding_applications FIELDS applicant;
DEFINE INDEX vendor_onboarding_status ON vendor_onboarding_applications FIELDS status;
DEFINE INDEX vendor_onboarding_email ON vendor_onboarding_applications FIELDS email;

DEFINE TABLE onboarding_documents SCHEMAFULL;
DEFINE FIELD schema_context ON onboarding_documents TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON onboarding_documents TYPE string DEFAULT 'DigitalDocument';
DEFINE FIELD schema_url ON onboarding_documents TYPE string VALUE 'https://schema.org/DigitalDocument';
DEFINE FIELD application ON onboarding_documents TYPE record<vendor_onboarding_applications>;
DEFINE FIELD document_type ON onboarding_documents TYPE string;
DEFINE FIELD name ON onboarding_documents TYPE string;
DEFINE FIELD url ON onboarding_documents TYPE string;
DEFINE FIELD status ON onboarding_documents TYPE string DEFAULT 'submitted';
DEFINE FIELD metadata ON onboarding_documents TYPE object DEFAULT {};
DEFINE FIELD created_at ON onboarding_documents TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON onboarding_documents TYPE datetime VALUE time::now();
DEFINE INDEX onboarding_documents_application ON onboarding_documents FIELDS application;
DEFINE INDEX onboarding_documents_type ON onboarding_documents FIELDS document_type;
DEFINE INDEX onboarding_documents_status ON onboarding_documents FIELDS status;

DEFINE TABLE onboarding_steps SCHEMAFULL;
DEFINE FIELD schema_context ON onboarding_steps TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON onboarding_steps TYPE string DEFAULT 'Action';
DEFINE FIELD schema_url ON onboarding_steps TYPE string VALUE 'https://schema.org/Action';
DEFINE FIELD application ON onboarding_steps TYPE record<vendor_onboarding_applications>;
DEFINE FIELD name ON onboarding_steps TYPE string;
DEFINE FIELD status ON onboarding_steps TYPE string DEFAULT 'pending';
DEFINE FIELD completed_at ON onboarding_steps TYPE option<datetime>;
DEFINE FIELD metadata ON onboarding_steps TYPE object DEFAULT {};
DEFINE FIELD created_at ON onboarding_steps TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON onboarding_steps TYPE datetime VALUE time::now();
DEFINE INDEX onboarding_steps_application ON onboarding_steps FIELDS application;
DEFINE INDEX onboarding_steps_status ON onboarding_steps FIELDS status;

-- ============================================================
-- Vendor onboarding relations
-- ============================================================

DEFINE TABLE onboarding_application_creates_merchant TYPE RELATION IN vendor_onboarding_applications OUT merchants SCHEMAFULL;
DEFINE FIELD created_at ON onboarding_application_creates_merchant TYPE datetime DEFAULT time::now();

DEFINE TABLE onboarding_has_document TYPE RELATION IN vendor_onboarding_applications OUT onboarding_documents SCHEMAFULL;
DEFINE FIELD created_at ON onboarding_has_document TYPE datetime DEFAULT time::now();

DEFINE TABLE onboarding_has_step TYPE RELATION IN vendor_onboarding_applications OUT onboarding_steps SCHEMAFULL;
DEFINE FIELD created_at ON onboarding_has_step TYPE datetime DEFAULT time::now();

-- ============================================================
-- Permissions
-- ============================================================

DEFINE TABLE vendor_onboarding_applications PERMISSIONS
  FOR select WHERE $auth.role = 'admin' OR tenant_id = $auth.tenant_id OR applicant = $auth.id,
  FOR create WHERE $auth.id != NONE,
  FOR update WHERE $auth.role = 'admin' OR applicant = $auth.id,
  FOR delete WHERE $auth.role = 'admin';

DEFINE TABLE onboarding_documents PERMISSIONS
  FOR select WHERE $auth.role = 'admin' OR application.applicant = $auth.id,
  FOR create WHERE $auth.id != NONE,
  FOR update WHERE $auth.role = 'admin' OR application.applicant = $auth.id,
  FOR delete WHERE $auth.role = 'admin';

DEFINE TABLE onboarding_steps PERMISSIONS
  FOR select WHERE $auth.role = 'admin' OR application.applicant = $auth.id,
  FOR create, update, delete WHERE $auth.role = 'admin';

-- ============================================================
-- Schema.org metamodel grounding
-- ============================================================

UPSERT schema_classes:InteractAction CONTENT { name: 'InteractAction', url: 'https://schema.org/InteractAction', parent: schema_classes:Action };
UPSERT schema_classes:RegisterAction CONTENT { name: 'RegisterAction', url: 'https://schema.org/RegisterAction', parent: schema_classes:InteractAction };
UPSERT schema_classes:DigitalDocument CONTENT { name: 'DigitalDocument', url: 'https://schema.org/DigitalDocument', parent: schema_classes:CreativeWork };
UPSERT schema_classes:CreativeWork CONTENT { name: 'CreativeWork', url: 'https://schema.org/CreativeWork', parent: schema_classes:Thing };
RELATE schema_classes:InteractAction->subclass_of->schema_classes:Action;
RELATE schema_classes:RegisterAction->subclass_of->schema_classes:InteractAction;
RELATE schema_classes:CreativeWork->subclass_of->schema_classes:Thing;
RELATE schema_classes:DigitalDocument->subclass_of->schema_classes:CreativeWork;

UPSERT schema_properties:legalName CONTENT { name: 'legalName', url: 'https://schema.org/legalName', expected_types: ['Text'] };
UPSERT schema_properties:email CONTENT { name: 'email', url: 'https://schema.org/email', expected_types: ['Text'] };
UPSERT schema_properties:telephone CONTENT { name: 'telephone', url: 'https://schema.org/telephone', expected_types: ['Text'] };
UPSERT schema_properties:address CONTENT { name: 'address', url: 'https://schema.org/address', expected_types: ['PostalAddress', 'Text'] };
UPSERT schema_properties:application CONTENT { name: 'application', url: 'https://agennext.dev/schema/application', expected_types: ['RegisterAction'] };
UPSERT schema_properties:status CONTENT { name: 'status', url: 'https://agennext.dev/schema/status', expected_types: ['DefinedTerm', 'Text'] };

UPSERT app_tables:vendor_onboarding_applications CONTENT { name: 'vendor_onboarding_applications', purpose: 'Vendor onboarding applications', primary_schema_class: schema_classes:RegisterAction };
UPSERT app_tables:onboarding_documents CONTENT { name: 'onboarding_documents', purpose: 'Vendor onboarding documents', primary_schema_class: schema_classes:DigitalDocument };
UPSERT app_tables:onboarding_steps CONTENT { name: 'onboarding_steps', purpose: 'Vendor onboarding workflow steps', primary_schema_class: schema_classes:Action };
RELATE app_tables:vendor_onboarding_applications->table_implements->schema_classes:RegisterAction;
RELATE app_tables:onboarding_documents->table_implements->schema_classes:DigitalDocument;
RELATE app_tables:onboarding_steps->table_implements->schema_classes:Action;

UPSERT app_fields:vendor_onboarding_applicant CONTENT { table: app_tables:vendor_onboarding_applications, name: 'applicant', surreal_type: 'record<users>', schema_property: schema_properties:agent, schema_range: [schema_classes:Person], required: true };
UPSERT app_fields:vendor_onboarding_merchant_name CONTENT { table: app_tables:vendor_onboarding_applications, name: 'merchant_name', surreal_type: 'string', schema_property: schema_properties:name, required: true };
UPSERT app_fields:vendor_onboarding_legal_name CONTENT { table: app_tables:vendor_onboarding_applications, name: 'legal_name', surreal_type: 'option<string>', schema_property: schema_properties:legalName };
UPSERT app_fields:vendor_onboarding_email CONTENT { table: app_tables:vendor_onboarding_applications, name: 'email', surreal_type: 'string', schema_property: schema_properties:email, required: true };
UPSERT app_fields:vendor_onboarding_telephone CONTENT { table: app_tables:vendor_onboarding_applications, name: 'telephone', surreal_type: 'option<string>', schema_property: schema_properties:telephone };
UPSERT app_fields:vendor_onboarding_url CONTENT { table: app_tables:vendor_onboarding_applications, name: 'url', surreal_type: 'option<string>', schema_property: schema_properties:url };
UPSERT app_fields:vendor_onboarding_address CONTENT { table: app_tables:vendor_onboarding_applications, name: 'address', surreal_type: 'option<object>', schema_property: schema_properties:address };
UPSERT app_fields:vendor_onboarding_status CONTENT { table: app_tables:vendor_onboarding_applications, name: 'status', surreal_type: 'string', schema_property: schema_properties:status, required: true };

RELATE app_fields:vendor_onboarding_applicant->field_maps_to->schema_properties:agent;
RELATE app_fields:vendor_onboarding_merchant_name->field_maps_to->schema_properties:name;
RELATE app_fields:vendor_onboarding_legal_name->field_maps_to->schema_properties:legalName;
RELATE app_fields:vendor_onboarding_email->field_maps_to->schema_properties:email;
RELATE app_fields:vendor_onboarding_telephone->field_maps_to->schema_properties:telephone;
RELATE app_fields:vendor_onboarding_url->field_maps_to->schema_properties:url;
RELATE app_fields:vendor_onboarding_address->field_maps_to->schema_properties:address;
RELATE app_fields:vendor_onboarding_status->field_maps_to->schema_properties:status;

UPSERT app_relations:onboarding_application_creates_merchant CONTENT { name: 'onboarding_application_creates_merchant', in_table: app_tables:vendor_onboarding_applications, out_table: app_tables:merchants, schema_property: schema_properties:result, description: 'Approved onboarding application creates merchant' };
UPSERT app_relations:onboarding_has_document CONTENT { name: 'onboarding_has_document', in_table: app_tables:vendor_onboarding_applications, out_table: app_tables:onboarding_documents, schema_property: schema_properties:object, description: 'Onboarding application has submitted document' };
UPSERT app_relations:onboarding_has_step CONTENT { name: 'onboarding_has_step', in_table: app_tables:vendor_onboarding_applications, out_table: app_tables:onboarding_steps, schema_property: schema_properties:actionStatus, description: 'Onboarding application has workflow step' };
RELATE app_relations:onboarding_application_creates_merchant->relation_maps_to->schema_properties:result;
RELATE app_relations:onboarding_has_document->relation_maps_to->schema_properties:object;
RELATE app_relations:onboarding_has_step->relation_maps_to->schema_properties:actionStatus;

-- ============================================================
-- DefinedTerms / accepted values
-- ============================================================

UPSERT defined_term_sets:VendorOnboardingStatus CONTENT { name: 'VendorOnboardingStatus', url: 'https://agennext.dev/defined-terms/VendorOnboardingStatus', description: 'Vendor onboarding lifecycle statuses.' };
UPSERT defined_terms:VendorOnboardingSubmitted CONTENT { name: 'submitted', termCode: 'submitted', url: 'https://agennext.dev/defined-terms/vendor-onboarding-status/submitted', inDefinedTermSet: defined_term_sets:VendorOnboardingStatus };
UPSERT defined_terms:VendorOnboardingInReview CONTENT { name: 'in_review', termCode: 'in_review', url: 'https://agennext.dev/defined-terms/vendor-onboarding-status/in-review', inDefinedTermSet: defined_term_sets:VendorOnboardingStatus };
UPSERT defined_terms:VendorOnboardingApproved CONTENT { name: 'approved', termCode: 'approved', url: 'https://agennext.dev/defined-terms/vendor-onboarding-status/approved', inDefinedTermSet: defined_term_sets:VendorOnboardingStatus };
UPSERT defined_terms:VendorOnboardingRejected CONTENT { name: 'rejected', termCode: 'rejected', url: 'https://agennext.dev/defined-terms/vendor-onboarding-status/rejected', inDefinedTermSet: defined_term_sets:VendorOnboardingStatus };
UPSERT defined_terms:VendorOnboardingNeedsInfo CONTENT { name: 'needs_info', termCode: 'needs_info', url: 'https://agennext.dev/defined-terms/vendor-onboarding-status/needs-info', inDefinedTermSet: defined_term_sets:VendorOnboardingStatus };
RELATE defined_term_sets:VendorOnboardingStatus->has_defined_term->defined_terms:VendorOnboardingSubmitted;
RELATE defined_term_sets:VendorOnboardingStatus->has_defined_term->defined_terms:VendorOnboardingInReview;
RELATE defined_term_sets:VendorOnboardingStatus->has_defined_term->defined_terms:VendorOnboardingApproved;
RELATE defined_term_sets:VendorOnboardingStatus->has_defined_term->defined_terms:VendorOnboardingRejected;
RELATE defined_term_sets:VendorOnboardingStatus->has_defined_term->defined_terms:VendorOnboardingNeedsInfo;
UPSERT field_accepted_values:vendor_onboarding_status CONTENT { field: app_fields:vendor_onboarding_status, term_set: defined_term_sets:VendorOnboardingStatus, required: true };
RELATE app_fields:vendor_onboarding_status->field_accepts_term_set->defined_term_sets:VendorOnboardingStatus SET required = true;

-- ============================================================
-- SurrealDB functions for onboarding workflow
-- ============================================================

DEFINE FUNCTION fn::submit_vendor_onboarding($data: object) {
  LET $application = CREATE vendor_onboarding_applications CONTENT {
    tenant_id: $data.tenant_id,
    applicant: $auth.id,
    merchant_name: $data.merchant_name,
    legal_name: $data.legal_name,
    email: $data.email,
    telephone: $data.telephone,
    url: $data.url,
    address: $data.address,
    tax_id: $data.tax_id,
    business_type: $data.business_type,
    product_categories: $data.product_categories ?? [],
    status: 'submitted'
  };

  CREATE commerce_actions CONTENT {
    schema_context: 'https://schema.org',
    schema_type: 'RegisterAction',
    schema_url: 'https://schema.org/RegisterAction',
    schema_parent: 'https://schema.org/InteractAction',
    agent: $auth.id,
    object: $application.id,
    result: [$application.id],
    actionStatus: 'https://schema.org/CompletedActionStatus',
    tenant_id: $data.tenant_id,
    metadata: { flow: 'vendor_onboarding' }
  };

  CREATE onboarding_steps CONTENT { application: $application.id, name: 'application_submitted', status: 'completed', completed_at: time::now() };
  CREATE onboarding_steps CONTENT { application: $application.id, name: 'document_review', status: 'pending' };
  CREATE onboarding_steps CONTENT { application: $application.id, name: 'business_review', status: 'pending' };
  CREATE onboarding_steps CONTENT { application: $application.id, name: 'approval', status: 'pending' };

  RETURN $application;
};

DEFINE FUNCTION fn::approve_vendor_onboarding($application_id: record<vendor_onboarding_applications>, $review_notes: option<string>) {
  IF $auth.role != 'admin' {
    THROW 'Admin role required to approve vendor onboarding';
  };

  LET $application = SELECT * FROM $application_id;
  IF array::len($application) = 0 {
    THROW 'Vendor onboarding application not found';
  };
  LET $app = $application[0];

  LET $merchant = CREATE merchants CONTENT {
    schema_context: 'https://schema.org',
    schema_type: 'OnlineBusiness',
    name: $app.merchant_name,
    description: $app.legal_name,
    url: $app.url,
    email: $app.email,
    telephone: $app.telephone,
    tenant_id: $app.tenant_id,
    address: $app.address
  };

  UPDATE $application_id MERGE {
    status: 'approved',
    review_notes: $review_notes,
    reviewed_at: time::now(),
    merchant: $merchant.id
  };

  RELATE $application_id->onboarding_application_creates_merchant->$merchant.id;

  UPDATE onboarding_steps SET status = 'completed', completed_at = time::now() WHERE application = $application_id AND name = 'approval';

  CREATE commerce_actions CONTENT {
    schema_context: 'https://schema.org',
    schema_type: 'RegisterAction',
    schema_url: 'https://schema.org/RegisterAction',
    schema_parent: 'https://schema.org/InteractAction',
    agent: $auth.id,
    object: $application_id,
    result: [$merchant.id],
    actionStatus: 'https://schema.org/CompletedActionStatus',
    tenant_id: $app.tenant_id,
    metadata: { flow: 'vendor_onboarding', decision: 'approved' }
  };

  RETURN $merchant;
};

DEFINE FUNCTION fn::reject_vendor_onboarding($application_id: record<vendor_onboarding_applications>, $review_notes: string) {
  IF $auth.role != 'admin' {
    THROW 'Admin role required to reject vendor onboarding';
  };

  LET $application = SELECT * FROM $application_id;
  IF array::len($application) = 0 {
    THROW 'Vendor onboarding application not found';
  };
  LET $app = $application[0];

  UPDATE $application_id MERGE {
    status: 'rejected',
    review_notes: $review_notes,
    reviewed_at: time::now()
  };

  UPDATE onboarding_steps SET status = 'failed', completed_at = time::now() WHERE application = $application_id AND name = 'approval';

  CREATE commerce_actions CONTENT {
    schema_context: 'https://schema.org',
    schema_type: 'RegisterAction',
    schema_url: 'https://schema.org/RegisterAction',
    schema_parent: 'https://schema.org/InteractAction',
    agent: $auth.id,
    object: $application_id,
    actionStatus: 'https://schema.org/FailedActionStatus',
    tenant_id: $app.tenant_id,
    metadata: { flow: 'vendor_onboarding', decision: 'rejected', notes: $review_notes }
  };

  RETURN SELECT * FROM $application_id;
};

-- ============================================================
-- Validation rules
-- ============================================================

UPSERT kg_validation_rules:vendor_onboarding_required_fields CONTENT {
  name: 'vendor_onboarding_required_fields',
  description: 'Vendor onboarding applications must include applicant, tenant_id, merchant_name, email, and status.',
  severity: 'error',
  query: 'SELECT * FROM vendor_onboarding_applications WHERE applicant = NONE OR tenant_id = NONE OR merchant_name = NONE OR email = NONE OR status = NONE;'
};

UPSERT kg_validation_rules:vendor_onboarding_status_values_are_defined CONTENT {
  name: 'vendor_onboarding_status_values_are_defined',
  description: 'vendor_onboarding_applications.status should be one of the VendorOnboardingStatus DefinedTerms.',
  severity: 'error',
  query: 'SELECT * FROM vendor_onboarding_applications WHERE status NOT IN (SELECT VALUE termCode FROM defined_terms WHERE inDefinedTermSet = defined_term_sets:VendorOnboardingStatus);'
};
