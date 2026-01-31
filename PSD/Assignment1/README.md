# Car Rental System (CLI MVP)

## 1) Project Overview
This is a command-line Car Rental System built as a minimum viable product (MVP). Customers can register and book cars; admins can add cars and approve or reject bookings. The goal is a small but complete workflow that is easy to demo and easy to extend.

## 2) Features

### Customer
- Register (email-only login, no password)
- Login
- List available cars (numbered list)
- Create booking (start date + rental days + add-ons)
- View my bookings (numbered list + details)

### Admin
- Login (email)
- Add car
- List cars
- List pending bookings
- Approve / reject bookings

## 3) Project Structure
- `src/models` — data models (User, Car, Booking)
- `src/repositories` — SQLite CRUD only (no business rules)
- `src/services` — business rules (validation, overlap checks, pricing)
- `src/ui` — CLI menus + input/output

Documentation:
- `docs/uml` — UML diagrams (PNG)
- `docs/Design_Report.md` — design & architecture report
- `docs/maintenance.md` — maintenance & support report

## 4) Files Included
- `README.md`
- `docs/Design_Report.md`
- `docs/maintenance.md`
- `docs/uml/*.png`
- `src/` (all source code)
- `requirements.txt`

## 5) Requirements / Dependencies
- Python 3.9+ recommended
- No third-party dependencies required (standard library only)

## 6) How to Run
From the assignment root folder (the folder that contains `src/`):

```bash
python3 -m src.main
```

On first run, a default admin is created if missing:
- Email: `admin@example.com`

## 7) Demo Script (for marking)
Follow these steps exactly to show the full workflow. The CLI uses numbered lists, so choose item numbers rather than typing UUIDs.

### A) Admin login -> Add car -> List cars
1. Start the app: `python3 -m src.main`
2. Choose **Admin** (menu: `2`)
3. Login with email: `admin@example.com`
4. Choose **Add car** and enter sample data:
   - Plate no: `AKL-100`
   - Make: `Toyota`
   - Model: `Corolla`
   - Year: `2020`
   - Mileage: `30000`
   - Category: `economy`
   - Daily rate: `55`
   - Deposit: `100`
   - Min rent days: `1`
   - Max rent days: `7`
   - Location: press **Enter** to accept default `Auckland`
5. Choose **List cars** and confirm the new car appears.

### B) Customer register -> Customer login
1. Go back to main menu, choose **Customer** (menu: `1`)
2. Register:
   - Name: `Test User`
   - Email: `test1@example.com`
   - Phone: optional (press Enter to skip)
   - Driver license no: `NZ12345`
3. Login with email: `test1@example.com`

### C) List available cars -> Create booking (pending)
1. Choose **List available cars** and note the car number.
2. Choose **Create booking**:
   - Select the car by number
   - Start date: press Enter to accept default (tomorrow)
   - Rental days: enter `2`
   - Insurance plan: `none`
   - Add-ons: enter `1,3` or press Enter to skip
3. You should see “Booking created” with estimated total.

### D) Admin list pending -> Approve booking
1. Go back to **Admin** menu and login.
2. Choose **List pending bookings**.
3. Choose **Approve booking**, select the booking by number.

### E) Customer view my bookings -> status=approved
1. Go back to **Customer** menu and login.
2. Choose **View my bookings** and select the booking by number.
3. Confirm status shows **approved**.

## 8) Data Storage
- SQLite database is stored at: `data/app.db`
- To reset all data, delete the file:

```bash
rm -f data/app.db
```

## 9) Known Limitations / Future Work
- Email-only login (no password system)
- No payment or refund workflow
- Limited automated tests
- Optional enhancements: cancellation/late fees, reporting/export features

## 10) Author / License
Author: Weizhao Tan  
License: For educational use only
