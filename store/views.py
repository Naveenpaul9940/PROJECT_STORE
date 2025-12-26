from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import Project, Payment
import razorpay

client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

def home(request):
    projects = Project.objects.all()
    return render(request, 'store/home.html', {'projects': projects})


def pay(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    order = client.order.create({
        'amount': project.price * 100,
        'currency': 'INR',
        'payment_capture': 1
    })

    payment = Payment.objects.create(
        project=project,
        razorpay_order_id=order['id'],
        status='CREATED'
    )

    return render(request, 'store/payment.html', {
        'project': project,
        'order_id': order['id'],
        'key': settings.RAZORPAY_KEY_ID
    })


def payment_success(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        payment = Payment.objects.get(razorpay_order_id=order_id)
        payment.razorpay_payment_id = payment_id
        payment.razorpay_signature = signature
        payment.status = "SUCCESS"
        payment.save()

        return redirect('download', project_id=payment.project.id)


def download(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    paid = Payment.objects.filter(
        project=project,
        status="SUCCESS"
    ).exists()

    if paid:
        return redirect(project.drive_link)
    else:
        return redirect('home')
