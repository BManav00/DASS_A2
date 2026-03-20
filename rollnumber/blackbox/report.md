# QuickCart Black-Box API Testing Report

- Base URL: `http://localhost:8000/api/v1`
- Tooling: `pytest`, `requests`
- Test command: `rollnumber/whitebox/.venv/bin/python -m pytest -q rollnumber/blackbox/tests`
- Latest run summary: `59 passed, 12 failed`

## Test Cases

### Test Case: test_admin_collection_endpoints_success
- Endpoint tested: `GET /api/v1/admin/carts`, `GET /api/v1/admin/orders`, `GET /api/v1/admin/products`, `GET /api/v1/admin/coupons`, `GET /api/v1/admin/tickets`, `GET /api/v1/admin/addresses`
- Input (method, URL, body): `GET`, each endpoint above, body: none
- Expected output: `200 OK` and JSON list with required entity keys
- Why this test is needed: Verifies admin inspection APIs return valid database snapshots for black-box validation.

### Test Case: test_admin_users_and_admin_user_by_id_success
- Endpoint tested: `GET /api/v1/admin/users`, `GET /api/v1/admin/users/{user_id}`
- Input (method, URL, body): `GET /admin/users`, then `GET /admin/users/<first_user_id>`
- Expected output: `200 OK`, list format, then correct single user object
- Why this test is needed: Ensures user inventory and user lookup work correctly.

### Test Case: test_products_list_success_and_only_active
- Endpoint tested: `GET /api/v1/products`
- Input (method, URL, body): `GET /products`, body: none
- Expected output: `200 OK`, list of products where all `is_active=true`
- Why this test is needed: Confirms inactive products are hidden from customer product listing.

### Test Case: test_product_lookup_by_id_success
- Endpoint tested: `GET /api/v1/products/{product_id}`
- Input (method, URL, body): `GET /products/<valid_id>`
- Expected output: `200 OK` with matching `product_id` and expected fields
- Why this test is needed: Validates product detail retrieval by ID.

### Test Case: test_products_filter_search_and_sort_success
- Endpoint tested: `GET /api/v1/products`
- Input (method, URL, body): `GET /products?category=...`, `GET /products?search=...`, `GET /products?sort=price_asc|price_desc`
- Expected output: Category filtering, name search behavior, ascending/descending sort correctness
- Why this test is needed: Ensures documented filter/search/sort behavior works for clients.

### Test Case: test_get_product_reviews_success
- Endpoint tested: `GET /api/v1/products/{product_id}/reviews`
- Input (method, URL, body): `GET /products/1/reviews`
- Expected output: `200 OK` with `average_rating` and `reviews` list
- Why this test is needed: Checks review listing structure for product detail screens.

### Test Case: test_get_and_update_profile_success
- Endpoint tested: `GET /api/v1/profile`, `PUT /api/v1/profile`
- Input (method, URL, body): `PUT /profile` with `{"name":"QA Smoke","phone":"9876543210"}`
- Expected output: `200 OK` and profile remains accessible after update
- Why this test is needed: Verifies user profile retrieval and update flow.

### Test Case: test_addresses_crud_smoke
- Endpoint tested: `GET /api/v1/addresses`, `POST /api/v1/addresses`, `PUT /api/v1/addresses/{address_id}`, `DELETE /api/v1/addresses/{address_id}`
- Input (method, URL, body): Create address payload, update payload, then delete created address
- Expected output: All operations return success (`200`) for valid inputs
- Why this test is needed: Validates end-to-end address management lifecycle.

### Test Case: test_wallet_endpoints_success
- Endpoint tested: `GET /api/v1/wallet`, `POST /api/v1/wallet/add`, `POST /api/v1/wallet/pay`
- Input (method, URL, body): Add `{"amount":1}`, pay `{"amount":1}`
- Expected output: Success responses and returned `wallet_balance`
- Why this test is needed: Confirms basic wallet operations are functional.

