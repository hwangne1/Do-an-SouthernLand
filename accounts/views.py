from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User
from contacts.models import Contact
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from accounts.models import Favorite
from listings.models import Listing
# Create your views here.
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    else:
        return render(request, 'accounts/login.html')


def register(request):
    if request.method == 'POST':
        # Get form values
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        # Check if passwords match
        if password == password2:
            # Check username
            if User.objects.filter(username=username).exists():
                messages.error(request,'The username is already taken')
                return redirect('register')
            else:
            # Check email
                if User.objects.filter(email=email).exists():
                    messages.error(request,'The email is already taken')
                    return redirect('register')
                else:
                    #Looks good
                    user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
                    # Login after register
                    # auth.login(request, user)
                    # messages.success(request, 'You are now logged in')
                    # return redirect('index')
                    user.save()
                    messages.success(request, 'You are now registered and can log in')
                    return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('accounts/register.html')
    else:
        return render(request,'accounts/register.html')


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, 'You are now logged out')
        return redirect('index')

def dashboard(request):
    user_contacts = Contact.objects.order_by('-contact_date').filter(user_id=request.user.id)

    context = {
        'contacts': user_contacts
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def toggle_favorite(request, listing_id):
    if request.method != 'POST':
        return redirect('listings')

    listing = get_object_or_404(
        Listing,
        id=listing_id,
        is_published=True
    )

    favorite = Favorite.objects.filter(
        user=request.user,
        listing=listing
    )

    if favorite.exists():
        favorite.delete()
        messages.success(request, 'Đã bỏ bất động sản khỏi danh sách yêu thích.')
    else:
        Favorite.objects.create(
            user=request.user,
            listing=listing
        )
        messages.success(request, 'Đã thêm bất động sản vào danh sách yêu thích.')

    return redirect(request.META.get('HTTP_REFERER', '/listings/'))
def dashboard(request):
    # Lấy danh sách liên hệ
    contacts = Contact.objects.filter(user_id=request.user.id)
    
    # LẤY DANH SÁCH YÊU THÍCH
    favorites = Favorite.objects.filter(user=request.user).select_related('listing')

    context = {
        'contacts': contacts,
        'favorites': favorites, # Truyền ra template
    }
    return render(request, 'accounts/dashboard.html', context)