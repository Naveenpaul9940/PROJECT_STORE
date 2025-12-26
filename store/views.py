from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.models import User
import razorpay
from .models import Project, Payment

client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

def create_superuser(request):
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )
        return HttpResponse("Superuser created!")
    return HttpResponse("Superuser already exists.")

def home(request):
    projects = Project.objects.all()
    return render(request, "store/home.html", {"projects": projects})

def pay(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    amount = int(project.price * 100)

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    Payment.objects.create(
        project=project,
        razorpay_order_id=order["id"],
        status="CREATED"
    )

    return render(request, "store/payment.html", {
        "project": project,
        "order_id": order["id"],
        "key": settings.RAZORPAY_KEY_ID,
        "amount_in_paise": amount
    })

def payment_success(request):
    if request.method == "POST":
        order_id = request.POST.get("razorpay_order_id")
        payment_id = request.POST.get("razorpay_payment_id")
        signature = request.POST.get("razorpay_signature")

        payment = get_object_or_404(Payment, razorpay_order_id=order_id)
        payment.razorpay_payment_id = payment_id
        payment.razorpay_signature = signature
        payment.status = "SUCCESS"
        payment.save()

        return redirect("download", project_id=payment.project.id)

    return redirect("home")

def download(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    paid = Payment.objects.filter(project=project, status="SUCCESS").exists()

    if paid:
        return redirect(project.drive_link)
    return redirect("home")
