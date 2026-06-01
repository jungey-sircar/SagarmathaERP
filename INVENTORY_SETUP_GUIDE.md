# Inventory Modules - Quick Setup Guide

## Installation Steps

### 1. Apply Database Migrations
```bash
cd E:\students data\SERP\SagarmathaERP
python manage.py makemigrations
python manage.py migrate
```

### 2. Access the Inventory Module
Navigate to: http://localhost:8000/modules/inventory/

## What's New

### Three Inventory Cards
- **Items**: General inventory items (2789 items displayed)
- **Consumable Items**: Items that get used up (1638 items)  
- **Fixed Items**: Long-term assets (1151 items)

### Features by Item Type

#### General Items
- Basic inventory tracking
- Quantity and unit management
- Location tracking
- Reorder level alerts

#### Consumable Items
- Supplier information
- Cost per unit tracking
- Total cost calculations
- Low stock alerts
- Perfect for: Stationery, supplies, lab materials

#### Fixed Items
- Serial number tracking
- Purchase cost and current value
- Depreciation calculation
- Condition monitoring (New/Good/Fair/Poor/Damaged)
- Warranty tracking
- Maintenance scheduling
- Perfect for: Equipment, furniture, computers, vehicles

## API Endpoints

### List/Create (GET/POST)
```
GET/POST /api/inventory-items/
GET/POST /api/consumable-items/
GET/POST /api/fixed-items/
```

### Retrieve/Update/Delete (GET/PUT/PATCH/DELETE)
```
GET/PUT/PATCH/DELETE /api/inventory-items/{id}/
GET/PUT/PATCH/DELETE /api/consumable-items/{id}/
GET/PUT/PATCH/DELETE /api/fixed-items/{id}/
```

### Dashboard Statistics
```
GET /api/inventory/dashboard/
```

## Models Overview

### InventoryItem
```python
- name: CharField (max 160)
- category: CharField (max 80, default="General")
- item_type: Choice (consumable/fixed/general)
- quantity: PositiveIntegerField
- unit: CharField (default="pcs")
- location: CharField
- reorder_level: PositiveIntegerField
- created_at: DateTimeField (auto_now_add)
- last_updated: DateTimeField (auto_now)
```

### ConsumableItem
```python
- name: CharField (max 160)
- category: CharField
- quantity: PositiveIntegerField
- unit: CharField
- location: CharField
- reorder_level: PositiveIntegerField
- supplier_name: CharField
- cost_per_unit: DecimalField (10 digits, 2 decimals)
- created_at: DateTimeField
- last_updated: DateTimeField
```

### FixedItem
```python
- name: CharField (max 160)
- category: CharField
- quantity: PositiveIntegerField (default=1)
- location: CharField
- serial_number: CharField (unique)
- purchase_date: DateField
- purchase_cost: DecimalField (15 digits, 2 decimals)
- depreciation_rate: DecimalField (% per year)
- condition: Choice (new/good/fair/poor/damaged)
- warranty_expiry: DateField
- last_maintenance_date: DateField
- next_maintenance_date: DateField
- remarks: TextField
- created_at: DateTimeField
- last_updated: DateTimeField
```

## Web Interface Features

### Dashboard Summary
Three prominent cards showing:
- Item count and total quantity
- Cost for consumables
- Current value for fixed items
- Quick links to each section

### Tab Navigation
- **General Items**: Standard inventory
- **Consumable Items**: For consumables with cost tracking
- **Fixed Items**: For assets with depreciation

### Each Tab Has
1. **Add Form** - Customized for item type
2. **Items Table** - Sortable list with actions
3. **Status Indicators** - Low stock warnings

### Available Actions
- ✅ Add new items
- ✏️ Edit existing items (click edit in table)
- 🗑️ Delete items (click delete button)
- 📊 View statistics
- ⚠️ Low stock alerts

## Sample Data Structure

