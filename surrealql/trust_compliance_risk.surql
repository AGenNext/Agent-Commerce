-- Trust, compliance, and risk
-- SurrealDB-first implementation.
-- Grounding:
-- - Merchant identity: https://schema.org/Organization
-- - Permits/licenses: https://schema.org/Permit
-- - Assessments: https://schema.org/AssessAction

DEFINE TABLE compliance_profiles SCHEMAFULL;
DEFINE FIELD tenant_id ON compliance_profiles TYPE string;
DEFINE FIELD merchant ON compliance_profiles TYPE record<merchants>;
DEFINE FIELD status ON compliance_profiles TYPE string DEFAULT 'pending';
DEFINE FIELD risk_score ON compliance_profiles TYPE number DEFAULT 0;
DEFINE FIELD review_notes ON compliance_profiles TYPE option<string>;
DEFINE FIELD approved_at ON compliance_profiles TYPE option<datetime>;
DEFINE FIELD updated_at ON compliance_profiles TYPE datetime VALUE time::now();
DEFINE INDEX compliance_profiles_merchant ON compliance_profiles FIELDS merchant UNIQUE;

DEFINE TABLE compliance_documents SCHEMAFULL;
DEFINE FIELD profile ON compliance_documents TYPE record<compliance_profiles>;
DEFINE FIELD schema_context ON compliance_documents TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON compliance_documents TYPE string DEFAULT 'Permit';
DEFINE FIELD schema_url ON compliance_documents TYPE string VALUE 'https://schema.org/Permit';
DEFINE FIELD document_type ON compliance_documents TYPE string;
DEFINE FIELD name ON compliance_documents TYPE string;
DEFINE FIELD url ON compliance_documents TYPE string;
DEFINE FIELD expires_at ON compliance_documents TYPE option<datetime>;
DEFINE FIELD verification_status ON compliance_documents TYPE string DEFAULT 'pending';
DEFINE FIELD created_at ON compliance_documents TYPE datetime DEFAULT time::now();
DEFINE INDEX compliance_documents_profile ON compliance_documents FIELDS profile;

DEFINE TABLE screening_results SCHEMAFULL;
DEFINE FIELD profile ON screening_results TYPE record<compliance_profiles>;
DEFINE FIELD screening_type ON screening_results TYPE string;
DEFINE FIELD provider ON screening_results TYPE string;
DEFINE FIELD score ON screening_results TYPE number DEFAULT 0;
DEFINE FIELD outcome ON screening_results TYPE string DEFAULT 'clear';
DEFINE FIELD raw_result ON screening_results TYPE object DEFAULT {};
DEFINE FIELD created_at ON screening_results TYPE datetime DEFAULT time::now();
DEFINE INDEX screening_results_profile ON screening_results FIELDS profile;

DEFINE TABLE policy_violations SCHEMAFULL;
DEFINE FIELD tenant_id ON policy_violations TYPE string;
DEFINE FIELD merchant ON policy_violations TYPE record<merchants>;
DEFINE FIELD severity ON policy_violations TYPE string DEFAULT 'low';
DEFINE FIELD category ON policy_violations TYPE string;
DEFINE FIELD description ON policy_violations TYPE string;
DEFINE FIELD status ON policy_violations TYPE string DEFAULT 'open';
DEFINE FIELD created_at ON policy_violations TYPE datetime DEFAULT time::now();
DEFINE INDEX policy_violations_merchant ON policy_violations FIELDS merchant;

DEFINE TABLE account_holds SCHEMAFULL;
DEFINE FIELD tenant_id ON account_holds TYPE string;
DEFINE FIELD merchant ON account_holds TYPE record<merchants>;
DEFINE FIELD reason ON account_holds TYPE string;
DEFINE FIELD status ON account_holds TYPE string DEFAULT 'active';
DEFINE FIELD created_at ON account_holds TYPE datetime DEFAULT time::now();
DEFINE FIELD released_at ON account_holds TYPE option<datetime>;
DEFINE INDEX account_holds_merchant ON account_holds FIELDS merchant;

DEFINE FUNCTION fn::create_compliance_profile($merchant: record<merchants>) {
  RETURN CREATE compliance_profiles CONTENT {
    tenant_id: $auth.tenant_id,
    merchant: $merchant,
    status: 'pending'
  };
};

DEFINE FUNCTION fn::record_screening_result($profile: record<compliance_profiles>, $data: object) {
  LET $result = CREATE screening_results CONTENT {
    profile: $profile,
    screening_type: $data.screening_type,
    provider: $data.provider,
    score: $data.score,
    outcome: $data.outcome,
    raw_result: $data.raw_result ?? {}
  };

  LET $profile_row = (SELECT * FROM $profile)[0];
  UPDATE $profile MERGE {
    risk_score: math::max($profile_row.risk_score, $data.score),
    status: IF $data.outcome = 'clear' THEN 'approved' ELSE 'review_required' END,
    approved_at: IF $data.outcome = 'clear' THEN time::now() ELSE NONE END
  };

  RETURN $result;
};

DEFINE FUNCTION fn::place_account_hold($merchant: record<merchants>, $reason: string) {
  IF $auth.role != 'admin' { THROW 'Admin role required'; };
  RETURN CREATE account_holds CONTENT {
    tenant_id: $auth.tenant_id,
    merchant: $merchant,
    reason: $reason,
    status: 'active'
  };
};