### Test Case: test_loyalty_endpoints_success
- Endpoint tested: `GET /api/v1/loyalty`, `POST /api/v1/loyalty/redeem`
- Input (method, URL, body): Redeem `{"points":1}`
- Expected output: `200 OK` and loyalty points decrease by one
- Why this test is needed: Ensures loyalty redemption flow works for valid values.

### Test Case: test_support_ticket_flow_success
- Endpoint tested: `POST /api/v1/support/ticket`, `GET /api/v1/support/tickets`, `PUT /api/v1/support/tickets/{ticket_id}`
- Input (method, URL, body): Create ticket, move status `OPEN -> IN_PROGRESS -> CLOSED`
- Expected output: Correct status transitions and ticket visibility in list
- Why this test is needed: Verifies support ticket lifecycle.

### Test Case: test_cart_add_update_remove_and_clear_success
- Endpoint tested: `GET /api/v1/cart`, `POST /api/v1/cart/add`, `POST /api/v1/cart/update`, `POST /api/v1/cart/remove`, `DELETE /api/v1/cart/clear`
- Input (method, URL, body): Add valid product, update quantity, remove item, clear cart
- Expected output: All valid operations return success
- Why this test is needed: Confirms core cart operations for shoppers.

### Test Case: test_coupon_apply_and_remove_success
- Endpoint tested: `POST /api/v1/coupon/apply`, `POST /api/v1/coupon/remove`
- Input (method, URL, body): Apply `WELCOME50` on non-empty cart, then remove coupon
- Expected output: Discount response includes `coupon_code`, `discount`, `new_total`; remove succeeds
- Why this test is needed: Validates coupon apply/remove user flow.

### Test Case: test_checkout_card_success
- Endpoint tested: `POST /api/v1/checkout`
- Input (method, URL, body): `{"payment_method":"CARD"}` with non-empty cart
- Expected output: `200 OK`, `payment_status=PAID`, `order_status=PLACED`
- Why this test is needed: Verifies card checkout path.

### Test Case: test_checkout_wallet_success
- Endpoint tested: `POST /api/v1/checkout`
- Input (method, URL, body): `{"payment_method":"WALLET"}` with non-empty cart
- Expected output: `200 OK`, `payment_status=PENDING`, `order_status=PLACED`
- Why this test is needed: Verifies wallet checkout status mapping.

### Test Case: test_orders_detail_invoice_and_cancel_success
- Endpoint tested: `GET /api/v1/orders`, `GET /api/v1/orders/{order_id}`, `GET /api/v1/orders/{order_id}/invoice`, `POST /api/v1/orders/{order_id}/cancel`
- Input (method, URL, body): Use fresh checkout order then query detail/invoice and cancel
- Expected output: Order appears in list, invoice math valid, cancel returns `CANCELLED`
- Why this test is needed: Validates post-checkout order lifecycle endpoints.

### Test Case: test_post_review_success
- Endpoint tested: `POST /api/v1/products/{product_id}/reviews`
- Input (method, URL, body): `{"rating":5,"comment":"Great item ..."}`
- Expected output: `200 OK` with created `review_id`
- Why this test is needed: Confirms valid review submission path.

### Test Case: test_missing_roll_header_returns_401
- Endpoint tested: `GET /api/v1/admin/users`
- Input (method, URL, body): No `X-Roll-Number` header
- Expected output: `401 Unauthorized`
- Why this test is needed: Verifies mandatory authorization header enforcement.

### Test Case: test_invalid_roll_header_returns_400
- Endpoint tested: `GET /api/v1/admin/users`
- Input (method, URL, body): Header `X-Roll-Number: abc`
- Expected output: `400 Bad Request`
- Why this test is needed: Validates type checking for roll-number header.

### Test Case: test_missing_user_header_returns_400
- Endpoint tested: `GET /api/v1/profile`
- Input (method, URL, body): Missing `X-User-ID`
- Expected output: `400 Bad Request`
- Why this test is needed: Ensures user-scoped endpoints reject missing user context.

