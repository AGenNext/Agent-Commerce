-- Digital Identity & Commerce Ecosystem layer for Agent-Commerce
-- Models a GoIDC-style "global digital identity ecosystem":
--   digital identity profiles (AI business cards), membership programs/tiers,
--   prepaid activation E-pins, a referral network, and referral commissions.
--
-- This layer sits on top of the existing security + commerce schemas and reuses
-- their `users`, `merchants`, and settlement conventions. Apply AFTER:
--   security.surql, commerce_schema_org.surql, settlements_payouts.surql
--
-- Grounding (schema.org):
-- - Digital identity / business card: https://schema.org/Person + https://schema.org/ProfilePage
-- - Membership program:               https://schema.org/MemberProgram
-- - Membership tier:                  https://schema.org/MemberProgramTier
-- - Active membership:                https://schema.org/ProgramMembership
-- - Prepaid activation pin:           https://schema.org/Order (digital voucher-style)
-- - Referral / affiliate commission:  https://schema.org/MoneyTransfer

-- ============================================================
-- Digital identity profile (the "AI business card")
-- Schema.org: ProfilePage describing a Person
-- ============================================================

DEFINE TABLE identity_profiles SCHEMAFULL;
DEFINE FIELD schema_context ON identity_profiles TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON identity_profiles TYPE string DEFAULT 'ProfilePage';
DEFINE FIELD schema_url ON identity_profiles TYPE string VALUE 'https://schema.org/ProfilePage';
DEFINE FIELD owner ON identity_profiles TYPE record<users>;
DEFINE FIELD tenant_id ON identity_profiles TYPE string;
DEFINE FIELD handle ON identity_profiles TYPE string;             -- public slug, e.g. goidc.in/u/<handle>
DEFINE FIELD display_name ON identity_profiles TYPE string;
DEFINE FIELD headline ON identity_profiles TYPE option<string>;
DEFINE FIELD bio ON identity_profiles TYPE option<string>;
DEFINE FIELD avatar ON identity_profiles TYPE option<string>;
DEFINE FIELD cover_image ON identity_profiles TYPE option<string>;
DEFINE FIELD email ON identity_profiles TYPE option<string>;
DEFINE FIELD telephone ON identity_profiles TYPE option<string>;
DEFINE FIELD organization ON identity_profiles TYPE option<record<merchants>>;
-- Clickable links / social handles shown on the card: [{ label, url, kind }]
DEFINE FIELD links ON identity_profiles TYPE array<object> DEFAULT [];
-- Verifiable-credential style attestations: [{ type, issuer, status, issued_at }]
DEFINE FIELD credentials ON identity_profiles TYPE array<object> DEFAULT [];
DEFINE FIELD is_verified ON identity_profiles TYPE bool DEFAULT false;
DEFINE FIELD is_public ON identity_profiles TYPE bool DEFAULT true;
DEFINE FIELD view_count ON identity_profiles TYPE int DEFAULT 0;
DEFINE FIELD created_at ON identity_profiles TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON identity_profiles TYPE datetime VALUE time::now();
DEFINE INDEX identity_profiles_handle_unique ON identity_profiles FIELDS handle UNIQUE;
DEFINE INDEX identity_profiles_owner ON identity_profiles FIELDS owner;
DEFINE INDEX identity_profiles_tenant ON identity_profiles FIELDS tenant_id;
DEFINE INDEX identity_profiles_name_search ON identity_profiles FIELDS display_name SEARCH ANALYZER ascii BM25;

-- Engagement tracking when a card is viewed / a link is tapped.
DEFINE TABLE profile_views SCHEMAFULL;
DEFINE FIELD profile ON profile_views TYPE record<identity_profiles>;
DEFINE FIELD tenant_id ON profile_views TYPE string;
DEFINE FIELD event_type ON profile_views TYPE string DEFAULT 'view' ASSERT $value IN ['view', 'link_tap', 'save_contact', 'share'];
DEFINE FIELD link_label ON profile_views TYPE option<string>;
DEFINE FIELD referrer ON profile_views TYPE option<string>;
DEFINE FIELD ip_hash ON profile_views TYPE option<string>;
DEFINE FIELD created_at ON profile_views TYPE datetime DEFAULT time::now();
DEFINE INDEX profile_views_profile ON profile_views FIELDS profile;
DEFINE INDEX profile_views_created_at ON profile_views FIELDS created_at;

-- ============================================================
-- Membership programs and tiers (the "plans")
-- Schema.org: MemberProgram / MemberProgramTier
-- ============================================================

