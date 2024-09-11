# D0010 Meter Reading Importer

This Django project is designed to import meter readings from D0010 files (energy industry standard files) and store the readings in a database. It provides functionality to process individual files or entire directories of files. The project also includes an admin interface to view and manage the meter points, meters, and readings.

## Features

- Import meter readings from D0010 files (pipe-delimited text files).
- Handle multiple files or directories of files.
- Skip files that have already been processed to avoid duplicate imports.
- Track processed files in the database.
- Django admin interface to view and manage imported meter readings and processed files.
- Unit tests to ensure the functionality of the import process.

## Prerequisites

- Python 3.10+
- Django 3.2+ (compatible with later versions as well)
- SQLite (default) or PostgreSQL for database

## Installation

1. **Unarchive the project**:

  If you received the project as a gzipped tarball, extract the project into a directory using the following command:

   ```bash
   tar -xzvf mihail_andritchi_meter_reader.tar.gz
   cd meter_reader
   ```

2. **Create a virtual environment**:

   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

3. **Install the required dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations** to set up the database:

   ```bash
   python manage.py migrate
   ```

5. **Create a superuser** to access the Django admin:

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**:

   ```bash
   python manage.py runserver
   ```

## Usage

### Importing Meter Readings

You can import meter readings from a D0010 file or directory containing multiple D0010 files. Use the `import_d0010` management command to process the files.

1. **Import a Single File**:

   ```bash
   python manage.py import_d0010 ./d0010_files/DTC5259515123502080915D0010.uff
   ```

2. **Import All Files in a Directory**:

   ```bash
   python manage.py import_d0010 ./d0010_files/
   ```

   - The command will skip files that have already been processed.
   - The system expects valid D0010 files where `026` lines contain meter serial numbers and `030` lines contain the meter readings and dates.

### Django Admin

Once the data is imported, you can view and manage it through the Django admin interface:

1. Start the development server:

   ```bash
   python3 manage.py runserver
   ```

2. Access the admin site at [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) and log in with your superuser account.

   - **MeterPoint**: View all meter points (identified by MPAN).
   - **Meter**: View individual meters and associated readings.
   - **Reading**: View and search for meter readings by date and meter.
   - **ProcessedFile**: View files that have already been processed.

## Running Unit Tests

The project includes a set of unit tests to ensure the import functionality works as expected. To run the tests, use the following command:

```bash
python manage.py test meter_readings.tests
```

- Tests cover file import, directory import, invalid data handling, and skipping of already processed files.

## Models

### MeterPoint

- **mpan**: The unique identifier for the meter point.

### Meter

- **serial_number**: The serial number of the physical meter.
- **meter_point**: ForeignKey to the `MeterPoint`.

### Reading

- **meter**: ForeignKey to the `Meter`.
- **value**: The cumulative meter reading value.
- **reading_date**: The timestamp of the reading.
- **file_name**: The D0010 file from which the reading was imported.

### ProcessedFile

- **file_name**: The name of the file that was processed.
- **processed_at**: The date and time when the file was processed.

---

## Assumptions and Suggestions for Improvement

### Assumptions Made During Development

1. **Reading Value Format**:
   - It is assumed that the reading values in the `030` lines are valid decimal numbers. Rows with invalid or non-decimal values (like text) are skipped.

2. **Date Format in D0010 Files**:
   - The date in `030` lines is expected to be in the format `YYYYMMDDHHMMSS`. If this format is not adhered to, the row is skipped.
   - No attempt is made to parse other date formats.

3. **Handling of Metadata in `028` Lines**:
   - The metadata in the `028` lines is currently ignored since it is not critical to the core functionality of importing meter readings. If needed, the parsing of `028` lines can be enhanced later.

4. **File Extensions**:
   - The command processes files with the `.uff` extension. Other extensions are not processed unless manually specified in the code.

### Suggestions for Future Improvements

1. **Enhanced Error Logging**:
   - Currently, invalid rows are skipped, and warnings are printed to the console. It would be helpful to log these warnings in a log file for better debugging and tracking of errors during the import process.

2. **Support for Additional File Formats**:
   - Currently, only `.uff` files are processed. Support for other file formats (e.g., `.txt`, `.csv`) could be added based on the file content or extension.

3. **Better Metadata Handling**:
   - The `028` lines, which contain metadata, are ignored in the current implementation. Adding logic to capture and store this metadata could enhance reporting and analysis.

4. **Automated File Ingestion**:
   - Instead of manually running the import command, the project could be extended to automatically monitor a directory and import new files as they become available (e.g., using Django Background Tasks or Celery).

5. **Improved Date Parsing**:
   - While the current implementation expects a specific date format (`YYYYMMDDHHMMSS`), it could be enhanced to handle a wider range of date formats, including adding a fallback for partial dates (e.g., just `YYYYMMDD`).

6. **File Validation**:
   - Add validation to ensure the D0010 file follows the expected structure before processing it. This would prevent incomplete or incorrectly formatted files from being imported.

7. **REST API for File Upload**:
   - Implement a REST API that allows files to be uploaded and processed via HTTP requests. This would allow for easier integration with other systems or user interfaces.

8. **Historical Data and Archiving**:
   - Add functionality to archive processed files or move them to a "processed" directory after successful processing. This would keep the incoming file directory clean and organized.
