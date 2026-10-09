# Deployment, ownership and recovery

## VPS launch

Use a maintained Linux VPS, Docker/Compose, private persistent storage and a domain. Set up SSH keys, security updates, monitoring and a firewall exposing only 80/443 publicly. PostgreSQL and Gunicorn have no published ports in Compose.

1. Copy `.env.example` to `.env` and `chmod 600 .env`. Generate independent random hexadecimal passwords and a secret key of at least 50 characters. Use hex for APP_DB_PASSWORD because it is embedded in a PostgreSQL URL.
2. Populate the real domain, approved company name/about/address, email, international phone number and currency. WHATSAPP is optional international digits without `+`. The project has no supplied real contact destinations.
3. Review site wording, privacy/retention policy, image rights and actual stock data. Only then set `CLIENT_APPROVED=1`. Demo stock is excluded automatically; do not relabel fictional records as real cars.
4. Point DNS to the VPS and run `docker compose up -d --build`. The empty-volume initialization script creates a non-superuser database owner. Gunicorn serves the application and WhiteNoise serves version-controlled static assets; Caddy terminates TLS.
5. Run `docker compose exec app python manage.py createsuperuser`, then `docker compose exec app python manage.py setup_roles`. Add individual staff accounts and grant only the required group permissions. Keep owner credentials separate.
6. Check `/health/`, TLS, cookie security, staff login, photo upload, publication, enquiry receipt and staff review on the actual domain. Do not create a real buyer enquiry as a deployment test; use authorized fictional test data and remove it afterward.

Production uses `ENVIRONMENT=production`, PostgreSQL, secure cookies and HTTPS. `TRUST_PROXY=1` assumes the app is reachable only through the bundled proxy; Caddy overwrites X-Real-IP and forwarded protocol. Do not expose Gunicorn directly or put an extra proxy in front without reviewing this trust boundary. Login and enquiry throttles are per-IP; shared networks may share a limit. No MFA/SSO is included; an operator-managed private access gateway can protect `/staff/` if required.

Staff notifications are **manual** in this release: check the enquiry queue routinely. No SMTP, marketing automation or external CRM is configured. Phone/email/WhatsApp links open external applications only after a visitor clicks them.

Changing database secrets in `.env` does not rotate a role in an existing database volume. Rotate credentials in PostgreSQL and update application configuration together. Never run `docker compose down -v` on a live installation.

## Backups

Run `sh scripts/backup.sh /absolute/new-snapshot-directory` from the repo root. It creates a consistent SQL dump followed by a complete photo archive and checksums, with private filesystem permissions. Image filenames are generated; edits write new files and old files are not automatically pruned, so copying after the SQL snapshot preserves its referenced files under normal operation.

Encrypt and copy snapshots off-host, secure the encryption keys separately, and alert on failures. Store environment/configuration secrets separately in an encrypted operator vault. Photos, database records and logs contain sensitive information; agree retention and access policies. Daily snapshots leave a daily potential loss window; use PostgreSQL continuous archiving and matching photo replication if the agreed RPO needs better protection. Do not promise zero loss from this setup.

## Restore drill

Restore on an isolated staging host using empty volumes, the same PostgreSQL major version, and a staging domain. Do not overwrite production.

1. Start only the database (`docker compose up -d db`). Initialization creates an empty `carhaven` database and its role.
2. Verify snapshot checksums and restore:

```sh
docker compose exec -T db pg_restore -U postgres -d carhaven --no-owner --role=carhaven --exit-on-error < /secure/snapshot/database.dump
docker compose build app
docker compose run --rm --no-deps -T app tar -C /data/photos -xf - < /secure/snapshot/photos.tar
```

3. Clear `django_session` on the restored database before opening staff access. Keep the cloned deployment private.
4. Start the application. Compare vehicle/enquiry counts, open a sample of published and draft photos, confirm draft photos remain private, and exercise a fictional enquiry. Check `/staff/` history. Record restored timestamp, restoration time and missing-file checks against RPO/RTO.
5. A production cutover needs a separately reviewed operating plan. Back up before every upgrade and rehearse migrations in staging. Never treat an untested archive as a verified backup.

## Operations

Monitor HTTP errors, disk capacity, database/backup health and unreviewed enquiries. Deactivate departing users. Audit administrator access. Staff changes are logged by Django; privileged database operators can alter history, so this is not a tamper-proof compliance archive. Expired session/throttle rows should be pruned periodically using a documented maintenance window; do not delete live sessions arbitrarily.

Sources: [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/), [PostgreSQL backup](https://www.postgresql.org/docs/17/backup.html), [Caddy reverse proxy](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy).