DEFINE TABLE membership_programs SCHEMAFULL;
DEFINE FIELD schema_context ON membership_programs TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON membership_programs TYPE string DEFAULT 'MemberProgram';
DEFINE FIELD schema_url ON membership_programs TYPE string VALUE 'https://schema.org/MemberProgram';
DEFINE FIELD name ON membership_programs TYPE string;
DEFINE FIELD description ON membership_programs TYPE option<string>;
DEFINE FIELD tenant_id ON membership_programs TYPE string;
DEFINE FIELD is_active ON membership_programs TYPE bool DEFAULT true;
DEFINE FIELD created_at ON membership_programs TYPE datetime DEFAULT time::now();
DEFINE INDEX membership_programs_tenant ON membership_programs FIELDS tenant_id;

DEFINE TABLE membership_tiers SCHEMAFULL;
DEFINE FIELD schema_context ON membership_tiers TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON membership_tiers TYPE string DEFAULT 'MemberProgramTier';
DEFINE FIELD schema_url ON membership_tiers TYPE string VALUE 'https://schema.org/MemberProgramTier';
DEFINE FIELD program ON membership_tiers TYPE record<membership_programs>;
DEFINE FIELD tenant_id ON membership_tiers TYPE string;
DEFINE FIELD name ON membership_tiers TYPE string;                -- e.g. Personal, Professional, Business
DEFINE FIELD price ON membership_tiers TYPE decimal DEFAULT 0;
DEFINE FIELD priceCurrency ON membership_tiers TYPE string DEFAULT 'USD';
DEFINE FIELD billing_period ON membership_tiers TYPE string DEFAULT 'P1Y' ;  -- ISO 8601 duration
DEFINE FIELD epins_required ON membership_tiers TYPE int DEFAULT 1;          -- E-pins needed to activate
DEFINE FIELD benefits ON membership_tiers TYPE array<string> DEFAULT [];
-- Referral commission rate paid to the direct referrer when this tier is purchased.
DEFINE FIELD referral_rate ON membership_tiers TYPE decimal DEFAULT 0;
DEFINE FIELD is_active ON membership_tiers TYPE bool DEFAULT true;
DEFINE FIELD created_at ON membership_tiers TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON membership_tiers TYPE datetime VALUE time::now();
DEFINE INDEX membership_tiers_program ON membership_tiers FIELDS program;
DEFINE INDEX membership_tiers_tenant ON membership_tiers FIELDS tenant_id;

DEFINE TABLE memberships SCHEMAFULL;
DEFINE FIELD schema_context ON memberships TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON memberships TYPE string DEFAULT 'ProgramMembership';
DEFINE FIELD schema_url ON memberships TYPE string VALUE 'https://schema.org/ProgramMembership';
DEFINE FIELD member ON memberships TYPE record<users>;
DEFINE FIELD tier ON memberships TYPE record<membership_tiers>;
DEFINE FIELD tenant_id ON memberships TYPE string;
DEFINE FIELD membershipNumber ON memberships TYPE string;
DEFINE FIELD status ON memberships TYPE string DEFAULT 'active' ASSERT $value IN ['pending', 'active', 'expired', 'cancelled'];
DEFINE FIELD activated_by_epin ON memberships TYPE option<record<epins>>;
DEFINE FIELD starts_at ON memberships TYPE datetime DEFAULT time::now();
DEFINE FIELD expires_at ON memberships TYPE option<datetime>;
DEFINE FIELD created_at ON memberships TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON memberships TYPE datetime VALUE time::now();
DEFINE INDEX memberships_number_unique ON memberships FIELDS membershipNumber UNIQUE;
DEFINE INDEX memberships_member ON memberships FIELDS member;
DEFINE INDEX memberships_tier ON memberships FIELDS tier;
DEFINE INDEX memberships_status ON memberships FIELDS status;

-- ============================================================
-- E-pins (prepaid activation pins)
-- A purchased, single-use code that activates a membership tier.
-- ============================================================

DEFINE TABLE epins SCHEMAFULL;
DEFINE FIELD code ON epins TYPE string;
DEFINE FIELD tenant_id ON epins TYPE string;
DEFINE FIELD tier ON epins TYPE record<membership_tiers>;
DEFINE FIELD status ON epins TYPE string DEFAULT 'unused' ASSERT $value IN ['unused', 'reserved', 'redeemed', 'void'];
DEFINE FIELD face_value ON epins TYPE decimal DEFAULT 0;
DEFINE FIELD currency ON epins TYPE string DEFAULT 'USD';
DEFINE FIELD issued_to ON epins TYPE option<record<users>>;       -- buyer/distributor holding the pin
DEFINE FIELD redeemed_by ON epins TYPE option<record<users>>;
DEFINE FIELD redeemed_at ON epins TYPE option<datetime>;
DEFINE FIELD source_payment ON epins TYPE option<record<payments>>;
DEFINE FIELD created_at ON epins TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON epins TYPE datetime VALUE time::now();
DEFINE INDEX epins_code_unique ON epins FIELDS code UNIQUE;
DEFINE INDEX epins_tenant ON epins FIELDS tenant_id;
DEFINE INDEX epins_status ON epins FIELDS status;
DEFINE INDEX epins_issued_to ON epins FIELDS issued_to;

