# CarHaven · A considered collection

A dealership website with a working staff inventory backend. Built from the [recorded public brief](docs/original-brief.md), not from the buyer's private code or assets.

## What works

- Luxury editorial design with responsive home, collection, vehicle details, approach, enquiry, privacy and not-found pages.
- Server-rendered inventory search, make/body/price filters, sorting and pagination.
- Authenticated staff studio: add draft vehicles, upload/reorder photos, publish, reserve, mark sold or archive; staff changes use Django's administrator audit history.
- Publication checks require photos for real stock. Draft/archive pages and their photos are inaccessible publicly. Demo vehicles are excluded after client approval.
- Real enquiry persistence, consent validation, CSRF, signed expiring submission identifiers, duplicate-submit prevention, staff review status and notes. Enquiries are stored for manual review; no automatic email or CRM notification is claimed.
- Images limited to 8 MB / 40 megapixels, validated and re-encoded as JPEG without source metadata. Uploaded content is served as an image through a controlled endpoint.
- PostgreSQL production configuration, named storage volumes, TLS proxy, backup procedure, and automated SQL/browser/container verification.
- Canonical URLs, metadata, sitemap, robots rules and semantic HTML. Demo content is explicitly noindex. No SEO ranking guarantee is made.

## Start locally

Python 3.12 is the verified runtime. SQLite is local-only; production requires PostgreSQL.

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py setup_roles
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000` and `/staff/`. No default accounts or passwords are installed. Use `python manage.py changepassword USERNAME` for operator-assisted account recovery. Set `SITE_ORIGIN` if you use another host/port. Never expose the development server or debug mode on the public internet.

The demo contains three fictional sample records. **Their prices, mileage and specifications are examples, not verified offers.** The original SVG illustration is an unbranded concept, not a photograph of a Porsche, Mercedes-Benz or Land Rover. It is intentionally labeled. Replace it with the client's approved photography for real stock.

## Staff workflow

1. Create a vehicle with status **Draft** and accurate stock details.
2. Save, add approved photos with descriptive alt text, and save again.
3. Change status to **Available**. The photo requirement is checked before publishing.
4. Update status to **Reserved** or **Sold** as needed. Sold detail pages remain accessible, but sold cars leave the active collection and stop accepting vehicle-specific enquiries.
5. **Archive** removes the vehicle and its photos from the public site while preserving its record. Inventory deletion is deliberately disabled in the staff interface.
6. Review new enquiries in the staff studio, contact the person through an approved channel, then mark Contacted/Closed. There are no automatic sends.

Run `setup_roles` to create the Inventory team permission group; assign that group and the Staff flag to approved accounts. The group does not grant user administration or enquiry deletion. Review least-privilege access before launch.

## Verification

```sh
python manage.py test inventory
python manage.py makemigrations --check --dry-run
npm install --prefix /tmp/browser playwright@1.56.0
/tmp/browser/node_modules/.bin/playwright install chromium
NODE_PATH=/tmp/browser/node_modules node scripts/browser.cjs
```

The browser test creates a disposable SQLite database and fictional staff account, exercises public filtering/enquiry plus actual staff draft/photo/publish/archive/review actions, and records desktop/mobile screenshots and video. It never contacts a real buyer. CI runs application tests with PostgreSQL 17 and checks production settings/container builds.

## Client acceptance remains

The implementation is delivered in source form. The client's logo, real vehicle photos, company information, contact destinations, currency, jurisdiction-specific privacy/retention decisions, domain and hosting were not supplied. They are required for a live launch. `ENVIRONMENT=production` fails closed until the strong secret, HTTPS origin, PostgreSQL and approved contact/company settings are provided with `CLIENT_APPROVED=1`.

Read [VPS operations](docs/operations.md) and [acceptance / scope](docs/acceptance.md). This is a website and inventory/enquiry CMS, not a full dealer accounting system, online payment service or automatic external inventory feed.
