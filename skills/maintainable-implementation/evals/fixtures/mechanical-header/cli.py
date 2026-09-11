from headers import build_headers


def response_metadata(request_id):
    return build_headers(request_id)
