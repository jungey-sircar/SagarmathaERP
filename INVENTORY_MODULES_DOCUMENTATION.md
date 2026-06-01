# Inventory Management Modules - Implementation Guide

## Overview
Created comprehensive inventory management system with three main inventory module categories:
- **Items** (General Items)
- **Consumable Items** 
- **Fixed Items** (Fixed Assets)

## Models Created

### 1. InventoryItem (Enhanced)
**Location:** `main_app/models.py` (lines 450-472)

Enhanced base inventory model with new fields:
- `item_type`: Choice field (consumable, fixed, general)
- `created_at`: Timestamp when item was created
- `name`: Item name (max 160 chars)
- `category`: Item category (max 80 chars)
- `quantity`: Positive integer for item count
- `unit`: Unit of measurement (default: "pcs")
- `location`: Where item is stored
- `reorder_level`: Low stock threshold

**Methods:**
- `is_low_stock`: Property that checks if quantity <= reorder_level

### 2. ConsumableItem (New)
**Location:** `main_app/models.py` (lines 475-500)

For items that are used up and need replenishment:
- `name`: Item name
- `category`: Item category
- `quantity`: Current stock quantity
- `unit`: Unit of measurement
- `location`: Storage location
- `reorder_level`: Low stock threshold
- `supplier_name`: Supplier information
- `cost_per_unit`: Price per unit (Decimal)
- `last_updated`: Auto-timestamp
- `created_at`: Creation timestamp

**Methods:**
- `is_low_stock`: Check if needs reordering
- `total_cost`: Property calculating total cost (quantity × cost_per_unit)

### 3. FixedItem (New)
**Location:** `main_app/models.py` (lines 503-549)

For long-term fixed assets:
- `name`: Asset name
- `category`: Asset category
- `quantity`: Number of items (default: 1)
- `location`: Physical location
- `serial_number`: Unique identifier (unique=True)
- `purchase_date`: When purchased
- `purchase_cost`: Original cost
- `depreciation_rate`: Annual depreciation percentage
- `condition`: Current condition (choices: new, good, fair, poor, damaged)
- `warranty_expiry`: Warranty end date
- `last_maintenance_date`: Last maintenance date
- `next_maintenance_date`: Scheduled maintenance date
- `remarks`: Additional notes

**Methods:**
- `current_value`: Property calculating current value after depreciation

## Database Migration

**File:** `main_app/migrations/0019_inventory_modules.py`

Creates:
- New `ConsumableItem` table
- New `FixedItem` table
- Modifies `InventoryItem` table with new fields

**To apply migration:**
```bash
python manage.py migrate
```

## API Endpoints

### ViewSets (RESTful CRUD operations)

| Endpoint | Methods | Model | Permissions |
|----------|---------|-------|------------|
| `/api/inventory-items/` | GET, POST, PUT, DELETE | InventoryItem | IsAuthenticated |
| `/api/consumable-items/` | GET, POST, PUT, DELETE | ConsumableItem | IsAuthenticated |
| `/api/fixed-items/` | GET, POST, PUT, DELETE | FixedItem | IsAuthenticated |

### Special Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/inventory/dashboard/` | GET | Inventory dashboard statistics |

### Dashboard API Response
```json
{
    "page_title": "Inventory Dashboard",
    "inventory_stats": {
        "total_items_count": 2789,
        "total_items_qty": 5000,
        "low_stock_count": 45,
        "healthy_stock_count": 2744
    },
    "consumable_stats": {
        "total_count": 1638,
        "total_qty": 3500,
        "total_cost": 125000.50,
        "low_stock_count": 23
    },
    "fixed_stats": {
        "total_count": 1151,
        "total_qty": 1500,
        "total_value": 850000.75
    },
    "low_stock_items": [
        {
            "id": 1,
            "name": "Stationery",
            "category": "Office Supplies",
            "quantity": 2,
            "reorder_level": 10
        }
    ]
}
```

## Serializers

**Location:** `main_app/api/serializers.py`

### InventoryItemSerializer
- Serializes all InventoryItem fields
- Includes calculated properties

### ConsumableItemSerializer
- Serializes all ConsumableItem fields
- Includes `total_cost` as serialized method field

### FixedItemSerializer
- Serializes all FixedItem fields
- Includes `current_value` as serialized method field

## Views and Templates

### Main Inventory View
**Location:** `main_app/module_views.py` (lines 656-770)
**URL:** `/modules/inventory/`

**Features:**
- Display three summary cards (Items, Consumable Items, Fixed Items)
- Tabbed interface for managing each inventory type
- Add/Edit/Delete functionality for each item type
- Low stock alerts
- Total cost/value calculations

**Template:** `main_app/templates/modules/inventory.html`

**Context Variables:**
```python
{
    "page_title": "Inventory Management",
    "all_items": QuerySet,
    "consumable_items": QuerySet,
    "fixed_items": QuerySet,
    "total_items_count": int,
    "total_items_qty": int,
    "total_consumable_count": int,
    "total_consumable_qty": int,
    "total_fixed_count": int,
    "total_fixed_qty": int,
    "total_consumable_cost": Decimal,
    "total_fixed_value": Decimal,
    "low_stock_inventory_count": int,
    "low_stock_consumable_count": int,
    "healthy_stock_count": int,
    "low_stock_items": list,
    "low_stock_consumable": list,
}
```

