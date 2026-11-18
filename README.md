# Househunting & Property Listing Platform (Kenya)

A full-stack Django web application connecting customers seeking vacant houses and rooms with verified house owners and real estate agents in Kenya. The platform enforces strict user onboarding, admin verification gates, free-tier posting quotas, subscription upgrades, and screenshot-based M-Pesa Paybill payment verification.

## Core Workflows & User Roles

### 1. Customers (House Seekers)
- **Onboarding:** Register with name, email (OTP-verified), phone number, preferred location, and budget.
- **Property Discovery:** Browse, search, and filter live, admin-approved listings by location, price range, property type, and amenities.
- **Deposit Options:** Choose between Advance Deposit (reserve prior to inspection) or Pay After Inspection.
- **M-Pesa Screenshot Payment Flow:** Select Pay Now to view the owner Paybill/Till number and reference code, pay via M-Pesa, and upload the payment screenshot with transaction details for manual verification.

### 2. House Owners & Agents
- **Onboarding Gate:** Register, verify email via OTP, and upload KYC documents (National ID/Passport, proof of ownership/authorization, title deed/lease, business permit, selfie). Posting is locked until Admin approves.
- **Free-Tier & Subscriptions:** Approved owners receive a free-tier listing quota before upgrading via M-Pesa screenshot verification.
- **Listing Moderation:** All listings enter Pending Review and require Admin approval before going live.

### 3. System Administrators
- **Verification Queues:** Review owner KYC documents, moderate property listings, and cross-check M-Pesa payment screenshots with automatic duplicate transaction code detection.

## Local Setup

1. Create and activate virtual environment:
   python -m venv venv
   .\venv\Scripts\Activate
2. Install dependencies:
   pip install -r requirements.txt
3. Run migrations and start server:
   python manage.py migrate
   python manage.py runserver