### Test Case: test_invalid_user_header_returns_400
- Endpoint tested: `GET /api/v1/profile`
- Input (method, URL, body): `X-User-ID: invalid`
- Expected output: `400 Bad Request`
- Why this test is needed: Ensures invalid user header format is rejected.

### Test Case: test_non_existing_user_header_returns_400
- Endpoint tested: `GET /api/v1/profile`
- Input (method, URL, body): `X-User-ID: 999999`
- Expected output: `400 Bad Request`
- Why this test is needed: Verifies that user header must map to an existing user as documented.

### Test Case: test_admin_user_by_id_not_found_returns_404
- Endpoint tested: `GET /api/v1/admin/users/{user_id}`
- Input (method, URL, body): `GET /admin/users/999999`
- Expected output: `404 Not Found`
- Why this test is needed: Confirms missing-user handling for admin lookup.

### Test Case: test_profile_name_boundaries_accept_2_and_50_chars
- Endpoint tested: `PUT /api/v1/profile`
- Input (method, URL, body): Name lengths exactly `2` and `50`, valid phone
- Expected output: `200 OK` for both boundary-valid names
- Why this test is needed: Confirms documented inclusive boundaries for name length.

### Test Case: test_profile_name_too_short_rejected
- Endpoint tested: `PUT /api/v1/profile`
- Input (method, URL, body): `{"name":"A","phone":"9876543210"}`
- Expected output: `400 Bad Request`
- Why this test is needed: Ensures invalid short names are rejected.

### Test Case: test_profile_phone_invalid_and_missing_rejected
- Endpoint tested: `PUT /api/v1/profile`
- Input (method, URL, body): Phone too short and missing-phone payloads
- Expected output: `400 Bad Request` in both cases
- Why this test is needed: Verifies strict phone validation and required field behavior.

### Test Case: test_profile_wrong_phone_type_rejected
- Endpoint tested: `PUT /api/v1/profile`
- Input (method, URL, body): Numeric phone type instead of string
- Expected output: `400 Bad Request`
- Why this test is needed: Validates wrong data type handling.

### Test Case: test_address_create_invalid_label_rejected
- Endpoint tested: `POST /api/v1/addresses`
- Input (method, URL, body): `label=WORK`
- Expected output: `400 Bad Request`
- Why this test is needed: Ensures enum validation for address label.

### Test Case: test_address_missing_field_rejected
- Endpoint tested: `POST /api/v1/addresses`
- Input (method, URL, body): Missing `pincode`
- Expected output: `400 Bad Request`
- Why this test is needed: Verifies required field enforcement in address creation.

### Test Case: test_address_wrong_pincode_type_rejected
- Endpoint tested: `POST /api/v1/addresses`
- Input (method, URL, body): Numeric `pincode` type in raw JSON
- Expected output: `400 Bad Request`
- Why this test is needed: Checks wrong-type payload rejection.

### Test Case: test_address_boundary_values_accept_valid_limits
- Endpoint tested: `POST /api/v1/addresses`
- Input (method, URL, body): Street length 5 and 100, city length 2 and 50, valid pincode
- Expected output: `200 OK` for boundary-valid payloads
- Why this test is needed: Confirms inclusive boundaries for address fields.

### Test Case: test_address_update_must_return_and_persist_updated_data
- Endpoint tested: `PUT /api/v1/addresses/{address_id}`, `GET /api/v1/addresses`
- Input (method, URL, body): Update `street` and `is_default` on created address
- Expected output: Response should contain new values and persisted values should match
- Why this test is needed: Ensures updates are actually applied and reflected immediately.

### Test Case: test_address_delete_non_existing_returns_404
- Endpoint tested: `DELETE /api/v1/addresses/{address_id}`
- Input (method, URL, body): `DELETE /addresses/999999`
- Expected output: `404 Not Found`
- Why this test is needed: Validates missing-resource behavior.

### Test Case: test_product_not_found_returns_404
- Endpoint tested: `GET /api/v1/products/{product_id}`
- Input (method, URL, body): `GET /products/999999`
- Expected output: `404 Not Found`
- Why this test is needed: Confirms missing product handling.

