def consume(message, handled):
    event_id = message['eventId'] if 'eventId' in message else message['id']
    handled.append(event_id)
