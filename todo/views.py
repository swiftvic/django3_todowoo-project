from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone

def home(request):
    return render(request, 'todo/home.html')

def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form':UserCreationForm()})
    else:
        # Someone POSTed to the page
        # Create a new user if the passwords match
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                #Username taken, return page with error
                return render(request, 'todo/signupuser.html', {'form':UserCreationForm(), 'error':'Username taken'})
        else:
            #Passwords did not match
            return render(request, 'todo/signupuser.html', {'form':UserCreationForm(), 'error':'Passwords did not match.'})

def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form':AuthenticationForm()})
    else:
        # Someone POSTed to the page
        user = authenticate(username = request.POST['username'], password = request.POST['password'])
        if user is not None:
            # Backend authenticated user
            login(request, user)
            return redirect('currenttodos')
        else:
            # Not authenticated
            return render(request, 'todo/loginuser.html', {'form':AuthenticationForm(), 'error':'Username/Password does not match'} )

def logoutuser(request):
    if request.method == "POST":
        logout(request)
        return redirect('home')

def createtodo(request):
    if request.method == "GET":
        return render(request, 'todo/createtodo.html', {'form':TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False) # Do not save into DB yet, assign and create new object
            newtodo.user = request.user # Add the username to the Todo
            newtodo.save() # Now save entire form into DB
            return redirect('currenttodos')
        except ValueError:
            # If length of text sumbitted is more than Chars specified in models
            return render(request, 'todo/createtodo.html', {'form':TodoForm(), 'error':'Incorrect data passed in. Try again.'} )

def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'todo/currenttodos.html', {'todos':todos})

def viewtodo(request, todo_pk):
    # Assign todo as an object from Todo model, pk and user=the requested user
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    # If just displaying the data GET
    if request.method == "GET":
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', {'todo':todo, 'form':form})
    # If data is edited and POST is submitted
    else:
        try:
            # Assign form with the POSTed updates and update the pk record todo
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            # If length of text sumbitted is more than Chars specified in models
            return render(request, 'todo/viewtodo.html', {'todo':todo, 'form':form, 'error':'Incorrect data passed in. Try again.'} )

def completetodo(request, todo_pk):
    # Assign todo as an object from Todo model, pk and user=the requested user
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now() # Set the datecompleted in models to have a time
        todo.save()
        return redirect('currenttodos')