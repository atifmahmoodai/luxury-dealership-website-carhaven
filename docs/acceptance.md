# Acceptance and actual delivery scope

The repository originally recorded a public CarHaven brief. This build is a custom implementation option, not the original buyer's website and not a claim of client acceptance.

| Requirement | Delivered behavior | Client validation |
| --- | --- | --- |
| Luxury, responsive, fast | Editorial layout, server-rendered pages, optimized photo bounds, no external font/tracker dependency | Approve design, real assets and device checks |
| Inventory/details/photos/specs | Filters, pagination, detail pages, staff image gallery and stock states | Verify real stock, price currency, mileage and specifications |
| Staff edits without developer | Permission-based Django staff studio with draft/publish/archive workflow | Train actual staff and approve access roles |
| Contact, WhatsApp or phone | Persisted enquiries with consent; configurable external contact links | Supply real destinations; assign a person to review enquiries |
| About/company identity | Editable deployment settings and proposed copy | Supply logo, company facts, address and approved wording |
| SEO friendly | Titles/descriptions/canonical URLs, sitemap and demo noindex | Confirm canonical domain, indexing approval and local search content |

Acceptance walkthrough:

1. Add two staff accounts with Inventory team permissions; confirm neither can manage users.
2. Create a draft, attempt publication without photos (must fail), upload licensed actual photos, save, then publish. Check desktop/mobile and alt text.
3. Filter by make/body/price, sort and paginate. Confirm archived/draft records and photos cannot be retrieved anonymously.
4. Submit an authorized test enquiry, repeat its POST and verify one saved record. Review it in staff, update the status and inspect audit history. No email or WhatsApp should be sent automatically.
5. Mark the car sold and then archive it. Confirm visitor behavior and private retention match the dealership's preferred policy.
6. Supply privacy contact and retention decisions, enable approved production configuration, run Django deployment checks, and conduct the full off-host database/photo restore drill.

Outstanding client inputs are real assets, company/contact information, price/stock approval, privacy/retention review, domain/VPS credentials, training and launch acceptance. Automated tests and source delivery do not establish that a buyer's live business is operating on the site.
