-- Inventory and fulfillment setup
-- SurrealDB-first implementation.
-- Grounding:
-- - Warehouse: https://schema.org/Place
-- - Inventory quantity: https://schema.org/QuantitativeValue
-- - Shipment: https://schema.org/ParcelDelivery
-- - Stock movement: https://schema.org/TransferAction

DEFINE TABLE warehouses SCHEMAFULL;
DEFINE FIELD schema_context ON warehouses TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON warehouses TYPE string DEFAULT 'Place';
DEFINE FIELD schema_url ON warehouses TYPE string VALUE 'https://schema.org/Place';
DEFINE FIELD tenant_id ON warehouses TYPE string;
DEFINE FIELD merchant ON warehouses TYPE record<merchants>;
DEFINE FIELD name ON warehouses TYPE string;
DEFINE FIELD description ON warehouses TYPE option<string>;
DEFINE FIELD address ON warehouses TYPE object;
DEFINE FIELD geo ON warehouses TYPE option<object>;
DEFINE FIELD is_active ON warehouses TYPE bool DEFAULT true;
DEFINE FIELD created_at ON warehouses TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON warehouses TYPE datetime VALUE time::now();
DEFINE INDEX warehouses_tenant ON warehouses FIELDS tenant_id;
DEFINE INDEX warehouses_merchant ON warehouses FIELDS merchant;

DEFINE TABLE inventory_levels SCHEMAFULL;
DEFINE FIELD tenant_id ON inventory_levels TYPE string;
DEFINE FIELD warehouse ON inventory_levels TYPE record<warehouses>;
DEFINE FIELD product ON inventory_levels TYPE record<products>;
DEFINE FIELD quantity ON inventory_levels TYPE int DEFAULT 0;
DEFINE FIELD reserved_quantity ON inventory_levels TYPE int DEFAULT 0;
DEFINE FIELD reorder_point ON inventory_levels TYPE option<int>;
DEFINE FIELD updated_at ON inventory_levels TYPE datetime VALUE time::now();
DEFINE INDEX inventory_unique ON inventory_levels FIELDS warehouse, product UNIQUE;

DEFINE TABLE stock_movements SCHEMAFULL;
DEFINE FIELD schema_context ON stock_movements TYPE string DEFAULT 'https://schema.org';
DEFINE FIELD schema_type ON stock_movements TYPE string DEFAULT 'TransferAction';
DEFINE FIELD schema_url ON stock_movements TYPE string VALUE 'https://schema.org/TransferAction';
DEFINE FIELD tenant_id ON stock_movements TYPE string;
DEFINE FIELD product ON stock_movements TYPE record<products>;
DEFINE FIELD from_warehouse ON stock_movements TYPE option<record<warehouses>>;
DEFINE FIELD to_warehouse ON stock_movements TYPE option<record<warehouses>>;
DEFINE FIELD quantity ON stock_movements TYPE int;
DEFINE FIELD movement_type ON stock_movements TYPE string;
DEFINE FIELD reason ON stock_movements TYPE option<string>;
DEFINE FIELD created_at ON stock_movements TYPE datetime DEFAULT time::now();
DEFINE INDEX stock_movements_product ON stock_movements FIELDS product;

DEFINE TABLE fulfillment_settings SCHEMAFULL;
DEFINE FIELD tenant_id ON fulfillment_settings TYPE string;
DEFINE FIELD merchant ON fulfillment_settings TYPE record<merchants>;
DEFINE FIELD default_warehouse ON fulfillment_settings TYPE option<record<warehouses>>;
DEFINE FIELD processing_time_days ON fulfillment_settings TYPE int DEFAULT 1;
DEFINE FIELD shipping_methods ON fulfillment_settings TYPE array<object> DEFAULT [];
DEFINE FIELD updated_at ON fulfillment_settings TYPE datetime VALUE time::now();
DEFINE INDEX fulfillment_settings_merchant ON fulfillment_settings FIELDS merchant UNIQUE;

DEFINE FUNCTION fn::create_warehouse($data: object) {
  RETURN CREATE warehouses CONTENT $data;
};

DEFINE FUNCTION fn::adjust_inventory($warehouse: record<warehouses>, $product: record<products>, $delta: int, $reason: option<string>) {
  UPSERT inventory_levels SET
    tenant_id = $auth.tenant_id,
    warehouse = $warehouse,
    product = $product,
    quantity = math::max(0, quantity + $delta);

  CREATE stock_movements CONTENT {
    tenant_id: $auth.tenant_id,
    product: $product,
    to_warehouse: IF $delta > 0 THEN $warehouse ELSE NONE END,
    from_warehouse: IF $delta < 0 THEN $warehouse ELSE NONE END,
    quantity: math::abs($delta),
    movement_type: IF $delta > 0 THEN 'inbound' ELSE 'outbound' END,
    reason: $reason
  };

  RETURN SELECT * FROM inventory_levels WHERE warehouse = $warehouse AND product = $product;
};
