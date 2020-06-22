from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login,logout,authenticate
from .forms import TodoCreationForm
from .models import todoslist
from django.utils import timezone
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request,'todo/home.html')

def usersignup(request):
    if request.method  == 'GET':
        return render(request,'todo/signup.html',{'form':UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'] , password = request.POST['password1'])
                user.save()
                login(request , user)
                return redirect('current')

            except IntegrityError:
                return render(request,'todo/signup.html',{'form':UserCreationForm(),'error':'The user name has already been taken!'})

        else:
            return render(request,'todo/signup.html',{'form':UserCreationForm(),'error':'The Passwords did not match'})

def loginuser(request):
    if request.method  == 'GET':
        return render(request,'todo/loginuser.html',{'form':AuthenticationForm()})
    else:
        user = authenticate(request,username = request.POST['username'] , password = request.POST['password'])
        if user is None:
            return render(request,'todo/loginuser.html',{'form':AuthenticationForm(),'error':'The username and passwords dont match'})
        else:
            login(request , user)
            return redirect('current')

@login_required
def current(request):
    todos = todoslist.objects.filter(user = request.user,datecompleted__isnull=True)
    if len(todos) == 0:
        return render(request,'todo/current.html',{'todos':todos,'error':'Looks like you dont have any current todos yet !'})
    else:
        return render(request,'todo/current.html',{'todos':todos})


@login_required
def viewtodo(request,todo_pk):
    todo = get_object_or_404(todoslist,pk = todo_pk,user = request.user)
    if request.method  == 'GET':
        form = TodoCreationForm(instance = todo)
        return render(request,'todo/viewtodo.html',{'todo':todo,'form':form})
    else:
        try:
            form = TodoCreationForm(request.POST,instance = todo)
            form.save()
            return redirect('current')
        except ValueError:
            return render(request,'todo/viewtodo.html',{'todo':todo,'form':form,'error':'Bad data Input !'})

@login_required
def createtodoview(request):
    if request.method  == 'GET':
        return render(request,'todo/createtodo.html',{'form':TodoCreationForm()})
    else:
        try:
            form = TodoCreationForm(request.POST)
            newtodo = form.save(commit = False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('current')
        except ValueError:
            return render(request,'todo/createtodo.html',{'form':TodoCreationForm(),'error':'Invalid data passed in . Try again .'})

@login_required
def complete(request,todo_pk):
    todo = get_object_or_404(todoslist,pk = todo_pk,user = request.user)
    if request.method  == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('current')

@login_required
def deletetodo(request,todo_pk):
    todo = get_object_or_404(todoslist,pk = todo_pk,user = request.user)
    if request.method  == 'POST':
        todo.delete()
        return redirect('current')

@login_required
def completedtodos(request):
    todos = todoslist.objects.filter(user = request.user,datecompleted__isnull = False)
    return render(request,'todo/completedtodos.html',{'todos':todos})

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
