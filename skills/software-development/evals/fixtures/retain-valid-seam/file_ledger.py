import csv


class FileLedger:
    def __init__(self, directory):
        self.directory = directory

    def load(self, period):
        with (self.directory / (period + ".csv")).open(newline="") as stream:
            return [{"amount_cents": int(row["amount_cents"])} for row in csv.DictReader(stream)]
