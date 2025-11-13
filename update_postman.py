#!/usr/bin/env python3
"""
Auto-update Postman collection from FastAPI OpenAPI spec
"""

import json
import requests
import sys
from typing import Dict, Any

def get_openapi_spec(base_url: str = "http://localhost:8000") -> Dict[Any, Any]:
    """Get OpenAPI specification from running FastAPI server"""
    try:
        response = requests.get(f"{base_url}/openapi.json")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Failed to get OpenAPI spec: {e}")
        return None

def update_postman_collection(openapi_spec: Dict[Any, Any]) -> Dict[Any, Any]:
    """Update Postman collection based on OpenAPI spec"""
    
    # Load existing collection
    try:
        with open("postman_collection.json", "r") as f:
            collection = json.load(f)
    except FileNotFoundError:
        print("❌ Postman collection not found")
        return None
    
    # Extract API info
    info = openapi_spec.get("info", {})
    paths = openapi_spec.get("paths", {})
    
    # Update collection info
    collection["info"]["name"] = info.get("title", "CoreX Banking System API")
    collection["info"]["description"] = info.get("description", "")
    
    # Track new endpoints
    new_endpoints = []
    existing_paths = set()
    
    # Extract existing paths from collection
    for item in collection["item"]:
        for endpoint in item.get("item", []):
            if "url" in endpoint.get("request", {}):
                path = endpoint["request"]["url"]["path"]
                if isinstance(path, list):
                    existing_paths.add("/" + "/".join(path))
    
    # Check for new endpoints
    for path, methods in paths.items():
        if path not in existing_paths:
            for method, details in methods.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    new_endpoints.append({
                        "path": path,
                        "method": method.upper(),
                        "summary": details.get("summary", ""),
                        "description": details.get("description", ""),
                        "tags": details.get("tags", [])
                    })
    
    return collection, new_endpoints

def generate_postman_request(endpoint: Dict[str, Any]) -> Dict[str, Any]:
    """Generate Postman request from endpoint info"""
    path_parts = [part for part in endpoint["path"].split("/") if part]
    
    return {
        "name": endpoint["summary"] or f"{endpoint['method']} {endpoint['path']}",
        "request": {
            "method": endpoint["method"],
            "header": [
                {
                    "key": "Content-Type",
                    "value": "application/json"
                }
            ] if endpoint["method"] in ["POST", "PUT", "PATCH"] else [],
            "url": {
                "raw": "{{base_url}}" + endpoint["path"],
                "host": ["{{base_url}}"],
                "path": path_parts
            }
        },
        "response": []
    }

def main():
    print("🔄 Updating Postman collection from OpenAPI spec...")
    
    # Get OpenAPI spec
    openapi_spec = get_openapi_spec()
    if not openapi_spec:
        sys.exit(1)
    
    # Update collection
    result = update_postman_collection(openapi_spec)
    if not result:
        sys.exit(1)
    
    collection, new_endpoints = result
    
    if new_endpoints:
        print(f"📝 Found {len(new_endpoints)} new endpoints:")
        for endpoint in new_endpoints:
            print(f"  + {endpoint['method']} {endpoint['path']} - {endpoint['summary']}")
        
        # Add new endpoints to appropriate folders
        for endpoint in new_endpoints:
            tags = endpoint.get("tags", [])
            folder_name = tags[0] if tags else "Miscellaneous"
            
            # Find or create folder
            folder = None
            for item in collection["item"]:
                if item["name"].lower() == folder_name.lower():
                    folder = item
                    break
            
            if not folder:
                folder = {
                    "name": folder_name,
                    "item": []
                }
                collection["item"].append(folder)
            
            # Add request to folder
            request = generate_postman_request(endpoint)
            folder["item"].append(request)
        
        # Save updated collection
        with open("postman_collection.json", "w") as f:
            json.dump(collection, f, indent=2)
        
        print("✅ Postman collection updated successfully!")
    else:
        print("✅ No new endpoints found. Collection is up to date.")

if __name__ == "__main__":
    main()