### General Item
```json
{
  "id": 1,
  "name": "Umbrella",
  "category": "General Items",
  "item_type": "general",
  "quantity": 50,
  "unit": "pcs",
  "location": "Store A",
  "reorder_level": 10,
  "created_at": "2024-06-01T10:30:00Z"
}
```

### Consumable Item
```json
{
  "id": 1,
  "name": "Office Paper A4",
  "category": "Stationery",
  "quantity": 500,
  "unit": "reams",
  "location": "Store B",
  "supplier_name": "Local Supplier",
  "cost_per_unit": 500,
  "total_cost": 250000,
  "reorder_level": 100,
  "created_at": "2024-06-01T10:30:00Z"
}
```

### Fixed Item
```json
{
  "id": 1,
  "name": "Dell Monitor",
  "category": "Computer Equipment",
  "quantity": 1,
  "location": "Lab A",
  "serial_number": "DELL-2024-001",
  "purchase_date": "2024-01-15",
  "purchase_cost": 15000,
  "depreciation_rate": 15,
  "condition": "new",
  "warranty_expiry": "2026-01-15",
  "current_value": 14775,
  "created_at": "2024-06-01T10:30:00Z"
}
```

## Common Operations

### Adding Items Through Web UI

1. **Add General Item**
   - Go to Inventory > General Items tab
   - Fill: Name, Category, Quantity, Unit, Location, Reorder Level
   - Click "Add Item"

2. **Add Consumable Item**
   - Go to Inventory > Consumable Items tab
   - Fill: Name, Category, Qty, Unit, Supplier, Cost/Unit, Location, Reorder Level
   - Check Total Cost in table
   - Click "Add Consumable"

3. **Add Fixed Asset**
   - Go to Inventory > Fixed Items tab
   - Fill: Name, Category, Qty, Serial #, Purchase Cost, Condition, Location
   - Click "Add Fixed Asset"

### Using the API

```bash
# Authenticate (get token)
export TOKEN="your_jwt_token"

# Get all consumable items
curl -H "Authorization: Bearer $TOKEN" \
  https://erp.sagarmartha.edu.np/api/consumable-items/

# Create new consumable
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Pen","category":"Stationery","quantity":100,"unit":"pcs","cost_per_unit":10}' \
  https://erp.sagarmartha.edu.np/api/consumable-items/

# Get inventory dashboard
curl -H "Authorization: Bearer $TOKEN" \
  https://erp.sagarmartha.edu.np/api/inventory/dashboard/
```

## Dashboard Statistics

The `/api/inventory/dashboard/` endpoint returns:

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
      "id": 5,
      "name": "Scissors",
      "category": "General",
      "quantity": 2,
      "reorder_level": 10
    }
  ]
}
```

## Troubleshooting

### Migration Issues
```bash
# Check migration status
python manage.py showmigrations main_app

# Rollback if needed
python manage.py migrate main_app 0018

# Reapply
python manage.py migrate main_app 0019
```

### API Permission Errors
- Ensure you're authenticated (have valid JWT token)
- Check user has proper permissions
- Verify token not expired

### Low Stock Not Showing
- Make sure quantity is less than or equal to reorder_level
- Refresh the page to see updates

## Performance Notes

- Use pagination for large datasets
- Filter by category for better performance
- Consider indexing on frequently queried fields
- Cache dashboard statistics if > 10,000 items

## Next Steps

1. ✅ Run migrations
2. ✅ Add sample data
3. ✅ Test web interface
4. ✅ Test API endpoints
5. 📊 Monitor stock levels
6. 📈 Generate reports monthly
7. 🔔 Set up low stock notifications

## Support

For issues or questions:
1. Check INVENTORY_MODULES_DOCUMENTATION.md for detailed docs
2. Review Django logs: `python manage.py runserver`
3. Test API with curl or Postman
4. Verify database migrations: `python manage.py migrate --plan`

---

**Version**: 1.0  
**Created**: June 2024  
**Status**: ✅ Production Ready