### Test Case: test_product_prices_match_admin_source
- Endpoint tested: `GET /api/v1/products`, `GET /api/v1/admin/products`
- Input (method, URL, body): Compare first 25 active products against admin DB snapshot
- Expected output: Public product price equals database price for same `product_id`
- Why this test is needed: Enforces documentation requirement that shown price is exact DB price.

### Test Case: test_reviews_average_is_decimal_when_fractional
- Endpoint tested: `POST /api/v1/products/{product_id}/reviews`, `GET /api/v1/products/{product_id}/reviews`
- Input (method, URL, body): Add two ratings then fetch average
- Expected output: Average exists and supports decimal values
- Why this test is needed: Verifies average rating representation is suitable for fractional averages.

### Test Case: test_review_rating_below_range_rejected
- Endpoint tested: `POST /api/v1/products/{product_id}/reviews`
- Input (method, URL, body): `{"rating":0,"comment":"below range"}`
- Expected output: `400 Bad Request`
- Why this test is needed: Ensures lower boundary violation is rejected.

### Test Case: test_review_rating_above_range_rejected
- Endpoint tested: `POST /api/v1/products/{product_id}/reviews`
- Input (method, URL, body): `{"rating":6,"comment":"above range"}`
- Expected output: `400 Bad Request`
- Why this test is needed: Ensures upper boundary violation is rejected.

### Test Case: test_review_comment_boundaries
- Endpoint tested: `POST /api/v1/products/{product_id}/reviews`
- Input (method, URL, body): Comment lengths `1`, `200`, `0`, `201`
- Expected output: 1 and 200 accepted; 0 and 201 rejected with `400`
- Why this test is needed: Verifies exact boundary handling for review comments.

### Test Case: test_cart_add_zero_quantity_rejected
- Endpoint tested: `POST /api/v1/cart/add`
- Input (method, URL, body): `{"product_id":1,"quantity":0}`
- Expected output: `400 Bad Request`
- Why this test is needed: Quantity must be at least 1.

### Test Case: test_cart_add_negative_quantity_rejected
- Endpoint tested: `POST /api/v1/cart/add`
- Input (method, URL, body): `{"product_id":1,"quantity":-1}`
- Expected output: `400 Bad Request`
- Why this test is needed: Rejects invalid negative quantity.

### Test Case: test_cart_add_product_not_found_returns_404
- Endpoint tested: `POST /api/v1/cart/add`
- Input (method, URL, body): Non-existent `product_id`
- Expected output: `404 Not Found`
- Why this test is needed: Ensures invalid product IDs are rejected.

### Test Case: test_cart_add_insufficient_stock_returns_400
- Endpoint tested: `POST /api/v1/cart/add`
- Input (method, URL, body): Quantity greater than available stock
- Expected output: `400 Bad Request`
- Why this test is needed: Validates stock protection rules.

### Test Case: test_cart_add_same_product_accumulates_quantity
- Endpoint tested: `POST /api/v1/cart/add`, `GET /api/v1/cart`
- Input (method, URL, body): Add same product twice (`2` then `3`)
- Expected output: Cart quantity becomes `5`
- Why this test is needed: Confirms additive quantity behavior.

### Test Case: test_cart_subtotal_and_total_are_exact
- Endpoint tested: `GET /api/v1/cart` after `POST /api/v1/cart/add`
- Input (method, URL, body): Add product quantity `2` and verify math
- Expected output: `subtotal = quantity * unit_price`, `total = sum(subtotals)`
- Why this test is needed: Checks core billing correctness.

### Test Case: test_cart_update_zero_quantity_rejected
- Endpoint tested: `POST /api/v1/cart/update`
- Input (method, URL, body): Update existing cart item to quantity `0`
- Expected output: `400 Bad Request`
- Why this test is needed: Enforces minimum quantity on updates.

