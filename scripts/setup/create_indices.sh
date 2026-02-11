#!/bin/bash
curl -X PUT "http://localhost:9200/siem-events" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1
  }
}
'

curl -X PUT "http://localhost:9200/siem-alerts" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1
  }
}
'

echo "Indices created"
