import os
import tempfile
from django.core.management import call_command
from django.test import TestCase
from unittest.mock import patch, mock_open
from meter_readings.models import MeterPoint, Meter, Reading, ProcessedFile

class ImportD0010CommandTest(TestCase):

    def setUp(self):
        """Set up mock data for testing."""
        # Valid file content simulating the format
        self.valid_file_content = (
            "026|1200023305967|V|\n"
            "028| F75A\t00802 |\n"  # Contains spaces and tabs that should be removed
            "030|123|20160222000000|56311.0|\n"
        )

        self.invalid_file_content = (
            "026|1200023305967|V|\n"
            "028| F75A\t00802 |\n"
            "030|123|InvalidDate|56311.0|\n"
        )

    @patch("builtins.open", new_callable=mock_open, read_data="026|1200023305967|V|\n028| F75A\t00802 |\n030|123|20160222000000|56311.0|\n")
    def test_valid_file_processing(self, mock_file):
        """Test that a valid file is processed correctly, including handling whitespace in serial numbers."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".uff")
        temp_file.write(self.valid_file_content.encode('utf-8'))
        temp_file.close()

        call_command('import_d0010', temp_file.name)

        self.assertTrue(ProcessedFile.objects.filter(file_name=os.path.basename(temp_file.name)).exists())
        meter = Meter.objects.get(serial_number="F75A00802")
        self.assertTrue(Reading.objects.filter(meter=meter, value=56311.0).exists())
        self.assertEqual(Reading.objects.get(meter=meter).meter_register_id, "123")
        
        os.unlink(temp_file.name)

    @patch("builtins.open", new_callable=mock_open, read_data="026|1200023305967|V|\n028| F75A\t00802 |\n030|123|20160222000000|56311.0|\n")
    def test_file_already_processed(self, mock_file):
        """Test that the command skips a file that has already been processed."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".uff")
        temp_file.write(self.valid_file_content.encode('utf-8'))
        temp_file.close()

        call_command('import_d0010', temp_file.name)

        call_command('import_d0010', temp_file.name)
        self.assertEqual(Reading.objects.count(), 1)

        os.unlink(temp_file.name)

    @patch("builtins.open", new_callable=mock_open, read_data="026|1200023305967|V|\n028| F75A\t00802 |\n030|123|InvalidDate|56311.0|\n")
    def test_invalid_date_in_file(self, mock_file):
        """Test that the command skips rows with invalid dates."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".uff")
        temp_file.write(self.invalid_file_content.encode('utf-8'))
        temp_file.close()

        call_command('import_d0010', temp_file.name)

        self.assertFalse(Reading.objects.exists())

        os.unlink(temp_file.name)

    @patch("builtins.open", new_callable=mock_open, read_data="026|1200023305967|V|\n028| F75A\t00802 |\n030|123|20160222000000|56311.0|\n")
    def test_processing_directory(self, mock_file):
        """Test processing all files in a directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file1 = tempfile.NamedTemporaryFile(delete=False, suffix=".uff", dir=temp_dir)
            temp_file2 = tempfile.NamedTemporaryFile(delete=False, suffix=".uff", dir=temp_dir)
            temp_file1.write(self.valid_file_content.encode('utf-8'))
            temp_file2.write(self.valid_file_content.encode('utf-8'))
            temp_file1.close()
            temp_file2.close()

            call_command('import_d0010', temp_dir)

            self.assertEqual(Reading.objects.count(), 2)
            self.assertEqual(ProcessedFile.objects.count(), 2)

