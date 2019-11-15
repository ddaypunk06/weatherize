"""
Authored by: Andy Delso
Weatherize Flask application
Uses bootstrap, bootswatch css
"""

from flask import Flask, url_for, redirect, request, render_template
from time import strftime
from datetime import datetime
from tzlocal import get_localzone
import requests, os, sys, pytz

#helper methods
def utc_to_local(utc_dt, local_tz=get_localzone()):

	#local_tz = pytz.timezone('America/Chicago')
	#print local timezone to check
	print "Detected Timezone =\t" + str(local_tz)
	#use local timezone to convert utc datetime to local datetime
	local_dt = utc_dt.replace(tzinfo=pytz.UTC).astimezone(local_tz)
	return local_tz.normalize(local_dt) #.normallize may be unnecessary

def get_time_local(utc_ts, formatting):
	#make into datetime object
	dto = datetime.fromtimestamp(int(utc_ts))
	#localize the time by using utc_to_local method
	localized_dto = utc_to_local(dto)
	#return formatted string
	return str(localized_dto.strftime(formatting))

#setup port and API key for later use
PORT = int(os.environ.get('PORT', 5000))
API_KEY = os.environ.get('API_KEY')

app = Flask(__name__)
app.config.from_object(__name__)



@app.route('/', methods=['GET'])
def index():
	return render_template('index.html', title='Home')

@app.route('/home', methods=['GET'])
def home():
	return render_template('index.html', title="Home")

@app.route('/results', methods=['POST'])
def results():
	inputCity = request.form['inputCity']
	inputState = request.form['inputState']

	#if not inputCity or not inputState:
		#return redirect(url_for('home'))

	#construct the URL to make the API request
	uri = "http://api.openweathermap.org/data/2.5/weather"
	params = {
	'q': str(inputCity + ',' + inputState),
	'APPID': API_KEY,
	}
	response = requests.get(uri, params=params)

	#collect the JSON response
	weather_data = response.json()
	#print weather_data #debug

	longitude = weather_data['coord']['lon']
	latitude = weather_data['coord']['lat']

	#aquire and convert times from unix format to python datetime
	currentRequestTime = get_time_local(weather_data['dt'], '%a. %B %d, %Y at %I:%M %p')

	#these are localized by the API it seems (should the times be converted to the local of the city?)
	sunriseTime = get_time_local(weather_data['sys']['sunrise'],'%I:%M %p')
	sunsetTime = get_time_local(weather_data['sys']['sunset'],'%I:%M %p')
	
	description = weather_data['weather'][0]['description']
	weather_icon = "http://openweathermap.org/img/w/" + str(weather_data['weather'][0]['icon']) + ".png"

	
	#aquire and convert all temps to Celsius
	tempKelvin = float(weather_data['main']['temp'])
	#print "Temp in Kelvin: " + str(tempKelvin) #debug
	tempCelsius = tempKelvin - 273.15
	tempCelsius = round(tempCelsius, 2)
	#print "Temp after C convert: " + str(tempCelsius) #debug
	maxTemp = float(weather_data['main']['temp_max']) - 273.15
	minTemp = float(weather_data['main']['temp_min']) - 273.15

	#check the checkbox and get Fareheidt if requested
	celsiusFlag = 'celsiusFlag' in request.form and request.form.get('celsiusFlag')
	#print celsiusFlag #debug
	tempflag = 1 #set flag to true if in C
	
	if not celsiusFlag:
		tempflag = 0 #set flag to flase if in F
		tempCelsius = (tempCelsius * 9.0/5.0) + 32
		tempCelsius = round(tempCelsius, 1)


		#print "Temp after F convert: " + str(tempCelsius) #debug
		maxTemp = (maxTemp * 9.0/5.0) + 32
		minTemp = (minTemp * 9.0/5.0) + 32
	
	pressure = weather_data['main']['pressure']
	humidity = weather_data['main']['humidity']

	return render_template('results.html', inputCity=inputCity.title(), inputState=inputState.upper(),
		longitude=longitude, latitude=latitude, sunriseTime=sunriseTime,
		sunsetTime=sunsetTime, description=description, tempCelsius=tempCelsius,
		maxTemp=maxTemp, minTemp=minTemp, pressure=pressure, humidity=humidity, 
		currentRequestTime=currentRequestTime, tempflag=tempflag,
		weather_icon=weather_icon, title='Results')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=PORT)
