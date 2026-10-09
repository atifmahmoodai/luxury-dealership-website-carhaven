#!/bin/sh
set -eu
umask 077
target=${1:?Usage: sh scripts/backup.sh /absolute/new-snapshot-directory}
mkdir "$target"
docker compose exec -T db pg_dump -U postgres -d carhaven -Fc > "$target/database.dump"
docker compose exec -T app tar -C /data/photos -cf - . > "$target/photos.tar"
sha256sum "$target/database.dump" "$target/photos.tar" > "$target/SHA256SUMS"
printf 'Snapshot created. Encrypt, copy off-host and complete the restore drill.\n'
