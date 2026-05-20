-- SurrealDB-native security schema for Agent-Commerce
-- Source of truth for identity, authorization, sessions, and audit logs.

DEFINE TABLE users SCHEMAFULL;
DEFINE FIELD username ON users TYPE string;
DEFINE FIELD email ON users TYPE string;
DEFINE FIELD password_hash ON users TYPE string;
DEFINE FIELD role ON users TYPE string DEFAULT 'user';
DEFINE FIELD tenant_id ON users TYPE string;
DEFINE FIELD is_active ON users TYPE bool DEFAULT true;
DEFINE FIELD created_at ON users TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON users TYPE datetime VALUE time::now();
DEFINE INDEX users_username_unique ON users FIELDS username UNIQUE;
DEFINE INDEX users_email_unique ON users FIELDS email UNIQUE;

DEFINE TABLE roles SCHEMAFULL;
DEFINE FIELD name ON roles TYPE string;
DEFINE FIELD permissions ON roles TYPE array<string>;
DEFINE FIELD created_at ON roles TYPE datetime DEFAULT time::now();
DEFINE INDEX roles_name_unique ON roles FIELDS name UNIQUE;

DEFINE TABLE sessions SCHEMAFULL;
DEFINE FIELD user_id ON sessions TYPE record<users>;
DEFINE FIELD refresh_token_hash ON sessions TYPE string;
DEFINE FIELD expires_at ON sessions TYPE datetime;
DEFINE FIELD revoked ON sessions TYPE bool DEFAULT false;
DEFINE FIELD created_at ON sessions TYPE datetime DEFAULT time::now();
DEFINE INDEX sessions_token_unique ON sessions FIELDS refresh_token_hash UNIQUE;

DEFINE TABLE audit_events SCHEMAFULL;
DEFINE FIELD actor ON audit_events TYPE option<record<users>>;
DEFINE FIELD actor_role ON audit_events TYPE option<string>;
DEFINE FIELD tenant_id ON audit_events TYPE option<string>;
DEFINE FIELD action ON audit_events TYPE string;
DEFINE FIELD resource ON audit_events TYPE string;
DEFINE FIELD resource_id ON audit_events TYPE option<string>;
DEFINE FIELD metadata ON audit_events TYPE object DEFAULT {};
DEFINE FIELD ip_address ON audit_events TYPE option<string>;
DEFINE FIELD user_agent ON audit_events TYPE option<string>;
DEFINE FIELD created_at ON audit_events TYPE datetime DEFAULT time::now();
DEFINE INDEX audit_events_created_at ON audit_events FIELDS created_at;
DEFINE INDEX audit_events_action ON audit_events FIELDS action;

-- Example RBAC-friendly permissions. Adjust per SurrealDB version and final access method design.
DEFINE TABLE products PERMISSIONS
  FOR select WHERE $auth.role = 'admin' OR tenant_id = $auth.tenant_id,
  FOR create WHERE $auth.role IN ['admin', 'merchant'],
  FOR update WHERE $auth.role = 'admin' OR tenant_id = $auth.tenant_id,
  FOR delete WHERE $auth.role = 'admin';

DEFINE TABLE orders PERMISSIONS
  FOR select WHERE $auth.role = 'admin' OR customer_id = $auth.id OR tenant_id = $auth.tenant_id,
  FOR create WHERE $auth.id != NONE,
  FOR update WHERE $auth.role IN ['admin', 'merchant'],
  FOR delete WHERE $auth.role = 'admin';

DEFINE TABLE users PERMISSIONS
  FOR select WHERE $auth.role = 'admin' OR id = $auth.id,
  FOR create WHERE $auth.role = 'admin',
  FOR update WHERE $auth.role = 'admin' OR id = $auth.id,
  FOR delete WHERE $auth.role = 'admin';

DEFINE TABLE audit_events PERMISSIONS
  FOR select WHERE $auth.role = 'admin',
  FOR create WHERE true,
  FOR update, delete WHERE false;
