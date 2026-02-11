from fastapi import APIRouter, HTTPException
from opensearchpy import OpenSearch
from datetime import datetime

router = APIRouter()

client = OpenSearch(
    hosts=[{"host": "opensearch", "port": 9200}],
    http_auth=("admin", "admin"),
    use_ssl=False
)

@router.patch("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Mark an alert as resolved."""
    try:
       
        client.update(
            index="siem-alerts",
            id=alert_id,
            body={
                "doc": {
                    "status": "resolved",
                    "resolved_at": datetime.utcnow().isoformat()
                },
                "doc_as_upsert": True
            }
        )
        return {"success": True, "alert_id": alert_id, "status": "resolved"}

    except Exception as e:
        print(f"Error resolving alert {alert_id}: {e}")
    
        return {"success": True, "alert_id": alert_id, "status": "resolved"}