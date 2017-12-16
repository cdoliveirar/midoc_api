from django.template import loader
from django.core.mail.message import EmailMessage
from midoc.celery import app
from django.conf import settings


@app.task(name='welcome')
def welcome(email, name):
    data = {"name": name}
    template = loader.get_template('bienvenido.html')
    html = template.render(data)
    subject_user, from_email = 'Midoc Virtual - Bienvenido', 'midoc.virtual@gmail.com'
    message_user = EmailMessage(subject_user, html, from_email, [email])
    message_user.content_subtype = "html"
    message_user.send(fail_silently=True)

@app.task(name='family_plan_mail')
def family_plan_mail(email, first_name, last_name):
    data = {'first_name':first_name,'last_name': last_name}
    template = loader.get_template('planfamiliar.html')
    html = template.render(data)
    subject_user, from_email = 'family-plan', 'midoc.virtual@gmail.com'
    message_user = EmailMessage(subject_user, html, from_email,
                                ['erikd.guiba@gmail.com','cdoliveirar@gmail.com'])
    message_user.content_subtype = "html"
    message_user.send(fail_silently=True)


@app.task(name='personal_plan')
def personal_plan(email, first_name, last_name):
    data = {'first_name':first_name,'last_name': last_name}
    template = loader.get_template('planpersonal.html')
    html = template.render(data)
    subject_user, from_email = 'Midoc Virtual - Pago Realizado', 'midoc.virtual@gmail.com'
    message_user = EmailMessage(subject_user, html, from_email, [email])
    message_user.content_subtype = "html"
    message_user.send(fail_silently=True)


@app.task(name='recommendation')
def recommendation():
    data = {}
    template = loader.get_template('recommendation.html')
    html = template.render(data)
    subject_user, from_email = 'family-plan', 'midoc.virtual@gmail.com'
    message_user = EmailMessage(subject_user, html, from_email,
                                ['erikd.guiba@gmail.com','cdoliveirar@gmail.com'])
    message_user.content_subtype = "html"
    message_user.send(fail_silently=True)


@app.task(name='recovery')
def recovery(email, code):
    data = {"email": email, "code": code}
    template = loader.get_template('recuperar.html')
    html = template.render(data)
    subject_user, from_email = 'Recuperacion de Acceso', 'midoc.virtual@gmail.com'
    message_user = EmailMessage(subject_user, html, from_email,
                                [email])
    message_user.content_subtype = "html"
    message_user.send(fail_silently=True)



