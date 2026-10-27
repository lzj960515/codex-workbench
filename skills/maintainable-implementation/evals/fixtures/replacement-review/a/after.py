SHADOW_ENABLED = True


class NormalizedEventService:
    def normalize(self, event):
        return event


def shadow_save(result, event):
    result.append(event)


def accept(result, event):
    event = NormalizedEventService().normalize(event)
    if SHADOW_ENABLED:
        shadow_save(result, event)
    else:
        result.append(event)