-- ============================================================
-- Referral network + referral commissions
-- Graph: a user `referred` another user (the sponsor relationship).
-- Ledger: commissions credited to referrers, reusing the settlement model's
-- MoneyTransfer grounding.
-- ============================================================

DEFINE TABLE referred TYPE RELATION IN users OUT users SCHEMAFULL;
DEFINE FIELD tenant_id ON referred TYPE string;
DEFINE FIELD code ON referred TYPE option<string>;               -- the referral code used at signup
DEFINE FIELD depth ON referred TYPE int DEFAULT 1;               -- 1 = direct sponsor
DEFINE FIELD created_at ON referred TYPE datetime DEFAULT time::now();
DEFINE INDEX referred_unique ON referred FIELDS in, out UNIQUE;

DEFINE TABLE referral_commissions SCHEMAFULL;
DEFINE FIELD schema_context ON referral_commissions TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON referral_commissions TYPE string DEFAULT 'MoneyTransfer';
DEFINE FIELD schema_url ON referral_commissions TYPE string VALUE 'https://schema.org/MoneyTransfer';
DEFINE FIELD tenant_id ON referral_commissions TYPE string;
DEFINE FIELD beneficiary ON referral_commissions TYPE record<users>;   -- the referrer being paid
DEFINE FIELD source_member ON referral_commissions TYPE record<users>; -- the new member who triggered it
DEFINE FIELD membership ON referral_commissions TYPE option<record<memberships>>;
DEFINE FIELD level ON referral_commissions TYPE int DEFAULT 1;
DEFINE FIELD rate ON referral_commissions TYPE decimal DEFAULT 0;
DEFINE FIELD amount ON referral_commissions TYPE decimal DEFAULT 0;
DEFINE FIELD currency ON referral_commissions TYPE string DEFAULT 'USD';
DEFINE FIELD status ON referral_commissions TYPE string DEFAULT 'pending' ASSERT $value IN ['pending', 'approved', 'paid', 'clawed_back'];
DEFINE FIELD created_at ON referral_commissions TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON referral_commissions TYPE datetime VALUE time::now();
DEFINE INDEX referral_commissions_beneficiary ON referral_commissions FIELDS beneficiary;
DEFINE INDEX referral_commissions_status ON referral_commissions FIELDS status;
DEFINE INDEX referral_commissions_member ON referral_commissions FIELDS source_member;

-- ============================================================
-- Functions
-- ============================================================

-- Redeem an E-pin to activate a membership for the given user.
-- Validates the pin, marks it redeemed, and creates an active membership.
DEFINE FUNCTION fn::redeem_epin($code: string, $member: record<users>) {
  LET $pin_rows = SELECT * FROM epins WHERE code = $code LIMIT 1;
  IF array::len($pin_rows) = 0 { THROW 'E-pin not found'; };
  LET $pin = $pin_rows[0];
  IF $pin.status != 'unused' { THROW 'E-pin is not redeemable'; };

  LET $tier_rows = SELECT * FROM $pin.tier;
  LET $tier = $tier_rows[0];

  LET $membership = CREATE memberships CONTENT {
    member: $member,
    tier: $pin.tier,
    tenant_id: $pin.tenant_id,
    membershipNumber: string::concat('M-', rand::ulid()),
    status: 'active',
    activated_by_epin: $pin.id,
    starts_at: time::now(),
    expires_at: time::now() + duration::from::days(365)
  };

  UPDATE $pin.id MERGE {
    status: 'redeemed',
    redeemed_by: $member,
    redeemed_at: time::now()
  };

  -- Audit trail, consistent with the settlement functions.
  CREATE commerce_actions CONTENT {
    schema_context: 'https://schema.org',
    schema_type: 'OrderAction',
    agent: $member,
    object: $membership.id,
    instrument: $pin.id,
    actionStatus: 'https://schema.org/CompletedActionStatus',
    tenant_id: $pin.tenant_id,
    price: $tier.price,
    priceCurrency: $tier.priceCurrency,
    metadata: { flow: 'epin_redemption', epin: $pin.code, tier: $tier.name }
  };

  RETURN $membership;
};

