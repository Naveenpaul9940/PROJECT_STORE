from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.models import User
import razorpay
from requests.exceptions import ConnectionError
from .models import Project, Payment
from django.core.management import call_command
import time

# Razorpay client
client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

# Create superuser (temporary utility)
def create_superuser(request):
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )
        return HttpResponse("Superuser created!")
    return HttpResponse("Superuser already exists.")

# Home page
def home(request):
    projects = Project.objects.all()
    return render(request, "store/home.html", {"projects": projects})

# Payment page
def pay(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    amount = int(project.price * 100)  # Razorpay amount in paise

    # Retry mechanism in case Razorpay server connection fails
    for attempt in range(2):
        try:
            order = client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": 1
            })
            break
        except ConnectionError:
            if attempt == 1:
                raise
            time.sleep(1)  # wait 1 sec before retry

    # Save payment object
    Payment.objects.create(
        user=request.user if request.user.is_authenticated else None,
        project=project,
        razorpay_order_id=order["id"],
        amount=amount,
        status="CREATED"
    )

    return render(request, "store/payment.html", {
        "project": project,
        "order_id": order["id"],
        "key": settings.RAZORPAY_KEY_ID,
        "amount_in_paise": amount
    })

# Payment success callback
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

# Download project after successful payment
def download(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    paid = Payment.objects.filter(project=project, status="SUCCESS").exists()

    if paid:
        return redirect(project.drive_link)
    return redirect("home")

# Temporary view to apply migrations (for production)
def apply_migrations(request):
    try:
        call_command("migrate", "store", interactive=False)
        return HttpResponse("✅ Migrations applied successfully for 'store' app!")
    except Exception as e:
        return HttpResponse(f"❌ Error applying migrations: {e}")
