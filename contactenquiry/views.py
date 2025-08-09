from django.shortcuts import render,redirect
from django.core.mail import send_mail
from contactenquiry.models import contactEnquiry
from . import views
from .forms import ContactForm
from django.template.loader import render_to_string
# Create your views here.

def contact(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        
        if form.is_valid():
            print('The form is valid')
            
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            contact = contactEnquiry(name=name,email=email,subject=subject,message=message)
            contact.save()  
            
            html = render_to_string('emails/contactForm.html', {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message
            })
            
            send_mail('The contact form subject',message,'xenobaka2@gmail.com',[email],html_message=html)
            
            return redirect('contact')
        else:
            form = ContactForm()
        
    return render(request,'contactenquiry/contact.html', {
        'form':form
    })
    