import os
from django.shortcuts import render, redirect
import requests
from .models import City
from .forms import CityForm
from dotenv import load_dotenv
load_dotenv()
YOUR_APP_KEY = os.getenv('YOUR_APP_KEY')


def home(request):
    message = ''
    message_class = ''
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            new_city = form.cleaned_data['name']
            existing_city_count = City.objects.filter(name=new_city).count()
            if existing_city_count == 0:
                url = f'http://api.openweathermap.org/data/2.5/weather?q={new_city}&units=imperial&appid={YOUR_APP_KEY}'
                req = requests.get(url.format(new_city)).json()
                if req['cod'] == 200:
                    form.save()
                    message = 'City added successfully!'
                    message_class = "alert-success"
                else:
                    message = 'City does not exist '
                    message_class = 'alert-danger'
            else:
                message = 'City already exist in database!'
                message_class = 'alert-danger'

    form = CityForm()
    cities = City.objects.all()
    weather_data = []

    for city in cities:
        response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&appid={YOUR_APP_KEY}')
        if response.status_code == 404:
            continue
        city_weather = response.json()
        weather = {
            'city': city,
            'temperature': (city_weather['main']['temp'] - 32) * 5 // 9,
            'description': city_weather['weather'][0]['description'],
            'icon': city_weather['weather'][0]['icon']
        }
        weather_data.append(weather)

    context = {'weather_data': weather_data, 'form': form, 'message': message, 'message_class': message_class}

    return render(request, 'main_page.html', context)


def delete_city(request, city_name):
    city = City.objects.get(name=city_name)
    city.delete()
    return redirect('home')