-- Credit a referral commission to the direct sponsor of a new member, based on
-- the purchased tier's referral_rate. Returns NONE when there is no sponsor.
DEFINE FUNCTION fn::record_referral_commission($membership: record<memberships>) {
  LET $m_rows = SELECT * FROM $membership;
  IF array::len($m_rows) = 0 { THROW 'Membership not found'; };
  LET $m = $m_rows[0];

  LET $tier_rows = SELECT * FROM $m.tier;
  LET $tier = $tier_rows[0];

  -- Find the direct sponsor (depth 1) of the new member.
  LET $sponsor_rows = SELECT in AS sponsor FROM referred WHERE out = $m.member AND depth = 1 LIMIT 1;
  IF array::len($sponsor_rows) = 0 { RETURN NONE; };
  LET $sponsor = $sponsor_rows[0].sponsor;

  LET $amount = $tier.price * $tier.referral_rate;

  LET $commission = CREATE referral_commissions CONTENT {
    tenant_id: $m.tenant_id,
    beneficiary: $sponsor,
    source_member: $m.member,
    membership: $membership,
    level: 1,
    rate: $tier.referral_rate,
    amount: $amount,
    currency: $tier.priceCurrency,
    status: 'pending'
  };

  -- Audit trail, consistent with the settlement functions.
  CREATE commerce_actions CONTENT {
    schema_context: 'https://schema.org',
    schema_type: 'MoneyTransfer',
    agent: $sponsor,
    recipient: $sponsor,
    object: $commission.id,
    actionStatus: 'https://schema.org/CompletedActionStatus',
    tenant_id: $m.tenant_id,
    amount: $amount,
    currency: $tier.priceCurrency,
    metadata: { flow: 'referral_commission', source_member: $m.member, membership: $membership }
  };

  RETURN $commission;
};

-- Batch a referrer's pending referral commissions into the shared payout
-- pipeline (payout_batches / payout_items). The resulting batch is settled by
-- the existing fn::mark_payout_paid, which marks each linked entry 'paid'.
DEFINE FUNCTION fn::create_referral_payout_batch($beneficiary: record<users>, $currency: string) {
  IF $auth.role != 'admin' { THROW 'Admin role required'; };

  LET $entries = SELECT * FROM referral_commissions WHERE beneficiary = $beneficiary AND currency = $currency AND status = 'pending';
  LET $total = math::sum($entries.amount);

  LET $batch = CREATE payout_batches CONTENT {
    tenant_id: $auth.tenant_id,
    beneficiary: $beneficiary,
    beneficiary_kind: 'user',
    currency: $currency,
    total_amount: $total,
    status: 'created'
  };

  FOR $entry IN $entries {
    CREATE payout_items CONTENT {
      batch: $batch.id,
      ledger_entry: $entry.id,
      amount: $entry.amount,
      currency: $entry.currency
    };
    UPDATE $entry.id MERGE { status: 'approved' };
  };

  RETURN $batch;
};

-- ============================================================
-- Row-level permissions
-- ============================================================

DEFINE TABLE identity_profiles PERMISSIONS
  FOR select WHERE is_public = true OR owner = $auth.id OR $auth.role = 'admin' OR tenant_id = $auth.tenant_id,
  FOR create WHERE $auth.id != NONE,
  FOR update WHERE owner = $auth.id OR $auth.role = 'admin',
  FOR delete WHERE $auth.role = 'admin';

DEFINE TABLE profile_views PERMISSIONS
  FOR select WHERE $auth.role = 'admin' OR tenant_id = $auth.tenant_id,
  FOR create WHERE true,
  FOR update, delete WHERE false;

DEFINE TABLE membership_programs PERMISSIONS
  FOR select WHERE is_active = true OR $auth.role = 'admin' OR tenant_id = $auth.tenant_id,
  FOR create, update, delete WHERE $auth.role = 'admin';

DEFINE TABLE membership_tiers PERMISSIONS
  FOR select WHERE is_active = true OR $auth.role = 'admin' OR tenant_id = $auth.tenant_id,
  FOR create, update, delete WHERE $auth.role = 'admin';

DEFINE TABLE memberships PERMISSIONS
  FOR select WHERE member = $auth.id OR $auth.role = 'admin' OR tenant_id = $auth.tenant_id,
  FOR create WHERE $auth.id != NONE,
  FOR update WHERE $auth.role = 'admin',
  FOR delete WHERE $auth.role = 'admin';

DEFINE TABLE epins PERMISSIONS
  FOR select WHERE issued_to = $auth.id OR redeemed_by = $auth.id OR $auth.role = 'admin' OR tenant_id = $auth.tenant_id,
  FOR create WHERE $auth.role = 'admin',
  FOR update WHERE $auth.role = 'admin',
  FOR delete WHERE false;

DEFINE TABLE referral_commissions PERMISSIONS
  FOR select WHERE beneficiary = $auth.id OR $auth.role = 'admin' OR tenant_id = $auth.tenant_id,
  FOR create WHERE $auth.id != NONE,
  FOR update WHERE $auth.role = 'admin',
  FOR delete WHERE false;
