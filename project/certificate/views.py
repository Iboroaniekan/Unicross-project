from django.shortcuts import render,get_object_or_404
from django.template.loader import render_to_string
from .models import certificate
from django.http import HttpResponse
from weasyprint import HTML   #type :ignore
from django.conf import settings
import hashlib
import os
# Create your views here.
#Function to View Certificate
def view_certificate(request, cert_id):
    Certificate = get_object_or_404(certificate, certificate_id=cert_id)
    return render(request, 'certificate.html', {'Certificate': Certificate})

#Function to download certificate
def download_certificate(request, cert_id):
    Certificate = get_object_or_404( certificate,certificate_id=cert_id )
    #Fonts path
    great_vibes_font = os.path.join(settings.BASE_DIR,"static", "fonts", "GreatVibes-Regular.ttf" ).replace("\\", "/")
    cinzel_font = os.path.join(settings.BASE_DIR,"static", "fonts","Cinzel-Bold.ttf" ).replace("\\", "/")
    playfair_font = os.path.join(settings.BASE_DIR,"static", "fonts", "PlayfairDisplay-Bold.ttf").replace("\\", "/")
    playfair_italic_font = os.path.join(settings.BASE_DIR,"static", "fonts","PlayfairDisplay-BoldItalic.ttf").replace("\\", "/")
            #Logo path
    logo_path= os.path.join(settings.BASE_DIR,"static","images","crutech-logo.png").replace("\\", "/")
            # QR code path
    qr_path = None
    if Certificate.qr_code:
        qr_path = Certificate.qr_code.path.replace("\\", "/")

    html = render_to_string("certificate_pdf.html",
    {"Certificate": Certificate,
    "logo_path":logo_path,
    "qr_path":qr_path,
    "great_vibes_font": great_vibes_font,
    "cinzel_font": cinzel_font,
    "playfair_font": playfair_font,
    "playfair_italic_font": playfair_italic_font,
    } )

    pdf = HTML(string=html,base_url=settings.BASE_DIR).write_pdf()

    response = HttpResponse( pdf,content_type="application/pdf")

    response["Content-Disposition"] = (f'attachment; filename="{Certificate.student.full_name}.pdf"')
        
    return response

#Function to Verify certificate
def verify_certificate(request):
    Certificate = None  # Will store verification outcome
    status = None

    if request.method == 'POST':
        query = request.POST.get('cert_id')  # Get input value directly
        if query:
            try:
                Certificate = certificate.objects.get(certificate_id=query)
            except certificate.DoesNotExist:
                try:
                        Certificate = certificate.objects.get(student__matric_number=query)
                except certificate.DoesNotExist:
                    Certificate = None  # invalid certificate

            if Certificate:
                # Recompute SHA-256 digital signature to verify authenticity
                data = f"{Certificate.student.full_name}{Certificate.student.matric_number}{Certificate.course_name}{Certificate.date_of_issue}{settings.SECRET_KEY}"
                recomputed_hash = hashlib.sha256(data.encode()).hexdigest()

                if recomputed_hash == Certificate.digital_signature:
                    status = "valid"
                else:
                    status = "tampered"
            else:
                status = "invalid"

    return render(request, 'index.html', {
        'Certificate': Certificate,
        'status': status
    })


#Function to Verify QR_CODE
def verify_qr(request, cert_id):
    """
    QR code verification: validate certificate using certificate_id and token from URL
    """
    token = request.GET.get('token', None)
    result = None
    status = None

    if cert_id and token:
        try:
            result = certificate.objects.get(certificate_id=cert_id, verification_token=token)
            
            # Recompute digital signature
            recomputed_signature = hashlib.sha256(
                f"{result.student.full_name}{result.student.matric_number}"
                f"{result.course_name}{result.date_of_issue}{settings.SECRET_KEY}".encode('utf-8')
            ).hexdigest()

            if recomputed_signature == result.digital_signature:
                status = "valid"
            else:
                status = "invalid"
        except certificate.DoesNotExist:
            result = None
            status = "not_found"
    else:
        status = "not_found"

    return render(request, 'verify.html', {'result': result, 'status': status})