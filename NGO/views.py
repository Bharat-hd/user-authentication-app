from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from .forms import CustomRegistrationForm, PostForm
from .models import Post, EmailVerificationToken
import datetime

def register(request):
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.is_active = False  # Inactive until email verified
            user.save()
            
            # Assign role
            role = form.cleaned_data['role']
            group = Group.objects.get_or_create(name=role.capitalize())[0]
            user.groups.add(group)
            
            # Generate verification token
            token = get_random_string(32)
            expires_at = timezone.now() + datetime.timedelta(hours=24)
            EmailVerificationToken.objects.create(user=user, token=token, expires_at=expires_at)
            
            # Send verification email
            verification_link = request.build_absolute_uri(f'/verify-email/{token}/')
            send_mail(
                'Verify Your Email',
                f'Click the link to verify your email: {verification_link}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return render(request, 'NGO/register_success.html')
    else:
        form = CustomRegistrationForm()
    return render(request, 'NGO/register.html', {'form': form})

def verify_email(request, token):
    try:
        verification_token = EmailVerificationToken.objects.get(token=token)
        if verification_token.is_expired():
            return render(request, 'NGO/verify_failed.html', {'error': 'Token expired'})
        user = verification_token.user
        user.is_active = True
        user.save()
        verification_token.delete()
        login(request, user)
        return redirect('dashboard')
    except EmailVerificationToken.DoesNotExist:
        return render(request, 'NGO/verify_failed.html', {'error': 'Invalid token'})

def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                return render(request, 'NGO/login.html', {'error': 'Invalid credentials'})
        except User.DoesNotExist:
            return render(request, 'NGO/login.html', {'error': 'Email not registered'})
    return render(request, 'NGO/login.html')

@login_required
def dashboard(request):
    posts = Post.objects.all().order_by('-created_at') if request.user.groups.filter(name='Admin').exists() else Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'NGO/dashboard.html', {'posts': posts})

@login_required
def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'NGO/post_list.html', {'posts': posts})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('dashboard')
    else:
        form = PostForm()
    return render(request, 'NGO/post_create.html', {'form': form})

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'NGO/post_detail.html', {'post': post})

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')