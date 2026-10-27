class ShadowWriter:
    def __init__(self, store):
        self.store = store

    def save(self, row, shadow=True):
        if shadow:
            return self._save_current(row)
        return self._save_current(row)

    def _save_current(self, row):
        self.store[row['id']] = dict(row)
