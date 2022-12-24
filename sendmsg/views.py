from django.shortcuts import render
from django.http import HttpResponse
from .forms import MessageForm
from .models import Message
from django.utils import timezone
import requests
import environ
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Create your views here.
def messageform(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            try:
                r = requests.post(env('POSTURL'), json={'message': message}, timeout=40)
            except requests.exceptions.ConnectionError:
                msg = Message(message=message, send_date=timezone.now(), is_sent=False)
                msg.save()
                errors = []
                errors.append('Connection Error, please try again later.')
                return render(request, 'sendmsg/messageform.html', {'form': form, 'errors': errors})
            except requests.exceptions.Timeout:
                msg = Message(message=message, send_date=timezone.now(), is_sent=False)
                msg.save()
                errors = []
                errors.append('Timeout Error, please try again later.')
                return render(request, 'sendmsg/messageform.html', {'form': form, 'errors': errors})
            else:
                if(r.status_code):
                    msg = Message(message=message, send_date=timezone.now(), is_sent=True)
                    msg.save()
                    return render(request, 'sendmsg/messageform.html', {'form': form, 'success': True})
                else:
                    msg = Message(message=message, send_date=timezone.now(), is_sent=False)
                    msg.save()
                    errors = []
                    errors.append('Something went wrong, please try again later.')
                    return render(request, 'sendmsg/messageform.html', {'form': form, 'errors': errors})
        else:
            return render(request, 'sendmsg/messageform.html', {'form': form, 'errors' : form.errors})
    else:
        form = MessageForm()

    return render(request, 'sendmsg/messageform.html', {'form': form})

def index(request):
    return render(request, 'sendmsg/index.html')

def history(request):
    messages = Message.objects.all().order_by('-send_date')
    
    if request.method == 'GET':
        return render(request, 'sendmsg/history.html', {'messages': messages})
    elif request.method == 'POST':
        if 'delete' in request.POST:
            try:
                Message.objects.get(id=request.POST['id']).delete()
                return render(request, 'sendmsg/history.html', {'messages': messages, 'success': True})
            except:
                errors = []
                errors.append('Something went wrong, please try again later.')
                return render(request, 'sendmsg/history.html', {'messages': messages, 'errors': errors})
        elif 'resend' in request.POST:
            message = Message.objects.get(id=request.POST['id'])
            try:
                r = requests.post(env('POSTURL'), json={'message': message.message}, timeout=40)
            except requests.exceptions.ConnectionError:
                errors = []
                errors.append('Connection Error, please try again later.')
                return render(request, 'sendmsg/history.html', {'messages': messages, 'errors': errors})
            except requests.exceptions.Timeout:
                errors = []
                errors.append('Timeout Error, please try again later.')
                return render(request, 'sendmsg/history.html', {'messages': messages, 'errors': errors})
            else:
                if(r.status_code):
                    message.send_date = timezone.now()
                    message.is_sent = True
                    message.save()
                    return render(request, 'sendmsg/history.html', {'messages': messages, 'success': True})
                else:
                    errors = []
                    errors.append('Something went wrong, please try again later.')
                    return render(request, 'sendmsg/history.html', {'messages': messages, 'errors': errors})
    else:
        return HttpResponse('Method not allowed')
