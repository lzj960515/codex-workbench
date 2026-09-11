def build_headers(request_id):
    return {"Content-Type": "application/json", "Request-Id": request_id}
