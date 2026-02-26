from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Profile, Connection, Activity, ActivityJoin, Interest, Post, Report
from django.utils import timezone
from datetime import datetime





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



# ========================= EDIT PROFILE =========================

@login_required
def edit_profile(request):
    profile = request.user.profile
    interests = Interest.objects.all()

    if request.method == "POST":
        profile.bio = request.POST.get("bio")
        profile.age = request.POST.get("age")
        profile.gender = request.POST.get("gender")
        profile.city = request.POST.get("city")
        profile.save()

        selected_interests = request.POST.getlist("interests")
        profile.interests.set(selected_interests)

        return redirect("discover")

    return render(request, "edit_profile.html", {
        "profile": profile,
        "interests": interests
    })
@login_required
def leave_activity(request, activity_id):
    ActivityJoin.objects.filter(
        user=request.user,
        activity_id=activity_id
    ).delete()

    return redirect("discover")

@login_required
def profile_view(request):
    profile = Profile.objects.get(user=request.user)
    posts = Post.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "profile.html", {
        "profile": profile,
        "posts": posts
    })

# ========================= DISCOVER PAGE =========================

@login_required
def discover(request):

    profiles = Profile.objects.exclude(user=request.user).select_related("user")
    activities = Activity.objects.all().order_by("-created_at").select_related("creator")

    # Accepted connections
    accepted_connections = Connection.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        status="accepted"
    )

    connected_user_ids = set()
    for conn in accepted_connections:
        if conn.sender == request.user:
            connected_user_ids.add(conn.receiver.id)
        else:
            connected_user_ids.add(conn.sender.id)

    # Pending requests sent by current user
    sent_requests = Connection.objects.filter(
        sender=request.user,
        status="pending"
    )

    sent_request_user_ids = set(sent_requests.values_list("receiver_id", flat=True))

    # Pending requests received by current user
    incoming_requests = Connection.objects.filter(
        receiver=request.user,
        status="pending"
    )

    received_request_user_ids = set(incoming_requests.values_list("sender_id", flat=True))

    # Joined activities
    joined_activity_ids = set(
        ActivityJoin.objects.filter(user=request.user)
        .values_list("activity_id", flat=True)
    )

    from django.db.models import Count
    activity_participants = dict(
        ActivityJoin.objects.values("activity")
        .annotate(count=Count("id"))
        .values_list("activity", "count")
    )

    return render(request, "discover.html", {
        "profiles": profiles,
        "activities": activities,
        "connected_user_ids": connected_user_ids,
        "sent_request_user_ids": sent_request_user_ids,
        "received_request_user_ids": received_request_user_ids,
        "incoming_requests": incoming_requests,
        "joined_activity_ids": joined_activity_ids,
        "activity_participants": activity_participants,
    })
def login_view(request):
    if request.method == "POST":
        print("LOGIN ATTEMPT")

        username = request.POST.get("username")
        password = request.POST.get("password")

        print(username, password)

        user = authenticate(request, username=username, password=password)

        print("USER:", user)

        if user is not None:
            login(request, user)
            return redirect("discover")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")

# ========================= CREATE ACTIVITY =========================



# ========================= JOIN ACTIVITY =========================

@login_required
def join_activity(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)

    if activity.creator == request.user:
        messages.error(request, "You cannot join your own activity.")
        return redirect("discover")

    if activity.status != "open":
        messages.error(request, "This activity is not open for joining.")
        return redirect("discover")

    current_count = ActivityJoin.objects.filter(activity=activity).count()

    if current_count >= activity.max_participants:
        messages.error(request, "This activity is full.")
        return redirect("discover")

    if ActivityJoin.objects.filter(user=request.user, activity=activity).exists():
        messages.info(request, "You have already joined this activity.")
        return redirect("discover")

    # ✅ Create join
    ActivityJoin.objects.create(
        user=request.user,
        activity=activity
    )

    # ✅ Recalculate count AFTER joining
    new_count = ActivityJoin.objects.filter(activity=activity).count()

    # ✅ Auto close if full
    if new_count >= activity.max_participants:
        activity.status = "closed"
        activity.save()

    messages.success(request, "Successfully joined the activity!")
    return redirect("discover")
@login_required
def remove_connection(request, user_id):
    Connection.objects.filter(
        (
            Q(sender=request.user, receiver_id=user_id) |
            Q(sender_id=user_id, receiver=request.user)
        ),
        status="accepted"
    ).delete()

    return redirect("discover")
@login_required
def send_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)

    if receiver == request.user:
        return redirect("discover")

    existing = Connection.objects.filter(
        Q(sender=request.user, receiver=receiver) |
        Q(sender=receiver, receiver=request.user)
    ).first()

    if not existing:
        Connection.objects.create(
            sender=request.user,
            receiver=receiver,
            status="pending"
        )

    return redirect("discover")

@login_required
def accept_request(request, request_id):
    connection = get_object_or_404(Connection, id=request_id, receiver=request.user)
    connection.status = "accepted"
    connection.save()
    return redirect("discover")


@login_required
def cancel_request(request, user_id):
    Connection.objects.filter(
        sender=request.user,
        receiver_id=user_id,
        status="pending"
    ).delete()

    return redirect("discover")


@login_required
def reject_request(request, request_id):
    connection = get_object_or_404(Connection, id=request_id, receiver=request.user)
    connection.delete()
    return redirect("discover")




@login_required
def create_activity(request):

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        location = request.POST.get("location")
        date = request.POST.get("date")
        time = request.POST.get("time")
        max_participants = request.POST.get("max_participants")

        Activity.objects.create(
            creator=request.user,
            title=title,
            description=description,
            location=location,
            date=date,
            time=time,
            max_participants=max_participants
        )

        return redirect("discover")

    return render(request, "create_activity.html")

@login_required
def report_user(request, user_id):
    reported_user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        reason = request.POST.get("reason")
        Report.objects.create(
            reporter=request.user,
            reported_user=reported_user,
            reason=reason
        )
        return redirect("discover")

    return render(request, "report.html", {"user": reported_user})
# ========================= LOGOUT =========================

def logout_view(request):
    logout(request)
    return redirect("home")
def about(request):
    return render(request, "about.html")