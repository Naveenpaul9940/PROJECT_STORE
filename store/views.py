from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import Project, Payment
import razorpay
from django.contrib.auth.models import User
from django.http import HttpResponse

# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def create_superuser(request):
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="naveenpaul9940@gmail.com",
            password="Naveenpaul9940_"
        )
        return HttpResponse("Superuser created!")
    return HttpResponse("Superuser already exists.")


def home(request):
    projects = Project.objects.all()
    return render(request, 'store/home.html', {'projects': projects})


def pay(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    amount = project.price * 100

    order = client.order.create({
        'amount': amount,
        'currency': 'INR',
        'payment_capture': 1
    })

    Payment.objects.create(
        project=project,
        razorpay_order_id=order['id'],
        status="CREATED"
    )

    return render(request, 'store/checkout.html', {
        'project': project,
        'order': order,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID
    })


def payment_success(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        payment = get_object_or_404(Payment, razorpay_order_id=order_id)
        payment.razorpay_payment_id = payment_id
        payment.razorpay_signature = signature
        payment.status = "SUCCESS"
        payment.save()

        return redirect('download', project_id=payment.project.id)
    return redirect('home')


def download(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    paid = Payment.objects.filter(project=project, status="SUCCESS").exists()

    if paid:
        return redirect(project.drive_link)  # direct download
    else:
        return redirect('home')
