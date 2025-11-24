from django.db import models
class Client(models.Model):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email= models.EmailField(unique=True)
    phone= models.CharField(max_length=20,blank=True)

    def __str__(self):
        return f"{self.first_name}  {self.last_name}"
# Create your models here.
class Fridge(models.Model):
    name = models.CharField(max_length=32,unique=True)
    topic = models.CharField(max_length=32, unique=True)

    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    updated_at= models.DateTimeField(auto_now=True)
    fan_gpio = models.IntegerField(default=18)   
    fan_on   = models.BooleanField(default=False)  
    alert_email = models.EmailField(blank=True, null=True)  
    last_alert_ts = models.DateTimeField(blank=True, null=True)


    temp_threshold     = models.FloatField(default=8.0)   
    humidity_threshold = models.FloatField(default=85.0)

    def __str__(self):
        return f"{self.name} ({self.topic})"
    