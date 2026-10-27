class Converter:
    def normalize(self, row):
        return {'id': row['id'], 'title': row['title']}