### Test Case: test_cart_remove_non_existing_product_returns_404
- Endpoint tested: `POST /api/v1/cart/remove`
- Input (method, URL, body): Remove product not in cart
- Expected output: `404 Not Found`
- Why this test is needed: Verifies correct error signaling for absent cart items.

### Test Case: test_coupon_expired_coupon_rejected
- Endpoint tested: `POST /api/v1/coupon/apply`
- Input (method, URL, body): Apply expired coupon `DEAL5`
- Expected output: `400 Bad Request`
- Why this test is needed: Ensures expiry checks are enforced.

### Test Case: test_coupon_min_cart_value_enforced
- Endpoint tested: `POST /api/v1/coupon/apply`
- Input (method, URL, body): Apply `BONUS75` with low cart total
- Expected output: `400 Bad Request`
- Why this test is needed: Verifies minimum cart value rule.

### Test Case: test_checkout_empty_cart_rejected
- Endpoint tested: `POST /api/v1/checkout`
- Input (method, URL, body): Empty cart + `{"payment_method":"COD"}`
- Expected output: `400 Bad Request`
- Why this test is needed: Prevents invalid order creation without cart items.

### Test Case: test_checkout_invalid_payment_method_rejected
- Endpoint tested: `POST /api/v1/checkout`
- Input (method, URL, body): `{"payment_method":"UPI"}`
- Expected output: `400 Bad Request`
- Why this test is needed: Enforces allowed methods (`COD`, `WALLET`, `CARD`).

### Test Case: test_checkout_cod_over_5000_rejected
- Endpoint tested: `POST /api/v1/checkout`
- Input (method, URL, body): High-value cart + `{"payment_method":"COD"}`
- Expected output: `400 Bad Request`
- Why this test is needed: Validates COD upper limit rule.

### Test Case: test_checkout_gst_added_once
- Endpoint tested: `POST /api/v1/checkout`
- Input (method, URL, body): One item of price `20` with `CARD`
- Expected output: `gst_amount=1`, `total_amount=21`
- Why this test is needed: Confirms GST computation and single application.

### Test Case: test_wallet_add_invalid_amounts_rejected
- Endpoint tested: `POST /api/v1/wallet/add`
- Input (method, URL, body): `amount=0`, `amount=100001`
- Expected output: `400 Bad Request` for both
- Why this test is needed: Validates wallet top-up boundaries.

### Test Case: test_wallet_pay_must_deduct_exact_amount
- Endpoint tested: `POST /api/v1/wallet/add`, `POST /api/v1/wallet/pay`, `GET /api/v1/wallet`
- Input (method, URL, body): Add `10`, pay `5`, compare before/after balances
- Expected output: Deduction should be exactly `5`
- Why this test is needed: Ensures payment debits are mathematically correct.

### Test Case: test_wallet_pay_insufficient_balance_rejected
- Endpoint tested: `POST /api/v1/wallet/pay`
- Input (method, URL, body): `{"amount":999999}`
- Expected output: `400 Bad Request`
- Why this test is needed: Checks insufficient funds handling.

### Test Case: test_loyalty_redeem_invalid_values_rejected
- Endpoint tested: `POST /api/v1/loyalty/redeem`
- Input (method, URL, body): `points=0`, `points=999999`
- Expected output: `400 Bad Request`
- Why this test is needed: Enforces loyalty redeem validation.

### Test Case: test_order_detail_non_existing_returns_404
- Endpoint tested: `GET /api/v1/orders/{order_id}`
- Input (method, URL, body): `GET /orders/999999`
- Expected output: `404 Not Found`
- Why this test is needed: Confirms missing-order handling.

### Test Case: test_cancel_delivered_order_rejected
- Endpoint tested: `POST /api/v1/orders/{order_id}/cancel`
- Input (method, URL, body): Cancel delivered order
- Expected output: `400 Bad Request`
- Why this test is needed: Enforces cancellation state rules.

### Test Case: test_cancel_non_existing_order_returns_404
- Endpoint tested: `POST /api/v1/orders/{order_id}/cancel`
- Input (method, URL, body): Cancel non-existent order
- Expected output: `404 Not Found`
- Why this test is needed: Validates missing resource behavior.

