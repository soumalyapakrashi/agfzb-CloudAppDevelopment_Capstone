from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarMake, CarModel
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def homepage(request):
    if request.method == 'GET':
        return render(request, 'djangoapp/index.html')

# Create an `about` view to render a static about page
def about(request):
    if request.method == 'GET':
        return render(request, 'djangoapp/about.html')


# Create a `contact` view to return a static contact page
def contact(request):
    if request.method == 'GET':
        return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        print(username, password)
        user = authenticate(username=username, password=password)
        if user is not None:
            print("User is authenticated")
            login(request, user)
            return render(request, 'djangoapp/index.html', context)
        else:
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return render(request, 'djangoapp/index.html')


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        user_exist = False
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        password = request.POST['password']
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=firstname, last_name=lastname, password=password)
            login(request, user)
            return render(request, "djangoapp/index.html", context)
        else:
            return render(request, 'djangoapp/index.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/soumalyapakrashi%40gmail.com_dev/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context['dealerships'] = dealerships
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id, dealer_name):
    context = {}
    if request.method == "GET":
        url = "https://eu-gb.functions.appdomain.cloud/api/v1/web/soumalyapakrashi%40gmail.com_dev/dealership-package/get-review"
        # Get dealers from the URL
        reviews = get_dealer_reviews_from_cf(url, dealerId=dealer_id)
        context["reviews"] = reviews
        context["dealer_name"] = dealer_name
        context["dealer_id"] = dealer_id
        print("Context:", reviews[0])
        # Concat all dealer's short name
        # reviewer_names = ' '.join([review.sentiment["sentiment"]["document"]["label"] for review in reviews])
        # Return a list of dealer short name
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id, dealer_name):
    cars = []

    if request.method == 'GET':
        car_makes = CarMake.objects.all().values()
        car_models = CarModel.objects.all().values()

        for car_model in car_models:
            car = {}
            car["id"] = car_model["id"]
            car["name"] = car_model["name"]
            car["year"] = car_model["year"].year
            make_id = car_model["car_model_id"]
            make_name = None
            for make in car_makes:
                if make["id"] == make_id:
                    make_name = make["name"]
            car["make_name"] = make_name

            cars.append(car)
        
        

    elif request.method == 'POST':
        car_makes = CarMake.objects.all().values()
        car_models = CarModel.objects.all().values()

        car_model = None
        car_make = None
        car_year = None

        for car_model_loop in car_models:
            if car_model_loop['id'] == int(request.POST['car']):
                car_model = car_model_loop['name']
                car_year = car_model_loop['year'].year

                for car_make_loop in car_makes:
                    if car_make_loop['id'] == car_model_loop['car_model_id']:
                        car_make = car_make_loop['name']

        review = {
            "car_make": car_make,
            "car_model": car_model,
            "car_year": car_year,
            "dealership": dealer_id,
            "name": request.user.first_name + " " + request.user.last_name,
            "purchase": request.POST.get('purchasecheck', False) == 'on',
            "purchase_date": request.POST["purchasedate"],
            "review": request.POST["content"]
        }
        json_payload = {
            "review": review
        }

        response = post_request(
            url="https://eu-gb.functions.appdomain.cloud/api/v1/web/soumalyapakrashi%40gmail.com_dev/dealership-package/get-review",
            json_payload=json_payload
        )

    context = {
        "cars": cars,
        "dealer_id": dealer_id,
        "dealer_name": dealer_name
    }

    return render(request, 'djangoapp/add_review.html', context)
