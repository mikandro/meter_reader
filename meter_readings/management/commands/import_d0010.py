import os
import re
import csv
from django.core.management.base import BaseCommand, CommandError
from meter_readings.models import MeterPoint, Meter, Reading, ProcessedFile
from datetime import datetime

class Command(BaseCommand):
    help = 'Import D0010 meter reading file(s) and store the readings in the database.'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='Path to a D0010 file or a directory containing D0010 files')

    def handle(self, *args, **options):
        path = options['path']

        if os.path.isfile(path):
            # If a single file is provided, process that file
            self.process_file(path)
        elif os.path.isdir(path):
            # If a directory is provided, process all files in that directory
            for file_name in os.listdir(path):
                full_file_path = os.path.join(path, file_name)
                if os.path.isfile(full_file_path) and file_name.endswith('.uff'):
                    self.process_file(full_file_path)
        else:
            raise CommandError(f"'{path}' is neither a file nor a directory.")

    def process_file(self, file_path):
        """Process a single D0010 file and store the readings in the database."""
        file_name = os.path.basename(file_path)

        if ProcessedFile.objects.filter(file_name=file_name).exists():
            self.stdout.write(self.style.WARNING(f"File '{file_name}' has already been processed. Skipping."))
            return

        try:
            current_mpan = None
            current_serial_number = None

            with open(file_path, 'r') as file:
                reader = csv.reader(file, delimiter='|')

                for row in reader:
                    if not row or len(row) < 3:
                        continue  # Skip empty or malformed rows

                    record_type = row[0].strip()

                    # Process 026 line: Contains MPAN (MPAN = Meter Point Administration Number)
                    if record_type == '026':
                        current_mpan = row[1].strip()

                    # Process 028 line: Contains the meter serial number
                    elif record_type == '028':
                        # TODO Not sure if having spaces in the serial number is normal. Remove for now
                        current_serial_number = re.sub(r'\s+', '', row[1].strip())

                    # Process 030 line: Contains the reading value, register ID, and date
                    elif record_type == '030':
                        meter_register_id = row[1].strip()
                        reading_date = row[2].strip()
                        reading_value = row[3].strip()

                        try:
                            reading_value = float(reading_value)
                        except ValueError:
                            self.stdout.write(self.style.WARNING(f"Invalid reading value in row: {row}"))
                            continue

                        if not self.is_valid_date(reading_date):
                            self.stdout.write(self.style.WARNING(f"Invalid date in row: {row}"))
                            continue

                        meter_point, _ = MeterPoint.objects.get_or_create(mpan=current_mpan)
                        meter, _ = Meter.objects.get_or_create(serial_number=current_serial_number, meter_point=meter_point)

                        Reading.objects.create(
                            meter=meter,
                            value=reading_value,
                            reading_date=self.parse_date(reading_date),
                            meter_register_id=meter_register_id,
                            file_name=file_name
                        )

                # Mark the file as processed
                ProcessedFile.objects.create(file_name=file_name)
                self.stdout.write(self.style.SUCCESS(f'Successfully imported readings from {file_path}'))

        except Exception as e:
            raise CommandError(f'Error processing file {file_path}: {e}')

    def is_valid_date(self, date_str):
        """Validate the reading date format (YYYYMMDDHHMMSS)."""
        try:
            # Dummy check if it's a valid datetime format for YYYYMMDDHHMMSS
            if len(date_str) == 14:
                datetime.strptime(date_str, '%Y%m%d%H%M%S')
                return True
        except ValueError:
            return False
        return False

    def parse_date(self, date_str):
        """Convert date string to datetime object."""
        return datetime.strptime(date_str, '%Y%m%d%H%M%S')

