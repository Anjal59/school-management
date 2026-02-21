from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Attendance, Task, Notification, TaskSubmission
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

User = get_user_model()

def login_view(request):
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.role == "student":
                return redirect("student_home")
            elif user.role == "teacher":
                return redirect("teacher_home")
            elif user.role == "admin":
                return redirect("admin_home")

        else:
            return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html")


@login_required
def student_home(request):

    if request.user.role != "student":
        return redirect("login")

    today = timezone.now().date()

    already_marked = Attendance.objects.filter(
        student=request.user,
        date=today
    ).exists()

    # Handle POST
    if request.method == "POST":

        # ✅ Attendance Form
        if "attendance_submit" in request.POST and not already_marked:
            Attendance.objects.create(
                student=request.user,
                status="Present"
            )
            return redirect("student_home")

        # ✅ Task Submission Form
        if "task_submit" in request.POST:
            task_id = request.POST.get("task_id")
            submission_text = request.POST.get("submission_text")

            task = Task.objects.get(id=task_id)

            # Prevent multiple submissions
            already_submitted = TaskSubmission.objects.filter(
                task=task,
                student=request.user
            ).exists()

            if not already_submitted and submission_text:
                TaskSubmission.objects.create(
                    task=task,
                    student=request.user,
                    submission_text=submission_text
                )

            return redirect("student_home")

    attendance = Attendance.objects.filter(student=request.user)
    tasks = Task.objects.filter(assigned_to=request.user)
    notifications = Notification.objects.all()

    context = {
        "attendance": attendance,
        "tasks": tasks,
        "notifications": notifications,
        "already_marked": already_marked,
    }

    return render(request, "student_home.html", context)


@login_required
def teacher_home(request):

    if request.user.role != "teacher":
        return redirect("login")

    students = User.objects.filter(role="student")
    submissions = TaskSubmission.objects.filter(task__teacher=request.user)
    attendance_records = Attendance.objects.all().order_by("-date")

    if request.method == "POST":

        # 🔔 Notification Form
        if "notification_submit" in request.POST:
            message = request.POST.get("notification_message")

            if message:  # prevent empty
                Notification.objects.create(
                    teacher=request.user,
                    message=message
                )

        # 📌 Create Task Form
        elif "create_task_submit" in request.POST:
            title = request.POST.get("title")
            description = request.POST.get("description")
            student_id = request.POST.get("student")
            due_date = request.POST.get("due_date")

            if title and student_id and due_date:
                student = User.objects.get(id=student_id)

                Task.objects.create(
                    teacher=request.user,   # 🔥 ADD THIS
                    title=title,
                    description=description,
                    assigned_to=student,
                    due_date=due_date
                )

        return redirect("teacher_home")

    context = {
        "students": students,
        "submissions": submissions,
        "attendance_records": attendance_records,
    }

    return render(request, "teacher_home.html", context)


def create_task(request):
    students = User.objects.filter(role='student')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        student_id = request.POST.get('student')
        due_date = request.POST.get('due_date')

        student = User.objects.get(id=student_id)

        Task.objects.create(
            title=title,
            description=description,
            assigned_to=student,
            due_date=due_date
        )

        return redirect('teacher_dashboard')

    return render(request, 'create_task.html', {'students': students})

def student_tasks(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    return render(request, 'student_tasks.html', {'tasks': tasks})



@login_required
def submit_task(request, task_id):

    if request.user.role != "student":
        return redirect("login")

    task = get_object_or_404(Task, id=task_id)

    # Security: student can submit only their task
    if task.assigned_to != request.user:
        return redirect("student_home")

    # Prevent multiple submission
    already_submitted = TaskSubmission.objects.filter(
        task=task,
        student=request.user
    ).exists()

    # Block after due date
    if task.due_date and task.due_date < timezone.now().date():
        return redirect("student_home")

    if request.method == "POST" and not already_submitted:
        submission_text = request.POST.get("submission_text")

        if submission_text:
            TaskSubmission.objects.create(
                task=task,
                student=request.user,
                submission_text=submission_text
            )

        return redirect("student_home")

    return render(request, "submit_task.html", {
        "task": task,
        "already_submitted": already_submitted
    })




@login_required
def admin_home(request):
    return render(request, "admin_home.html")





@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")

