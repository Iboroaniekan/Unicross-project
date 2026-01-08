from django.shortcuts import render,get_object_or_404
from .models import certificate
from django.http import HttpResponse
from weasyprint import HTML

# Create your views here.

def view_certificate(request, cert_id):
    Certificate = get_object_or_404(certificate, certificate_id=cert_id)
    return render(request, 'certificate.html', {'Certificate': Certificate})


def download_certificate(request, cert_id):
    Certificate = get_object_or_404(certificate, certificate_id=cert_id)
    
    # Render HTML template
    html_string = render(request, 'certificate.html', {'Certificate': Certificate}).content.decode('utf-8')
    # Generate PDF using WeasyPrint
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    # Return as PDF response
           # Send PDF as download
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{Certificate.student.full_name}_certificate.pdf"'
    return response
def verify_certificate(request):
    result = None  # Will store verification outcome

    if request.method == 'POST':
        query = request.POST.get('cert_id')  # Get input value directly
        if query:
            try:
                result = certificate.objects.get(certificate_id=query)
            except certificate.DoesNotExist:
                try:
                        result = certificate.objects.get(student__matric_number=query)
                except certificate.DoesNotExist:
                        result = False  # invalid certificate

    # Render index.html with result to display in your verification section
    return render(request, 'index.html', {'result': result})