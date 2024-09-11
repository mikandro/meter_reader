from django.contrib import admin
from .models import MeterPoint, Meter, Reading, ProcessedFile

@admin.register(MeterPoint)
class MeterPointAdmin(admin.ModelAdmin):
    search_fields = ['mpan']

@admin.register(Meter)
class MeterAdmin(admin.ModelAdmin):
    search_fields = ['serial_number', 'meter_point__mpan']
    list_display = ['serial_number', 'meter_point']

@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    search_fields = ['meter__serial_number', 'meter__meter_point__mpan']
    list_display = ['meter', 'value', 'reading_date', 'file_name']
    list_filter = ['reading_date', 'meter__meter_point__mpan']

@admin.register(ProcessedFile)
class ProcessedFileAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'processed_at']
    search_fields = ['file_name']
    readonly_fields = ['processed_at']

