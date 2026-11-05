def consume(message, handled):
    handled.append(message['id'])