## UI/Template Structure

### Dashboard Cards (Row 1)
```
┌─────────────────────┐  ┌──────────────────────┐  ┌────────────────────┐
│     ITEMS           │  │  CONSUMABLE ITEMS    │  │   FIXED ITEMS      │
│     2789            │  │      1638            │  │      1151          │
│   Total Qty: 5000   │  │  Total Qty: 3500     │  │  Total Qty: 1500   │
│                     │  │  Total Cost: ₨...    │  │  Total Value: ₨... │
│  View Items ►       │  │  View Consumables ►  │  │  View Fixed ►      │
└─────────────────────┘  └──────────────────────┘  └────────────────────┘
```

### Tabs Navigation
```
┌─ General Items ─|─ Consumable Items ─|─ Fixed Items ─┐
```

### Each Tab Contains:
1. **Add Form** - Fields specific to item type
2. **Data Table** - Tabular view of items with actions

## Usage Examples

### Adding a General Item via Form
```
Name: Umbrella
Category: General Items
Quantity: 50
Unit: pcs
Location: Store A
Reorder Level: 10
```

### Adding a Consumable Item via Form
```
Name: Office Paper A4
Category: Stationery
Quantity: 500
Unit: Reams
Supplier: Local Supplier
Cost/Unit: ₨500
Location: Store B
Reorder Level: 100
```

### Adding a Fixed Item via Form
```
Name: Dell Monitor
Category: Computer Equipment
Quantity: 1
Serial Number: DELL-2024-001
Cost: ₨15000
Condition: New
Location: Lab A
```

## API Usage Examples

### Fetch All Items
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/inventory-items/
```

### Create Consumable Item
```bash
curl -X POST -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pen",
    "category": "Stationery",
    "quantity": 100,
    "unit": "pieces",
    "cost_per_unit": 10
  }' \
  http://localhost:8000/api/consumable-items/
```

### Get Dashboard Statistics
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/inventory/dashboard/
```

## Files Modified

1. **models.py**
   - Added `item_type` field to InventoryItem
   - Added `created_at` field to InventoryItem
   - Created ConsumableItem model
   - Created FixedItem model

2. **api/serializers.py**
   - Added imports for new models
   - Created InventoryItemSerializer
   - Created ConsumableItemSerializer
   - Created FixedItemSerializer

3. **api/viewsets.py**
   - Added imports
   - Created InventoryItemViewSet
   - Created ConsumableItemViewSet
   - Created FixedItemViewSet

4. **api/urls.py**
   - Registered new viewsets
   - Added InventoryDashboardAPIView endpoint

5. **api/views.py**
   - Added imports
   - Created InventoryDashboardAPIView class

6. **module_views.py**
   - Added imports for new models
   - Enhanced inventory() view function
   - Added support for item_type parameter
   - Calculated statistics for each item type

7. **templates/modules/inventory.html**
   - Complete redesign with cards
   - Added tab navigation
   - Created separate forms for each item type
   - Enhanced tables with item-specific columns

8. **migrations/0019_inventory_modules.py**
   - Created migration file for new models

## Business Logic Features

### Low Stock Management
- Automatic low stock alerts
- Items marked with "Low Stock" badge when `quantity <= reorder_level`
- Summary count of low stock items

### Cost Tracking (Consumable Items)
- Track cost per unit
- Calculate total cost automatically
- Supplier tracking

### Asset Depreciation (Fixed Items)
- Calculate current value based on depreciation rate
- Track maintenance dates
- Condition tracking (New, Good, Fair, Poor, Damaged)
- Warranty expiry dates
- Serial number tracking

### Statistics Dashboard
- Total items, quantities, and counts
- Category-wise breakdown
- Low stock item identification
- Total inventory value calculations

## Security & Permissions

All API endpoints require:
- User authentication (IsAuthenticated)
- CSRF token for form submissions
- Django user privileges

## Future Enhancement Possibilities

1. Inventory audit trails (track changes)
2. Barcode/QR code integration
3. Automated reorder alerts via email/SMS
4. Inventory transfer between locations
5. Stock-in/Stock-out history
6. Advanced reporting and analytics
7. Multi-warehouse support
8. Integration with purchase orders
9. Export to Excel/PDF reports
10. Batch operations

## Testing

To test the inventory module:

1. Migrate database
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. Create test data:
   ```bash
   python manage.py shell
   # Then create items via models
   ```

3. Access via URL:
   ```
   http://localhost:8000/modules/inventory/
   ```

4. Test API:
   ```bash
   curl http://localhost:8000/api/inventory-items/
   ```

## Summary

The inventory management system is now fully functional with:
✅ Three categorized inventory types
✅ RESTful API endpoints
✅ Dashboard statistics
✅ Web interface with tabs
✅ Low stock tracking
✅ Cost/Value calculations
✅ Depreciation tracking for fixed assets
✅ Complete CRUD operations

