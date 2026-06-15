from django.contrib import admin
from .models import Student, certificate
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import StudentUploadForm
import pandas as pd
from django import forms
# Register your models here.

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'matric_number', 'email', 'phone_number', 'faculty', 'department', 'year_of_graduation','graduation_date')
    search_fields = ('full_name', 'matric_number', 'email', 'department', 'faculty','year_of_graduation',)
    list_filter = ('faculty', 'department', 'year_of_graduation')

     # Custom admin page
    change_list_template = "admin/student_changelist.html"

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "upload-students/",
                self.admin_site.admin_view(self.upload_students),
                name="upload_students",
            ),
        ]

        return custom_urls + urls

   # To upload bulk student data
    
    def upload_students(self, request):

        if request.method == "POST":

            form = StudentUploadForm(
                request.POST,
                request.FILES
            )

            if form.is_valid():

                uploaded_file = request.FILES["file"]

                try:

                    # Read uploaded file
                    if uploaded_file.name.endswith(".csv"):
                        df = pd.read_csv(uploaded_file)

                    elif uploaded_file.name.endswith(".xlsx"):
                        df = pd.read_excel(uploaded_file)

                    else:
                        messages.error(
                            request,
                            "Please upload a CSV or Excel file."
                        )
                        return redirect(request.path)

                    # Normalize column names
                    df.columns = (
                        df.columns
                        .str.strip()
                        .str.lower()
                    )

                    # Required columns
                    required_columns = [
                        "full_name",
                        "matric_number",
                        "email",
                        "phone_number",
                        "date_of_birth",
                        "faculty",
                        "department",
                        "year_of_graduation",
                        "graduation_date",
                    ]

                    missing_columns = [
                        col
                        for col in required_columns
                        if col not in df.columns
                    ]

                    if missing_columns:
                        messages.error(
                            request,
                            f"Missing columns: {', '.join(missing_columns)}"
                        )
                        return redirect(request.path)

                    created_count = 0
                    duplicate_count = 0

                    for _, row in df.iterrows():

                        student, created = Student.objects.get_or_create(
                            matric_number=str(
                                row["matric_number"]
                            ).strip().upper(),

                            defaults={
                                "full_name": str(
                                    row["full_name"]
                                ).strip(),

                                "email": str(
                                    row["email"]
                                ).strip(),

                                "phone_number": str(
                                    row["phone_number"]
                                ).strip(),

                                "date_of_birth": row[
                                    "date_of_birth"
                                ],

                                "faculty": str(
                                    row["faculty"]
                                ).strip(),

                                "department": str(
                                    row["department"]
                                ).strip(),

                                "year_of_graduation": int(
                                    row["year_of_graduation"]
                                ),

                                "graduation_date": row[
                                    "graduation_date"
                                ],
                            }
                        )

                        if created:
                            created_count += 1
                        else:
                            duplicate_count += 1

                    messages.success(
                        request,
                        f"{created_count} student(s) added successfully. "
                        f"{duplicate_count} duplicate(s) skipped."
                    )

                    return redirect("../")

                except Exception as e:

                    messages.error(
                        request,
                        f"Error: {str(e)}"
                    )

        else:
            form = StudentUploadForm()

        return render(
            request,
            "admin/upload_students.html",
            {
                "form": form
            }
        )
    

class CertificateAdminForm(forms.ModelForm):

    class Meta:
        model = certificate
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only students without certificates
        self.fields["student"].queryset = Student.objects.filter(
            certificate__isnull=True
        )
    
@admin.register(certificate)
class CertificateAdmin(admin.ModelAdmin):
    exclude = ('course_name',)  # course_name is auto-set from student's department
    form = CertificateAdminForm
    list_display = ('student', 'certificate_type', 'classification', 'certificate_id', 'created_at','qr_code_preview','view_certificate_link')
    search_fields = ('student__full_name', 'student__matric_number', 'certificate_id')
    list_filter = ('certificate_type', 'classification')
    readonly_fields= ('certificate_id', 'verification_token', 'digital_signature', 'qr_code_preview','certificate_file')
    
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