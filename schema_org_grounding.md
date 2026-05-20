# Schema.org Grounding for Agent-Commerce

This file maps the SurrealDB commerce schema to exact Schema.org type URLs.

## Core commerce entity types

| SurrealDB table | Schema.org type | Canonical URL |
|---|---|---|
| `merchants` | `Organization` | https://schema.org/Organization |
| `merchants` | `OnlineBusiness` | https://schema.org/OnlineBusiness |
| `merchants` | `LocalBusiness` | https://schema.org/LocalBusiness |
| `users` | `Person` | https://schema.org/Person |
| `brands` | `Brand` | https://schema.org/Brand |
| `products` | `Product` | https://schema.org/Product |
| `products` | `ProductModel` | https://schema.org/ProductModel |
| `products` | `ProductGroup` | https://schema.org/ProductGroup |
| `products` | `IndividualProduct` | https://schema.org/IndividualProduct |
| `offers` | `Offer` | https://schema.org/Offer |
| `offers` | `Demand` | https://schema.org/Demand |
| `orders` | `Order` | https://schema.org/Order |
| `invoices` | `Invoice` | https://schema.org/Invoice |
| `payment_methods` | `PaymentMethod` | https://schema.org/PaymentMethod |
| `deliveries` | `ParcelDelivery` | https://schema.org/ParcelDelivery |
| `return_policies` | `MerchantReturnPolicy` | https://schema.org/MerchantReturnPolicy |
| `reviews` | `Review` | https://schema.org/Review |
| `reviews.reviewRating` | `Rating` | https://schema.org/Rating |
| aggregate product rating | `AggregateRating` | https://schema.org/AggregateRating |
| catalog lists | `ItemList` | https://schema.org/ItemList |
| catalog list items | `ListItem` | https://schema.org/ListItem |
| services / subscriptions | `Service` | https://schema.org/Service |

## Commerce action types

All of these are represented through the `commerce_actions` table using `schema_type`.

| `schema_type` | Schema.org URL | Recommended commerce use |
|---|---|---|
| `SearchAction` | https://schema.org/SearchAction | Search queries, semantic search, product discovery queries |
| `FindAction` | https://schema.org/FindAction | Finding products, offers, vendors, orders, or services |
| `CheckAction` | https://schema.org/CheckAction | Inventory checks, price checks, eligibility checks, delivery checks |
| `DiscoverAction` | https://schema.org/DiscoverAction | Exploratory product/vendor/category discovery |
| `TrackAction` | https://schema.org/TrackAction | Order, shipment, refund, dispute, or payment tracking |
| `BuyAction` | https://schema.org/BuyAction | Purchase intent or completed buying action |
| `OrderAction` | https://schema.org/OrderAction | Order placement flow |
| `PayAction` | https://schema.org/PayAction | Payment execution |
| `PreOrderAction` | https://schema.org/PreOrderAction | Preorder intent before product availability |
| `QuoteAction` | https://schema.org/QuoteAction | Quote request or quote issuance |
| `RentAction` | https://schema.org/RentAction | Rental / lease flow |
| `SellAction` | https://schema.org/SellAction | Merchant sale action |
| `TipAction` | https://schema.org/TipAction | Gratuity or tip flow |
| `BorrowAction` | https://schema.org/BorrowAction | Borrowing product/equipment |
| `DonateAction` | https://schema.org/DonateAction | Donation or charitable transfer |
| `DownloadAction` | https://schema.org/DownloadAction | Digital product/content fulfillment |
| `GiveAction` | https://schema.org/GiveAction | Gift, loyalty reward, or ownership transfer without payment |
| `LendAction` | https://schema.org/LendAction | Merchant/platform lends an item |
| `MoneyTransfer` | https://schema.org/MoneyTransfer | Payment movement, payout, refund, wallet, commission transfer |
| `ReceiveAction` | https://schema.org/ReceiveAction | Receipt of product, payment, refund, return, or transfer |
| `ReturnAction` | https://schema.org/ReturnAction | Product return, RMA, refund request, reverse logistics |
| `SendAction` | https://schema.org/SendAction | Shipment, notification, invoice send, digital delivery |
| `TakeAction` | https://schema.org/TakeAction | Pickup, collection, or taking possession |

## Action hierarchy grounding

| Parent type | URL |
|---|---|
| `Thing` | https://schema.org/Thing |
| `Action` | https://schema.org/Action |
| `FindAction` | https://schema.org/FindAction |
| `SearchAction` | https://schema.org/SearchAction |
| `TradeAction` | https://schema.org/TradeAction |
| `TransferAction` | https://schema.org/TransferAction |

## JSON-LD compatibility guidance

Each Schema.org-aligned record should preserve:

```json
{
  "@context": "https://schema.org",
  "@type": "Product"
}
```

In SurrealDB, use:

```surql
schema_context = 'https://schema.org';
schema_type = 'Product';
```

API serialization can transform these into JSON-LD keys:

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Example product"
}
```
