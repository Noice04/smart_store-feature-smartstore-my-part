from django.contrib import messages
from .models import Client
from .light import show_success,show_failure
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Fridge
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


# phase1 client
def store_view(request):
    if request.method == "GET":
        return render(request, 'smartstore/store.html')
    
    if request.method == "POST":
        print("POST received:",request.POST)
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        if not fname or not lname:
            show_failure()
            messages.error(request, "First and Last name are required.")
            return render(request, "smartstore/store.html",{"data":request.POST})

        try:
            Client.objects.create(first_name=fname,last_name=lname,email=email or None,phone=phone or "",)
        except Exception as e:
            show_failure()
            messages.error(request, f"Could not save client: {e}")
            return render(request, "smartstore/store.html",{"data":request.POST})
        print("saving client & calling show_success()")
        show_success()
        messages.success(request, "Client added successfuly.")
        return redirect("smartstore:store")
    
    return HttpResponseNotAllowed(["GET","POST"])


# phase 2 fridge
def dashboard(request):
    fridges = Fridge.objects.order_by("id")
    fridges_data = list(fridges.values(
            "id","name","topic","temperature","humidity",
            "temp_threshold","humidity_threshold","updated_at"
        )
    )
    return render(request, "smartstore/dashboard.html", {
        "fridges": fridges,              
        "fridges_data": fridges_data,    
    })


def api_latest_readings(request):
    fridges = list(
        Fridge.objects.values(
            "id", "name", "topic",
            "temperature", "humidity",
            "temp_threshold", "humidity_threshold", "fan_on",
            "updated_at",
        ).order_by("id")
    )
    return JsonResponse({"fridges": fridges})

@csrf_exempt
def update_thresholds(request, pk):
    fridge = get_object_or_404(Fridge, pk=pk)
    if request.method == "POST":
        try:
            t = request.POST.get("temp_threshold")
            h = request.POST.get("humidity_threshold")
            if t is not None:
                fridge.temp_threshold = float(t)
            if h is not None:
                fridge.humidity_threshold = float(h)
            fridge.save(update_fields=["temp_threshold", "humidity_threshold"])
            messages.success(request, f"{fridge.name} thresholds updated.")
        except Exception as e:
            messages.error(request, f"Failed to update thresholds: {e}")
    return redirect("smartstore:dashboard")


@require_POST
def fan_toggle(request, pk):
    f = get_object_or_404(Fridge, pk=pk)
    action = (request.POST.get("action") or "").upper() 
    want_on = (action == "ON")
    # update DB
    f.fan_on = want_on
    f.save(update_fields=["fan_on"])
    messages.success(request, f"Fan for {f.name} set to {action}.")

    # publish an MQTT command so fan_control.py acts
    try:
        import paho.mqtt.publish as publish
        publish.single(f"fan/{f.topic}/cmd", action, hostname="localhost", port=1883)
    except Exception:
        pass

    return redirect("smartstore:dashboard")