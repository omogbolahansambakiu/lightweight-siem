"""OpenSearch Client Wrapper"""
from opensearchpy import OpenSearch
import os

class OpenSearchClient:
    def __init__(self):
        self.client = OpenSearch(
            hosts=[{
                "host": os.getenv("OPENSEARCH_HOST", "opensearch"),
                "port": int(os.getenv("OPENSEARCH_PORT", 9200))
            }],
            http_auth=(
                os.getenv("OPENSEARCH_USER", "admin"),
                os.getenv("OPENSEARCH_PASSWORD", "admin")
            ),
            use_ssl=False,
            verify_certs=False
        )
    
    def index_event(self, index, event):
        return self.client.index(index=index, body=event)
    
    def search(self, index, query):
        return self.client.search(index=index, body=query)
