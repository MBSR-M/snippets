import logging

# logger = logging.getLogger(__name__)


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
        logging.info(f"Extracting MPSR file for date: {self.date}")
        return file_name


if __name__ == "__main__":
    extractor = MPSRFileExtractor("2023-01-01")
    try:
        file_name = extractor.get_mpsr_file()
        logging.info(file_name)
    except ValueError as e:
        logging.error(e)
