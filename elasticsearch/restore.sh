#!/bin/bash

set -e

echo "Waiting for Elasticsearch to be ready..."
until curl -s "http://localhost:9200/_cluster/health" | grep -q '"status":"green\|yellow"'; do
  echo "Waiting for Elasticsearch to be ready..."
  sleep 5
done

if [ "$(curl -s http://localhost:9200/_cat/indices?h=status | wc -l)" -eq 0 ]; then
  echo "Cluster is empty. Restoring snapshot..."

  curl -sS -X PUT "http://localhost:9200/_snapshot/is_snapshot" -H 'Content-Type: application/json' -d '
    {
      "type": "fs",
      "settings": {
        "location": "/usr/share/elasticsearch/backup/is_snapshot"
      }
    }
  '

  curl -sS -X POST "http://localhost:9200/_snapshot/is_snapshot/test/_restore" -H 'Content-Type: application/json' -d '{
    "indices": "*"
  }'
  echo "Snapshot restored successfully."
else
  echo "Cluster is not empty. Skipping snapshot restore."
fi

echo "Restoration process complete."
