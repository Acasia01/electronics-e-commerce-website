from django.shortcuts import render,redirect
from userauths.forms import Register_form,Login_form
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
from django.conf import settings

User = settings.AUTH_USER_MODEL

# Create your views here.d

def register_page(request):
     
    print("Method:", request.method)
    
    if request.method == "POST":
        form = Register_form(request.POST or None)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"{username}Your account is created")
            new_user = authenticate(username=form.cleaned_data['email'],
                                    password = form.cleaned_data['password1']
            )
            login(request , new_user)
            return redirect("core:index")
    else:
        print("user cannot be registered")
        form = Register_form()
        
    context = {
        'form':form,
    }
    return render(request, "userauths/register_page.html",context)


def login_page(request):
    if request.user.is_authenticated:
        return redirect("core:index")
    
    form = Login_form(request.POST or None)
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")  
        
        user = authenticate(request, email = email, password=password) 
        
        if user is not None:
            login(request, user)
            messages.success(request,"You are logged in ")
            return redirect("core:index")
        else:
            if User.objects.filter(email=email).exists():
                messages.error(request, "Invalid password. Please try again.")
            else:
                messages.success(request,"User with {email} does not exist. Create an account")
    
    context = {
        "form":form,
    }
    
    return render(request, "userauths/login_page.html",context)

def logout_page(request):
    print("Logout view called")
    logout(request)
    messages.success(request, "You are successfully logged out")
    return redirect("userauths:login_page")