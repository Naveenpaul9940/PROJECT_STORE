from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.IntegerField()
    drive_link = models.URLField()
    thumbnail = models.ImageField(upload_to='thumbnails/')

    def __str__(self):
        return self.title



class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    razorpay_order_id = models.CharField(max_length=200)
    razorpay_payment_id = models.CharField(max_length=200, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=500, blank=True, null=True)

    amount = models.IntegerField()  # in paise
    status = models.CharField(max_length=20, default="CREATED")  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.project.title} - {self.status}"
