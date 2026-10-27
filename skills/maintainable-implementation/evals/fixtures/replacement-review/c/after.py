def event_id(message):
    return message['eventId'] if 'eventId' in message else message['id']


def consume(message, handled):
    handled.append(event_id(message))