### Test Case: test_cancel_order_restocks_inventory
- Endpoint tested: `POST /api/v1/orders/{order_id}/cancel`, `GET /api/v1/products/{product_id}`
- Input (method, URL, body): Create order with quantity 1, cancel, compare stock before vs after cancel
- Expected output: Stock after cancel should increase by 1
- Why this test is needed: Ensures order cancellation properly returns stock.

### Test Case: test_invoice_total_matches_order_total
- Endpoint tested: `GET /api/v1/orders/{order_id}`, `GET /api/v1/orders/{order_id}/invoice`
- Input (method, URL, body): Query fresh order and corresponding invoice
- Expected output: `subtotal + gst = invoice_total` and `invoice_total = order_total`
- Why this test is needed: Validates invoice correctness and consistency.

### Test Case: test_support_create_subject_and_message_boundaries
- Endpoint tested: `POST /api/v1/support/ticket`
- Input (method, URL, body): Subject too short, message too long (`501` chars)
- Expected output: `400 Bad Request` in both cases
- Why this test is needed: Verifies support-ticket validation limits.

### Test Case: test_support_message_saved_exactly
- Endpoint tested: `POST /api/v1/support/ticket`, `GET /api/v1/admin/tickets`
- Input (method, URL, body): Create ticket with unique message string and retrieve from admin tickets
- Expected output: Stored message exactly matches submitted message
- Why this test is needed: Ensures no truncation or mutation of user support text.

### Test Case: test_support_invalid_status_transition_rejected
- Endpoint tested: `PUT /api/v1/support/tickets/{ticket_id}`
- Input (method, URL, body): Try `OPEN -> CLOSED` directly
- Expected output: `400 Bad Request`
- Why this test is needed: Enforces one-direction transition rules.

### Test Case: test_support_update_non_existing_ticket_returns_404
- Endpoint tested: `PUT /api/v1/support/tickets/{ticket_id}`
- Input (method, URL, body): `PUT /support/tickets/999999`
- Expected output: `404 Not Found`
- Why this test is needed: Confirms proper missing-ticket behavior.

## Bug Group 1

### Bug 1
- Endpoint tested: `POST /api/v1/cart/add`
- Request payload: `{"product_id":1,"quantity":0}`
- Expected result: `400 Bad Request` because quantity must be at least 1
- Actual result: `200 OK` with `{"message":"Item added to cart"}`

### Bug 2
- Endpoint tested: `GET /api/v1/cart`
- Request payload: After adding `{"product_id":1,"quantity":2}`
- Expected result: Item `subtotal = 240`, cart `total = 240`
- Actual result: Item `subtotal = -16`, cart `total = 0`

### Bug 3
- Endpoint tested: `POST /api/v1/coupon/apply`
- Request payload: `{"coupon_code":"DEAL5"}` (expired in docs timeline)
- Expected result: `400 Bad Request` (expired coupon should be rejected)
- Actual result: `200 OK` with discount applied

## Bug Group 2

### Bug 4
- Endpoint tested: `POST /api/v1/checkout`
- Request payload: Empty cart + `{"payment_method":"COD"}`
- Expected result: `400 Bad Request` because checkout must reject empty carts
- Actual result: `200 OK` and order created with `total_amount=0`

### Bug 5
- Endpoint tested: `POST /api/v1/products/{product_id}/reviews`
- Request payload: `{"rating":0,"comment":"below range"}` and `{"rating":6,"comment":"above range"}`
- Expected result: `400 Bad Request` for ratings outside 1..5
- Actual result: `200 OK` and review records created

### Bug 6
- Endpoint tested: `PUT /api/v1/addresses/{address_id}`
- Request payload: `{"street":"99999 Updated Street ...","is_default":true}`
- Expected result: Updated address data should be returned and persisted
- Actual result: `200 OK` but response contains old address values; follow-up `GET /addresses` shows values unchanged
