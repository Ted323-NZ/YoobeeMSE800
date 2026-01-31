# Car Rental System Specification

## 1. Purpose and Scope
This specification describes a CLI-based Car Rental System (MVP). It supports two roles (Customer and Admin), basic car management, booking creation/approval, and price estimation. The goal is a clean, working core that is easy to extend.

Out of scope for this MVP: real payment/refund integration and advanced reporting.

## 2. Roles and Permissions

**Customer**
- Register and login
- Browse available cars
- Create bookings
- View own bookings

**Admin**
- Login
- Add and manage cars
- List cars
- View pending bookings
- Approve or reject bookings

## 3. Data Models

### 3.1 User
- id: UUID
- role: customer | admin
- name: string
- email: string (unique)
- phone: string (optional)
- driver_license_no: string (required for customer)
- status: active | suspended
- created_at, updated_at: ISO datetime (UTC)

### 3.2 Car
- id: UUID
- plate_no: string (unique)
- make: string
- model: string
- year: integer
- mileage: integer (>= 0)
- available_now: boolean
- min_rent_days: integer (>= 1)
- max_rent_days: integer (<= 30, >= min_rent_days)
- daily_rate: decimal (> 0)
- deposit: decimal (>= 0)
- category: economy | compact | suv | luxury | van
- status: active | maintenance | retired
- location: string
- created_at, updated_at: ISO datetime (UTC)

### 3.3 Booking
- id: UUID
- user_id: UUID
- car_id: UUID
- start_date, end_date: ISO date (end_date is exclusive)
- status: pending | approved | rejected | cancelled | active | completed | overdue
- pickup_time, return_time: ISO datetime (UTC, optional)
- base_daily_rate: decimal (snapshot)
- addons: JSON/dict snapshot (e.g., {"GPS": "5.00"})
- insurance_plan: none | basic | premium
- insurance_daily_fee: decimal (>= 0)
- late_fee_per_day: decimal (>= 0)
- total_estimated: decimal
- total_final: decimal (optional)
- created_at, updated_at: ISO datetime (UTC)

## 4. Business Rules

### 4.1 Rental period
- Global rule: 1–30 days
- Car rule: rental_days must be within car.min_rent_days and car.max_rent_days
- start_date must be today or later

### 4.2 Availability and overlap
- A car must have **status = active** to accept new bookings.
- A booking cannot overlap with existing bookings for the same car if the status is **approved**, **active**, or **overdue**.
- Overlap rule: NOT (new_end <= existing_start OR new_start >= existing_end)

### 4.3 Booking flow
- Customer creates booking → status = pending
- Admin approves → status = approved
- Admin rejects → status = rejected
- Pickup → status = active
- Return → status = completed or overdue

## 5. Pricing

### 5.1 Estimated total
- rental_days = (end_date − start_date).days  
  (end_date is exclusive: e.g., 2026-01-01 → 2026-01-02 = 1 day)
- base_fee = rental_days × base_daily_rate
- addons_fee = sum(addon_daily_price) × rental_days
- insurance_fee = insurance_daily_fee × rental_days
- estimated_total = base_fee + addons_fee + insurance_fee

### 5.2 Late fee
- late_days = max(0, (return_time.date() − end_date).days)
- late_fee = late_days × late_fee_per_day
- if late_days > 3, add penalty = 1 × base_daily_rate

### 5.3 Cancellation fee
- if cancelled within 24 hours before start_date → 1 × base_daily_rate
- otherwise → 0

## 6. Error Handling (CLI)
If a rule is violated, the system shows a clear error message and does not create/approve the booking.

- Invalid dates (start >= end or in the past) → reject booking
- Car not active or unavailable → reject booking
- User suspended → reject booking
- Overlapping booking → reject booking
- Invalid pricing (negative or zero rates) → reject booking

## 7. Non-Functional Requirements
- CLI is the only user interface
- SQLite local database, no external services
- Monetary values use Decimal to avoid rounding errors
- UTC timestamps for consistency

## 8. Future Work
- Background consistency repair job to resolve mismatched car/booking states
- Database migration scripts for future schema changes
- Payment/refund integration
- Reporting and export features
