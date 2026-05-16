# API Reference

## Products

### Create Product

```
POST /api/store/products
```

```json
{
    "title": "Product Name",
    "price": 29.99,
    "description": "Description",
    "sku": "SKU123",
    "inventory": 100
}
```

### List Products

```
GET /api/store/products
```

### Get Product

```
GET /api/store/products/{product_id}
```

## Orders

### Create Order

```
POST /api/store/orders
```

### Get Dashboard

```
GET /api/store/dashboard
```

## Payments

### Create Payment

```
POST /api/payments/{provider}
```

Providers: `ap2`, `x402`, `stripe`, `paypal`, `mastercard`, `openbanking`, `mpp`, `shopify`

### List Providers

```
GET /api/providers
```

## Admin

### Get Users

```
GET /api/admin/users
```

### Get Roles

```
GET /api/admin/roles
```

### Create API Key

```
POST /api/admin/api-keys
```