from django.db import models
from django.contrib.auth.models import User
import uuid
import hashlib
import qrcode
from io import BytesIO
from django.conf import settings
from django.core.files import File

# Create your models here.
def upload_path(instance, kind, filename):
    ref = instance.certificate_id or ("TMP-" + uuid.uuid4().hex[:8].upper())
    return f"certificates/{ref}/{kind}/{filename}"

def qr_upload_path(instance, filename):
    return upload_path(instance, "qr", filename)

class Student(models.Model):
    full_name = models.CharField(max_length=200)
    matric_number = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    faculty = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    year_of_graduation = models.PositiveIntegerField()
    graduation_date = models.DateField() 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.matric_number})"
    

class certificate(models.Model):
    CERT_TYPE_CHOICES =[
        ('B.Sc.', 'Bachelor of Science'),
        ('B.A', 'Bachelor of Arts'),
        ('M.Sc', 'Master of Science'),
        ('M.A', 'Master of Arts'),
        ('PhD', 'Doctor of Philosophy'),
        ('PGD', 'Post Graduate Diploma'),
        ('HND', 'higher National Diploma'),
        ('OND ', 'Ordinary National Diploma'),
    ]

    CLASSIFICATION_CHOICES = [
        ('First Class Honours', 'First Class Honours'),
        ('Second Class Hons. Upper Division', 'Second Class Hons. Upper Division'),
        ('Second Class Hons. Lower Division', 'Second Class Hons. Lower Division'),
        ('Third Class', 'Third Class'),
        ('Pass', 'Pass'),
    ]

    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    certificate_id = models.CharField(max_length=30, unique=True, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='certificates')
    certificate_type = models.CharField(max_length=50, choices=CERT_TYPE_CHOICES, default='B.Sc.')
    classification = models.CharField(max_length=50, choices=CLASSIFICATION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    course_name = models.CharField(max_length=200)
      # 🔐 SECURITY FIELDS
    verification_token = models.CharField(max_length=64, blank=True, editable=False)
    digital_signature = models.CharField(max_length=64, blank=True, editable=False)
    qr_code = models.ImageField(upload_to=qr_upload_path, blank=True, null=True, editable=False)
    date_of_issue = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['date_of_issue']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.certificate_type} - {self.classification}"
    

    # 🔐 DIGITAL SIGNATURE (tamper-proof)
    def generate_signature(self):
        data = f"{self.student.full_name}{self.student.matric_number}{self.course_name}{self.date_of_issue}{settings.SECRET_KEY}"
        self.digital_signature = hashlib.sha256(data.encode("utf-8")).hexdigest()
        return self.digital_signature
    # 🔐 VERIFICATION TOKEN
    def generate_verification_token(self):
        if not self.verification_token:
            raw_string = f"{self.certificate_id}{uuid.uuid4()}{settings.SECRET_KEY}"
            self.verification_token = hashlib.sha256(raw_string.encode()).hexdigest()
        return self.verification_token
    
     # 📱 QR CODE
    def generate_qr_code(self):
        if not self.certificate_id or not self.verification_token:
            return

        if self.qr_code:
            return

        verification_url = f"{settings.SITE_URL}/verify/{self.certificate_id}/?token={self.verification_token}"
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(verification_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="transparent")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        filename = f"QR-{self.certificate_id}.png"
        self.qr_code.save(filename, File(buffer), save=False)

    def save(self, *args, **kwargs):
        if not self.certificate_id:
            self.certificate_id = f"CERT-{uuid.uuid4().hex[:8].upper()}"  
        self.generate_verification_token()
        self.generate_signature()
        self.generate_qr_code()
        super().save(*args, **kwargs)