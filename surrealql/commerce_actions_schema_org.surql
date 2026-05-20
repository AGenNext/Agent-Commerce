-- Schema.org-aligned commerce action model for Agent-Commerce
-- This models customer/agent intent, workflows, transfers, fulfillment, payments,
-- and post-purchase behavior as first-class records.

DEFINE TABLE commerce_actions SCHEMAFULL;

-- JSON-LD / Schema.org compatibility
DEFINE FIELD schema_context ON commerce_actions TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON commerce_actions TYPE string ASSERT $value IN [
  'SearchAction',
  'FindAction',
  'CheckAction',
  'DiscoverAction',
  'TrackAction',
  'BuyAction',
  'OrderAction',
  'PayAction',
  'PreOrderAction',
  'QuoteAction',
  'RentAction',
  'SellAction',
  'TipAction',
  'BorrowAction',
  'DonateAction',
  'DownloadAction',
  'GiveAction',
  'LendAction',
  'MoneyTransfer',
  'ReceiveAction',
  'ReturnAction',
  'SendAction',
  'TakeAction'
];
DEFINE FIELD schema_url ON commerce_actions TYPE string VALUE string::concat('https://schema.org/', schema_type);
DEFINE FIELD schema_parent ON commerce_actions TYPE string VALUE IF schema_type IN ['BuyAction','OrderAction','PayAction','PreOrderAction','QuoteAction','RentAction','SellAction','TipAction'] THEN 'https://schema.org/TradeAction' ELSE IF schema_type IN ['BorrowAction','DonateAction','DownloadAction','GiveAction','LendAction','MoneyTransfer','ReceiveAction','ReturnAction','SendAction','TakeAction'] THEN 'https://schema.org/TransferAction' ELSE IF schema_type IN ['SearchAction','FindAction','CheckAction','DiscoverAction','TrackAction'] THEN 'https://schema.org/FindAction' ELSE 'https://schema.org/Action' END;

-- Schema.org Action fields
DEFINE FIELD agent ON commerce_actions TYPE option<record<users>>;
DEFINE FIELD participant ON commerce_actions TYPE option<array<record>>;
DEFINE FIELD recipient ON commerce_actions TYPE option<record>;
DEFINE FIELD object ON commerce_actions TYPE option<record>;
DEFINE FIELD target ON commerce_actions TYPE option<string>;
DEFINE FIELD instrument ON commerce_actions TYPE option<record>;
DEFINE FIELD result ON commerce_actions TYPE option<array<record>>;
DEFINE FIELD actionStatus ON commerce_actions TYPE string DEFAULT 'https://schema.org/PotentialActionStatus';
DEFINE FIELD startTime ON commerce_actions TYPE option<datetime>;
DEFINE FIELD endTime ON commerce_actions TYPE option<datetime>;

-- Commerce-specific fields
DEFINE FIELD tenant_id ON commerce_actions TYPE string;
DEFINE FIELD query ON commerce_actions TYPE option<string>;
DEFINE FIELD query_input ON commerce_actions TYPE option<object>;
DEFINE FIELD price ON commerce_actions TYPE option<decimal>;
DEFINE FIELD priceCurrency ON commerce_actions TYPE option<string>;
DEFINE FIELD amount ON commerce_actions TYPE option<decimal>;
DEFINE FIELD currency ON commerce_actions TYPE option<string>;
DEFINE FIELD fromLocation ON commerce_actions TYPE option<object>;
DEFINE FIELD toLocation ON commerce_actions TYPE option<object>;
DEFINE FIELD embedding ON commerce_actions TYPE option<array<float>>;
DEFINE FIELD metadata ON commerce_actions TYPE object DEFAULT {};
DEFINE FIELD created_at ON commerce_actions TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON commerce_actions TYPE datetime VALUE time::now();

-- Indexes for analytics, retrieval, attribution, and agent memory
DEFINE INDEX commerce_actions_type ON commerce_actions FIELDS schema_type;
DEFINE INDEX commerce_actions_schema_url ON commerce_actions FIELDS schema_url;
DEFINE INDEX commerce_actions_tenant ON commerce_actions FIELDS tenant_id;
DEFINE INDEX commerce_actions_agent ON commerce_actions FIELDS agent;
DEFINE INDEX commerce_actions_status ON commerce_actions FIELDS actionStatus;
DEFINE INDEX commerce_actions_created_at ON commerce_actions FIELDS created_at;
DEFINE INDEX commerce_actions_query_search ON commerce_actions FIELDS query SEARCH ANALYZER ascii BM25;

-- Relations for action graph / attribution
DEFINE TABLE performed_action TYPE RELATION IN users OUT commerce_actions SCHEMAFULL;
DEFINE FIELD tenant_id ON performed_action TYPE string;
DEFINE FIELD created_at ON performed_action TYPE datetime DEFAULT time::now();

DEFINE TABLE action_returned TYPE RELATION IN commerce_actions OUT record SCHEMAFULL;
DEFINE FIELD rank ON action_returned TYPE option<int>;
DEFINE FIELD score ON action_returned TYPE option<float>;
DEFINE FIELD created_at ON action_returned TYPE datetime DEFAULT time::now();

DEFINE TABLE action_led_to TYPE RELATION IN commerce_actions OUT commerce_actions SCHEMAFULL;
DEFINE FIELD reason ON action_led_to TYPE option<string>;
DEFINE FIELD created_at ON action_led_to TYPE datetime DEFAULT time::now();

DEFINE TABLE action_checked TYPE RELATION IN commerce_actions OUT record SCHEMAFULL;
DEFINE FIELD check_type ON action_checked TYPE option<string>;
DEFINE FIELD result_summary ON action_checked TYPE option<object>;
DEFINE FIELD created_at ON action_checked TYPE datetime DEFAULT time::now();

DEFINE TABLE action_transferred TYPE RELATION IN commerce_actions OUT record SCHEMAFULL;
DEFINE FIELD transfer_type ON action_transferred TYPE option<string>;
DEFINE FIELD quantity ON action_transferred TYPE option<decimal>;
DEFINE FIELD created_at ON action_transferred TYPE datetime DEFAULT time::now();

-- Permissions: users can see their own actions and tenant-scoped actions;
-- admins can see all tenant records. Writes require an authenticated actor.
DEFINE TABLE commerce_actions PERMISSIONS
  FOR select WHERE $auth.role = 'admin' OR tenant_id = $auth.tenant_id OR agent = $auth.id,
  FOR create WHERE $auth.id != NONE,
  FOR update WHERE $auth.role = 'admin' OR agent = $auth.id,
  FOR delete WHERE $auth.role = 'admin';

DEFINE TABLE performed_action PERMISSIONS
  FOR select WHERE $auth.role = 'admin' OR tenant_id = $auth.tenant_id,
  FOR create WHERE $auth.id != NONE,
  FOR update, delete WHERE $auth.role = 'admin';

DEFINE TABLE action_returned PERMISSIONS
  FOR select WHERE true,
  FOR create WHERE $auth.id != NONE,
  FOR update, delete WHERE $auth.role = 'admin';

DEFINE TABLE action_led_to PERMISSIONS
  FOR select WHERE true,
  FOR create WHERE $auth.id != NONE,
  FOR update, delete WHERE $auth.role = 'admin';

DEFINE TABLE action_checked PERMISSIONS
  FOR select WHERE true,
  FOR create WHERE $auth.id != NONE,
  FOR update, delete WHERE $auth.role = 'admin';

DEFINE TABLE action_transferred PERMISSIONS
  FOR select WHERE true,
  FOR create WHERE $auth.id != NONE,
  FOR update, delete WHERE $auth.role = 'admin';
