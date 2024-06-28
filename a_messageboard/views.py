from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
import threading
from .models import *
from .forms import *
from .tasks import *

@login_required
def messageboard_view(request):
    messageboard = get_object_or_404(MessageBoard, id=1)
    form = MessageCreateForm()
    
    if request.method == 'POST':
        if request.user in messageboard.subscribers.all():
            form = MessageCreateForm(request.POST)
            if form.is_valid():
                message = form.save(commit=False)
                message.author = request.user
                message.messageboard = messageboard
                message.save()
                send_email(message)
                return redirect('messageboard')
        else:
            messages.warning(request, 'You need to be Subscribed!')
        return redirect('messageboard')
    
    context = {
        'messageboard': messageboard,
        'form' : form
    }
    return render(request, 'a_messageboard/index.html', context)

@login_required
def subscribe(request):
    messageboard = get_object_or_404(MessageBoard, id=1)
    
    if request.user not in messageboard.subscribers.all():
        messageboard.subscribers.add(request.user)
    else:
        messageboard.subscribers.remove(request.user)
    return redirect('messageboard')

def send_email(message):
    messageboard = message.messageboard
    subscribers = messageboard.subscribers.all()
    
    for subscriber in subscribers:
        if subscriber.email:  # Ensure the subscriber has an email
            subject = f'New Message from {message.author.profile.name}'
            body = f'{message.author.profile.name}: {message.body}\n\nRegards from\nMy Message Board'
            send_email_task.delay(subject, body, subscriber.email)
            
#             email_thread = threading.Thread(target=send_email_thread, args=(subject, body, subscriber))
#             email_thread.start()
            
# def send_email_thread(subject, body, subscriber):
#     email = EmailMessage(subject, body, to=[subscriber.email])
#     email.send()

def is_staff(user):
     return user.is_staff
 
@user_passes_test(is_staff)
def newsletter(request):
    return render(request, 'a_messageboard/newsletter.html')