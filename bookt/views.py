from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Product, Category, Profile
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django import forms
from .forms import SignUpForm,UpdateUserForm, ChangePasswordForm, UserInfoForms
import json
from cart.cart import Cart
from payment.forms import ShippingForm
from payment.models import ShippingAddress

def search(request):
    if request.method == 'POST':
        searched = request.POST.get('searched', '')
        searched = Product.objects.filter(name__icontains=searched)

        if not searched:
            messages.success(request, 'PRODUCT NOT FOUND')
        return render(request, 'bookt/search.html', {'searched': searched})
    return render(request, 'bookt/search.html', {})



def update_info(request):
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user__id=request.user.id)
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        form = UserInfoForms(request.POST or None, instance=current_user)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        if form.is_valid() or shipping_form.is_valid():
            form.save()
            shipping_form.save()
            messages.success(request, "Your Info Has Been Updated!")
            return redirect('bookt:home')
        else:
            return render(request, 'bookt/update_info.html', {"form": form, "shipping_form": shipping_form} )
    else:
        messages.success(request, "Oops There Was An Error!")
        return redirect('bookt:home')

def update_password(request):
        if request.user.is_authenticated:
            current_user = request.user
            if request.method == 'POST':
                form = ChangePasswordForm(current_user, request.POST)
                if form.is_valid():
                    form.save()
                    login(request, current_user)
                    messages.success(request, 'Password changed successfully.')
                    return redirect('bookt:home')
                else:
                    for error in list(form.errors.values()):
                        messages.error(request, error)
                        return redirect('bookt:update_password')
            else:
                form = ChangePasswordForm(request.user)
                return render(request, 'bookt/update_password.html', {'form': form})
        else:
            return redirect('bookt:login')  # Redirect unauthenticated users to login


def update_user(request):
    user_form = UpdateUserForm()
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)
        if user_form.is_valid():
            user_form.save()
            login(request,current_user)
            messages.success(request,"User Has Been Updated!")
            return redirect('bookt:home')
        else:
            return render(request,'bookt/update_user.html', {"user_form": user_form})
    else:
        messages.success(request,"Oops There Was An Error!")
        return redirect('bookt:home')

def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'bookt/category_summary.html', {'categories': categories})



def category(request,foo):
    foo = foo.replace("-", " ")
    try:
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'bookt/category.html', {'products': products,'category': category})
    except:
        messages.success(request, ("THAT CATEGORY DOESN'T EXIST "))
        return redirect("bookt:home")

def product_detail(request, pk):
    products = Product.objects.get(id=pk)
    return render(request, 'bookt/product.html', {'products': products})
def say_hello(request):
    products = Product.objects.all()
    return render(request, 'bookt/hello.html',{'products':products})
def about(request):
    return render(request, 'bookt/about.html',{})
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            current_user = Profile.objects.get(user__id=request.user.id)
            saved = current_user.old_cart
            if saved:
                converted = json.loads(saved)
                cart = Cart(request)
                for key,value in converted.items():
                     cart.db_add(product=key,quantity=value)





            messages.success(request, ("LOGGED IN SUCCESSFULLY....."))
            return redirect('bookt:home')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('bookt:login')
    else:
        return render(request, 'bookt/login.html',{} )
def logout_user(request):
    logout(request)
    messages.success(request, ("Logged Out Successfully"))
    return redirect('bookt:home')
def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request,(f"Welcome! {username} You Have Registered"))
            return redirect('bookt:update_info')
        else:
            messages.success(request, ("There Was a problem! "))
            return redirect('bookt:register')
    else:
        return render(request, 'bookt/register.html', {"form": form})


