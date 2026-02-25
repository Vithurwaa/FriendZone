from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Profile, Connection, Activity, ActivityJoin


def home(request):
    return render(request, "home.html")


# ========================= REGISTER =========================

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        Profile.objects.get_or_create(user=user)

        login(request, user)
        return redirect("edit_profile")

    return render(request, "register.html")


# ========================= LOGIN =========================

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("discover")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")


# ========================= EDIT PROFILE =========================

@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        profile.bio = request.POST.get("bio")
        profile.age = request.POST.get("age")
        profile.gender = request.POST.get("gender")
        profile.city = request.POST.get("city")
        profile.interests = request.POST.get("interests")
        profile.save()

        return redirect("discover")

    return render(request, "edit_profile.html", {"profile": profile})


# ========================= DISCOVER PAGE =========================

@login_required
def discover(request):
    users = Profile.objects.exclude(user=request.user)
    activities = Activity.objects.all().order_by("-created_at")

    return render(request, "discover.html", {
        "users": users,
        "activities": activities
    })


# ========================= CREATE ACTIVITY =========================

@login_required
def create_activity(request):
    if request.method == "POST":
        Activity.objects.create(
            creator=request.user,
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            location=request.POST.get("location"),
            date=request.POST.get("date"),
            time=request.POST.get("time"),
        )
        return redirect("discover")

    return render(request, "create_activity.html")


# ========================= JOIN ACTIVITY =========================

@login_required
def join_activity(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)

    ActivityJoin.objects.get_or_create(
        user=request.user,
        activity=activity
    )

    return redirect("discover")


# ========================= CONNECTION SYSTEM =========================

@login_required
def send_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)

    if receiver == request.user:
        return redirect("discover")

    existing = Connection.objects.filter(
        sender=request.user,
        receiver=receiver
    ).exists() or Connection.objects.filter(
        sender=receiver,
        receiver=request.user
    ).exists()

    if not existing:
        Connection.objects.create(
            sender=request.user,
            receiver=receiver,
            status="pending"
        )

    return redirect("discover")


@login_required
def accept_request(request, request_id):
    connection = get_object_or_404(Connection, id=request_id)

    if connection.receiver == request.user:
        connection.status = "accepted"
        connection.save()

    return redirect("discover")


@login_required
def cancel_request(request, request_id):
    connection = get_object_or_404(Connection, id=request_id)

    if connection.sender == request.user and connection.status == "pending":
        connection.delete()

    return redirect("discover")


@login_required
def reject_request(request, request_id):
    connection = get_object_or_404(Connection, id=request_id)

    if connection.receiver == request.user:
        connection.delete()

    return redirect("discover")


# ========================= LOGOUT =========================

def logout_view(request):
    logout(request)
    return redirect("home")