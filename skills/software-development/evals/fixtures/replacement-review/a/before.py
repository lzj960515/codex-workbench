SHADOW_ENABLED = True


def shadow_save(result, event):
    result.append(event)


def accept(result, event):
    if SHADOW_ENABLED:
        shadow_save(result, event)
    else:
        result.append(event)
