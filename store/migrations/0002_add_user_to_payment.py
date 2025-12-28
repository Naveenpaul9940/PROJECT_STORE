from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),  # replace with your last migration
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='user',
            field=models.ForeignKey(
                to='auth.User',
                on_delete=django.db.models.deletion.CASCADE,
                null=True,
                blank=True
            ),
        ),
    ]
