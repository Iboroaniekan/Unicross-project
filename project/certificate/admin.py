from django.contrib import admin
from .models import Student, certificate
from django.utils.html import format_html
# Register your models here.

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'matric_number', 'email', 'phone_number', 'faculty', 'department', 'year_of_graduation','graduation_date')
    search_fields = ('full_name', 'matric_number', 'email', 'department', 'faculty','year_of_graduation',)
    list_filter = ('faculty', 'department', 'year_of_graduation')

@admin.register(certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('student', 'certificate_type', 'classification', 'certificate_id', 'created_at','qr_code_preview','view_certificate_link')
    search_fields = ('student__full_name', 'student__matric_number', 'certificate_id')
    list_filter = ('certificate_type', 'classification')
    readonly_fields= ('certificate_id', 'verification_token', 'digital_signature', 'qr_code_preview')
    
    # QR code preview
    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="30">', obj.qr_code.url)
        return "-"
    qr_code_preview.short_description = "QR Code"

     # Add a clickable link to view certificate
    def view_certificate_link(self, obj):
        return format_html(
            '<a href="/certificate/{}/" target="_blank">View Certificate</a>', obj.certificate_id
        )
    view_certificate_link.short_description = "Certificate Preview"