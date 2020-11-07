from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import RegisterForm, LoginForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Message
import sqlite3
import datetime

def index(request):
    return render(request,'messages/index.html')
    #return HttpResponse("Hello, my friend. You're at the mailbox index.")


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            User.objects.create(username=username, password=password)
            return redirect('/login')

    else:
        form = RegisterForm()
    return render(request, 'messages/register.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        #don't use get, otherwise django raises an exception if no user was found
        user = User.objects.filter(username=username, password=password).first()
        if user is not None:
            login(request, user)
            return redirect('/sendmail')

    form = LoginForm()
    return render(request, 'messages/login.html', {'form': form})

@login_required
def send_mail(request):
    if request.method == 'POST':
        target = User.objects.get(username=request.POST.get('to'))
        target_id = target.id
        source_id = request.user.id
        content = request.POST.get('content')
        #content = 'content");delete from auth_user; --'
        datetime_now = datetime.datetime.now()
        #Message.objects.create(source=request.user, target=target, content=request.POST.get('content'))
        conn = sqlite3.connect('./db.sqlite3')
        cursor = conn.cursor()
        query = 'INSERT INTO mailbox_message (source_id,target_id,time,content) values("%s","%s","%s","%s")'\
             % (source_id,target_id,datetime_now,content)
        print(query)
        cursor.executescript(query)
        conn.commit()
        return redirect('/sendmail')
    
    messages = Message.objects.filter(Q(source=request.user) | Q(target=request.user))
    users = User.objects.exclude(pk=request.user.id)
    return render(request, 'messages/mail.html', {'msgs': messages, 'users': users})

@login_required
def admin_view(request):
    users = User.objects.all()
    return render(request, 'messages/admin.html', {'users':users})

@login_required
def remove_user(request):
    remove_username = request.POST.get('remove')
    user = User.objects.get(username=remove_username)
    user.delete()
    return redirect('/admin')
