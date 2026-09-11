def accept(events):
    seen = set()
    accepted = []
    for event in events:
        key = event["batch_id"]
        if key in seen:
            continue
        seen.add(key)
        accepted.append(event["item_id"])
    return accepted
