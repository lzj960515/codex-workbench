from config import SETTINGS
from registry import ConverterRegistry
from writer import ShadowWriter


def discover(store, rows):
    writer = ShadowWriter(store)
    converter = ConverterRegistry().get('article')
    for row in rows:
        writer.save(converter.normalize(row), shadow=SETTINGS['shadow_mode'])
    return [row['id'] for row in rows]


def import_csv(store, rows):
    writer = ShadowWriter(store)
    for row in rows:
        writer.save(row, shadow=False)
    return [row['id'] for row in rows]
