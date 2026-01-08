from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.

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
    date_of_issue = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['date_of_issue']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.certificate_type} - {self.classification}"
    def save(self, *args, **kwargs):
        if not self.certificate_id:
            self.certificate_id = f"CERT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)