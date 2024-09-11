from django.db import models

class MeterPoint(models.Model):
    mpan = models.CharField(max_length=255, unique=True)  # MPAN as a unique identifier

    def __str__(self):
        return self.mpan


class Meter(models.Model):
    serial_number = models.CharField(max_length=255, unique=True)  # Serial number from 028 line
    meter_point = models.ForeignKey(MeterPoint, on_delete=models.CASCADE)  # Related to an MPAN

    def __str__(self):
        return f"{self.serial_number} ({self.meter_point.mpan})"


class Reading(models.Model):
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE)  # Linked to a specific meter
    value = models.DecimalField(max_digits=10, decimal_places=3)  # Reading value from 030 line
    reading_date = models.DateTimeField()
    meter_register_id = models.CharField(max_length=255) 
    file_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.meter} - {self.value} at {self.reading_date}"

class ProcessedFile(models.Model):
    file_name = models.CharField(max_length=255, unique=True)
    processed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_name} (Processed at: {self.processed_at})"
