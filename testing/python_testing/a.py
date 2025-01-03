class MPSRFileExtractor:
    def __init__(self, date):
        self.date = date

    def validate_date(self, date):
        # Implement date validation logic here
        return True

    def get_mpsr_file(self):
        validate = self.validate_date(self.date)
        if not validate:
            raise ValueError("Date cannot be greater than Yesterday")
        file_name = f"mpsr-dailyload-{self.date.replace('-', '')}-1d.csv.zip"

