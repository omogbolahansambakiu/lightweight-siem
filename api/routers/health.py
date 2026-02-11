from fastapi import APIRouter
import redis
from opensearchpy import OpenSearch
import os

router = APIRouter()

@router.get("/health")
async def health_check():
    checks = {
        "status": "healthy",
        "services": {}
    }
    
    # Check Redis
    try:
        r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"))
        r.ping()
        checks["services"]["redis"] = "up"
    except:
        checks["services"]["redis"] = "down"
        checks["status"] = "unhealthy"
    
    # Check OpenSearch
    try:
        es = OpenSearch(hosts=[{"host": os.getenv("OPENSEARCH_HOST", "opensearch"), "port": 9200}])
        es.info()
        checks["services"]["opensearch"] = "up"
    except:
        checks["services"]["opensearch"] = "down"
        checks["status"] = "unhealthy"
    
    return checks

@router.get("/metrics")
async def get_metrics():
    return {"events_processed": 0, "alerts_generated": 0}
