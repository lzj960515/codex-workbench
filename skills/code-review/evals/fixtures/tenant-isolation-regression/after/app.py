NOTES = [
    {"id": "note-1", "store_id": "store-a", "text": "A private note"},
    {"id": "note-2", "store_id": "store-b", "text": "B private note"},
]


NOTES_BY_ID = {note["id"]: note for note in NOTES}


def get_note(store_id, note_id):
    return NOTES_BY_ID.get(note_id)


def handle_request(authenticated_store, query_note_id):
    note = get_note(authenticated_store, query_note_id)
    return {"status": 404} if note is None else {"status": 200, "body": note}
