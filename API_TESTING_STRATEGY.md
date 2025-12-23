# Chiến Lược Test API - E-Commerce Backend

## 🎯 Tổng Quan

Tài liệu này mô tả chiến lược test toàn diện cho các API endpoints của dự án E-Commerce, bao gồm Categories, Products, Variants, Ingredients, Tags, Cart và Orders.

---

## 📋 Mục Lục

1. [Setup & Prerequisites](#setup--prerequisites)
2. [Test Order (Bottom-up)](#test-order-bottom-up)
3. [Integration & Complex Flows](#integration--complex-flows)
4. [Edge Cases & Validation](#edge-cases--validation)
5. [Postman Collection Structure](#postman-collection-structure)
6. [Automated Testing](#automated-testing-optional)
7. [Checklist](#checklist-test-hoàn-chỉnh)

---

## Setup & Prerequisites

### 1. Tools Cần Thiết

- **Postman** hoặc **Thunder Client** (VSCode extension) - Manual testing
- **pytest + httpx** - Automated testing (tuỳ chọn)
- **DB Tool** (pgAdmin/DBeaver) - Verify data changes

### 2. Prepare Test Environment

```bash
# Đảm bảo server đang chạy
cd be/api
uvicorn app.main:app --reload

# Kiểm tra server
curl http://127.0.0.1:8000/docs
```

### 3. Tạm Thời Bypass Authentication

Để test nhanh, comment out `Depends(get_current_user)` trong các routes cần authentication:

```python
# Trong routes cần test
# current_user: User = Depends(get_current_user)  # Comment này
```

---

## Test Order (Bottom-up)

### Level 1: Standalone Entities (không phụ thuộc)

#### A. Categories - `/catalog/categories`

**1. Create Root Category**
```http
POST /catalog/categories
Content-Type: application/json

{
  "name": "Electronics",
  "description": "Electronic products"
}

Expected: 201 Created
Response: { "id": 1, "name": "Electronics", ... }
```

**2. Create Child Category**
```http
POST /catalog/categories
Content-Type: application/json

{
  "name": "Laptops",
  "description": "Laptop computers",
  "parent_id": 1
}

Expected: 201 Created
```

**3. List Categories**
```http
GET /catalog/categories?skip=0&limit=10

Expected: 200 OK
Response: [{ "id": 1, "name": "Electronics", ... }, ...]
```

**4. Get Category by ID**
```http
GET /catalog/categories/1

Expected: 200 OK
Response: { "id": 1, "name": "Electronics", ... }
```

**5. Update Category**
```http
PUT /catalog/categories/1
Content-Type: application/json

{
  "description": "Updated description"
}

Expected: 200 OK
```

**6. Delete Category**
```http
DELETE /catalog/categories/1

Expected: 204 No Content
```

**Edge Cases:**
- ❌ POST duplicate name → `400 Bad Request`
- ❌ GET non-existent id → `404 Not Found`
- ❌ PUT with conflicting name → `400 Bad Request`
- ❌ Limit > 100 → `400 Bad Request`

---

#### B. Tags - `/catalog/tags`

**1. Create Tag**
```http
POST /catalog/tags
Content-Type: application/json

{
  "name": "Best Seller"
}

Expected: 201 Created
```

**2. Create Multiple Tags**
```http
POST /catalog/tags for each:
- "New Arrival"
- "Sale"
- "Featured"
```

**3. List Tags**
```http
GET /catalog/tags?skip=0&limit=100

Expected: 200 OK
```

**4. Get Tag by ID**
```http
GET /catalog/tags/1

Expected: 200 OK
```

**5. Delete Tag**
```http
DELETE /catalog/tags/1

Expected: 204 No Content
```

**Edge Cases:**
- ❌ Duplicate tag name → `400 Bad Request`

---

#### C. Ingredients - `/catalog/ingredients`

**1. Create Ingredient**
```http
POST /catalog/ingredients
Content-Type: application/json

{
  "name": "Aluminum",
  "unit": "kg",
  "price_per_unit": 50.0,
  "calories_per_unit": 0,
  "stock_quantity": 1000
}

Expected: 201 Created
```

**2. Create More Ingredients**
```http
POST for each:
- Plastic (unit: kg, price: 30.0)
- Steel (unit: kg, price: 80.0)
- Copper (unit: kg, price: 120.0)
```

**3. List Ingredients**
```http
GET /catalog/ingredients?skip=0&limit=100

Expected: 200 OK
```

**4. Update Ingredient Stock**
```http
PATCH /catalog/ingredients/1/stock?quantity=500

Expected: 200 OK
Response: { "message": "...", "stock_quantity": 500 }
```

**5. Delete Ingredient**
```http
DELETE /catalog/ingredients/1

Expected: 204 No Content
```

**Edge Cases:**
- ❌ Negative stock → `400 Bad Request` (nếu có validation)

---

### Level 2: Dependent Entities

#### D. Products - `/catalog/products`

**Prerequisite:** Cần có `category_id` từ Level 1

**1. Create Product**
```http
POST /catalog/products
Content-Type: application/json

{
  "name": "MacBook Pro 16",
  "description": "High-performance laptop for professionals",
  "price": 2499.99,
  "stock": 50,
  "image_url": "https://example.com/mbp16.jpg",
  "is_active": true,
  "category_id": 1,
  "tags": [1, 2],
  "ingredients": [
    {
      "ingredient_id": 1,
      "min_percentage": 10,
      "max_percentage": 20
    }
  ]
}

Expected: 201 Created
Response: Product with all relations loaded
```

**2. List Products with Filters**
```http
# By category
GET /catalog/products?category_id=1

# Search
GET /catalog/products?search=macbook

# Active only
GET /catalog/products?is_active=true

# Combined
GET /catalog/products?category_id=1&search=pro&is_active=true&skip=0&limit=10

Expected: 200 OK
```

**3. Get Product by ID**
```http
GET /catalog/products/1

Expected: 200 OK
Response: Full product with category, tags, ingredients, variants
```

**4. Update Product**
```http
PUT /catalog/products/1
Content-Type: application/json

{
  "price": 2399.99,
  "tags": [1, 3],
  "description": "Updated description"
}

Expected: 200 OK
```

**5. Update Product Stock**
```http
PATCH /catalog/products/1/stock?stock=45

Expected: 200 OK
Response: { "message": "Stock updated successfully", "stock": 45 }
```

**6. Soft Delete Product**
```http
DELETE /catalog/products/1?hard_delete=false

Expected: 204 No Content
Note: Product.is_active set to False
```

**7. Hard Delete Product**
```http
DELETE /catalog/products/1?hard_delete=true

Expected: 204 No Content
Note: Product permanently removed from DB
```

**Edge Cases:**
- ❌ Invalid `category_id` → `404 Not Found`
- ❌ Duplicate product name → `400 Bad Request`
- ❌ Negative price/stock → Validation error
- ❌ Non-existent `tag_ids` → Error (if checked)

---

#### E. Product Variants - `/catalog/products/{product_id}/variants`

**Prerequisite:** Cần có `product_id`

**1. Create Variant**
```http
POST /catalog/products/1/variants
Content-Type: application/json

{
  "name": "16GB RAM / 512GB SSD",
  "sku": "MBP16-16-512",
  "price": 2499.99,
  "stock": 20
}

Expected: 201 Created
```

**2. Create Multiple Variants**
```http
POST for each:
- "32GB RAM / 1TB SSD" (SKU: MBP16-32-1TB)
- "16GB RAM / 1TB SSD" (SKU: MBP16-16-1TB)
```

**3. List Variants for Product**
```http
GET /catalog/products/1/variants

Expected: 200 OK
Response: Array of variants
```

**4. Update Variant Stock**
```http
PATCH /catalog/products/1/variants/1/stock?stock=15

Expected: 200 OK
```

**5. Delete Variant**
```http
DELETE /catalog/products/1/variants/1

Expected: 204 No Content
```

**Edge Cases:**
- ❌ Duplicate SKU → `400 Bad Request`
- ❌ Invalid `product_id` → `404 Not Found`
- ❌ `variant_id` doesn't belong to `product_id` → `404 Not Found`

---

### Level 3: User-dependent Entities

#### F. Cart - `/cart`

**Note:** Tạm comment out authentication dependency

**1. Get Current User Cart**
```http
GET /cart

Expected: 200 OK
Response: Cart object (auto-created if not exists)
```

**2. Add Item to Cart**
```http
POST /cart/items
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 2
}

Expected: 201 Created
```

**3. Get Cart with Items**
```http
GET /cart

Expected: 200 OK
Response: { "id": 1, "items": [...], ... }
```

**4. Update Cart Item Quantity**
```http
PUT /cart/items/1
Content-Type: application/json

{
  "quantity": 3
}

Expected: 200 OK
```

**5. Remove Item from Cart**
```http
DELETE /cart/items/1

Expected: 204 No Content
```

**Edge Cases:**
- ❌ Add product with insufficient stock
- ❌ Quantity > available stock
- ❌ Invalid `product_id`

---

#### G. Orders - `/order`

**1. Create Order from Cart**
```http
POST /order
Content-Type: application/json

{
  "shipping_address_id": 1,
  "payment_method": "credit_card"
}

Expected: 201 Created
Response: Order object with items
```

**2. List User Orders**
```http
GET /order

Expected: 200 OK
Response: Array of orders
```

**3. Get Order Details**
```http
GET /order/1

Expected: 200 OK
Response: Full order with items, payment, shipment
```

**4. Update Order Status**
```http
PATCH /order/1/status
Content-Type: application/json

{
  "status": "shipped"
}

Expected: 200 OK
```

**Edge Cases:**
- ❌ Empty cart → Error
- ❌ Product out of stock during checkout
- ❌ Invalid address/payment method

---

## Integration & Complex Flows

### Scenario 1: Complete Product Setup

**Steps:**
1. ✅ Create category "Laptops"
2. ✅ Create tags ["New", "Sale", "Featured"]
3. ✅ Create ingredients ["Aluminum", "Plastic"]
4. ✅ Create product with category, tags, ingredients
5. ✅ Create 3 variants for product
6. ✅ Verify all relations loaded correctly in GET product

**Validation:**
- Product has correct category reference
- All tags appear in `product_tags`
- All ingredients linked in `product_ingredients`
- All variants reference correct `product_id`

---

### Scenario 2: Complete Shopping Flow

**Steps:**
1. ✅ List products by category
2. ✅ Get product details (with variants)
3. ✅ Add main product to cart (quantity=2)
4. ✅ Add variant to cart (quantity=1)
5. ✅ Update cart item quantity (from 2 to 3)
6. ✅ Create order from cart
7. ✅ Verify order created with correct items
8. ✅ Verify product stock decreased

**Validation:**
- Initial stock: 50
- After adding to cart: stock unchanged
- After creating order: stock = 50 - 3 = 47
- Cart cleared after order creation

---

### Scenario 3: Data Consistency Check

**Steps:**
1. ✅ Create product with `stock=10`
2. ✅ Add to cart `quantity=5`
3. ✅ Create order → stock becomes 5
4. ✅ Try add to cart `quantity=10` → should fail (insufficient stock)
5. ✅ Verify product stock still = 5

**Validation:**
- Stock never goes negative
- Cart validation checks available stock
- Order creation is atomic (all-or-nothing)

---

### Scenario 4: Cascade Operations

**Steps:**
1. ✅ Create product with 3 variants
2. ✅ Soft delete product (`is_active=False`)
3. ✅ Verify variants still accessible
4. ✅ Hard delete product
5. ✅ Verify variants are cascade deleted
6. ✅ Verify product no longer in any lists

**Validation:**
- Soft delete: `Product.is_active = False`, variants intact
- Hard delete: Product + Variants removed (cascade)
- Foreign key constraints working correctly

---

## Edge Cases & Validation

### 1. Pagination Limits
```http
# Should fail
GET /catalog/products?skip=0&limit=1000
Expected: 400 Bad Request (limit > 100)

GET /catalog/products?skip=-1&limit=10
Expected: 422 Unprocessable Entity
```

### 2. Invalid IDs
```http
GET /catalog/products/99999
Expected: 404 Not Found

GET /catalog/products/abc
Expected: 422 Unprocessable Entity
```

### 3. Required Fields
```http
POST /catalog/categories
Content-Type: application/json
{}

Expected: 422 Unprocessable Entity
```

### 4. Unique Constraints
```http
# Create duplicate category name
POST /catalog/categories
{ "name": "Electronics", "description": "..." }

Expected: 400 Bad Request
Detail: "Category with name 'Electronics' already exists"
```

### 5. Foreign Key Constraints
```http
# Invalid category_id
POST /catalog/products
{ "category_id": 9999, ... }

Expected: 404 Not Found
Detail: "Category with id 9999 not found"
```

### 6. Business Logic
- ❌ Add out-of-stock product to cart → Error
- ❌ Apply expired discount code → Invalid
- ❌ Create order with insufficient stock → Rollback

---

## Postman Collection Structure

```
E-Commerce API Tests/
│
├── 1. Categories/
│   ├── 1.1 Create Root Category
│   ├── 1.2 Create Child Category
│   ├── 1.3 List Categories
│   ├── 1.4 Get Category by ID
│   ├── 1.5 Update Category
│   ├── 1.6 Delete Category
│   └── 1.7 Edge Cases
│
├── 2. Tags/
│   ├── 2.1 Create Tag
│   ├── 2.2 List Tags
│   ├── 2.3 Get Tag by ID
│   ├── 2.4 Delete Tag
│   └── 2.5 Edge Cases
│
├── 3. Ingredients/
│   ├── 3.1 Create Ingredient
│   ├── 3.2 List Ingredients
│   ├── 3.3 Update Stock
│   ├── 3.4 Delete Ingredient
│   └── 3.5 Edge Cases
│
├── 4. Products/
│   ├── 4.1 Create Product
│   ├── 4.2 List Products
│   ├── 4.3 Search Products
│   ├── 4.4 Get Product Details
│   ├── 4.5 Update Product
│   ├── 4.6 Update Stock
│   ├── 4.7 Soft Delete
│   ├── 4.8 Hard Delete
│   └── 4.9 Edge Cases
│
├── 5. Product Variants/
│   ├── 5.1 Create Variant
│   ├── 5.2 List Variants
│   ├── 5.3 Update Variant Stock
│   ├── 5.4 Delete Variant
│   └── 5.5 Edge Cases
│
├── 6. Cart/
│   ├── 6.1 Get Cart
│   ├── 6.2 Add Item
│   ├── 6.3 Update Item
│   ├── 6.4 Remove Item
│   └── 6.5 Edge Cases
│
├── 7. Orders/
│   ├── 7.1 Create Order
│   ├── 7.2 List Orders
│   ├── 7.3 Get Order Details
│   ├── 7.4 Update Order Status
│   └── 7.5 Edge Cases
│
└── 8. Integration Scenarios/
    ├── 8.1 Complete Product Setup
    ├── 8.2 Shopping Flow
    ├── 8.3 Data Consistency
    └── 8.4 Cascade Operations
```

### Environment Variables

```json
{
  "base_url": "http://127.0.0.1:8000",
  "category_id": "",
  "product_id": "",
  "variant_id": "",
  "tag_id": "",
  "ingredient_id": "",
  "cart_id": "",
  "cart_item_id": "",
  "order_id": ""
}
```

### Postman Test Scripts

**Auto-save IDs:**
```javascript
// Trong Tests tab của request
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
    const response = pm.response.json();
    pm.environment.set("product_id", response.id);
});
```

**Chain requests:**
```javascript
// Pre-request Script
const categoryId = pm.environment.get("category_id");
if (!categoryId) {
    throw new Error("category_id not set. Run 'Create Category' first.");
}
```

---

## Automated Testing (Optional)

### Setup pytest

```bash
pip install pytest pytest-asyncio httpx
```

### Test File: `tests/test_api.py`

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_category():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/catalog/categories", json={
            "name": "Test Category",
            "description": "Test description"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Category"
        assert "id" in data

@pytest.mark.asyncio
async def test_list_categories():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/catalog/categories")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_create_product_invalid_category():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/catalog/products", json={
            "name": "Test Product",
            "description": "Test",
            "price": 100,
            "stock": 10,
            "image_url": "https://test.com/img.jpg",
            "category_id": 9999
        })
        assert response.status_code == 404
```

### Run Tests

```bash
pytest tests/test_api.py -v
```

---

## Checklist Test Hoàn Chỉnh

### Functional Testing
- [ ] ✅ CRUD operations cho tất cả entities
- [ ] ✅ Pagination (skip, limit) hoạt động đúng
- [ ] ✅ Filtering (category, search, active status)
- [ ] ✅ Relationships eager loading
- [ ] ✅ Cascade delete operations
- [ ] ✅ Stock management logic

### Validation Testing
- [ ] ✅ Required fields validation
- [ ] ✅ Data type validation
- [ ] ✅ Unique constraints
- [ ] ✅ Foreign key constraints
- [ ] ✅ Business rules (stock, pricing)

### Error Handling
- [ ] ✅ 404 Not Found cho invalid IDs
- [ ] ✅ 400 Bad Request cho invalid data
- [ ] ✅ 422 Unprocessable Entity cho validation errors
- [ ] ✅ Proper error messages

### Integration Testing
- [ ] ✅ Complete product setup flow
- [ ] ✅ Shopping cart to order flow
- [ ] ✅ Stock consistency across operations
- [ ] ✅ Cascade delete behavior

### Performance
- [ ] ✅ Response time < 500ms for simple queries
- [ ] ✅ Pagination limits prevent overload
- [ ] ✅ N+1 query problem checked (use selectin loading)

---

## Tips Hiệu Quả

### 1. Test Data Management
```sql
-- Script để clean test data
DELETE FROM cart_items;
DELETE FROM carts;
DELETE FROM order_items;
DELETE FROM orders;
DELETE FROM product_ingredients;
DELETE FROM product_tags;
DELETE FROM product_variants;
DELETE FROM products;
DELETE FROM tags;
DELETE FROM ingredients;
DELETE FROM categories;
```

### 2. Visual Validation
- Sử dụng Swagger UI: `http://127.0.0.1:8000/docs`
- Kiểm tra DB trực tiếp với pgAdmin/DBeaver

### 3. Log Monitoring
```bash
# Terminal chạy uvicorn sẽ hiện request logs
INFO:     127.0.0.1:59036 - "POST /catalog/categories HTTP/1.1" 201 Created
```

### 4. Git Workflow
```bash
# Tạo branch test riêng
git checkout -b test/api-endpoints

# Commit các thay đổi (comment auth, etc.)
git commit -m "test: bypass auth for API testing"

# Sau test xong, discard changes hoặc revert
```

---

## Kết Luận

Chiến lược test này đảm bảo:
- ✅ Coverage đầy đủ cho tất cả endpoints
- ✅ Test theo thứ tự logic (bottom-up)
- ✅ Edge cases và error handling được kiểm tra
- ✅ Integration flows hoạt động end-to-end
- ✅ Dễ maintain và mở rộng

**Next Steps:**
1. Tạo Postman Collection theo structure trên
2. Chạy manual tests qua từng phase
3. Document bugs/issues tìm thấy
4. Implement automated tests (optional)
5. Re-enable authentication và test với real users

---

**Cuối cùng:** Sau khi test xong, đừng quên bật lại authentication và test lại một số flows quan trọng với JWT tokens!
