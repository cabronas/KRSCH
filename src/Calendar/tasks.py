# from datetime import time
import time

from django.core.mail import send_mail

from .models import Event

from celery import shared_task


@shared_task(serializer='json', name="send_mail")
def send_email_cel(subject, message, sender, receiver):
    time.sleep(1)  # for check that sending email process runs in background
    send_mail(subject, message, sender, ['cabronas.max@mail.ru'])
