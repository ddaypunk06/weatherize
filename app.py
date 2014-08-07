from flask import Flask, url_for, redirect, request, render_template
from time import strftime
from datetime import datetime
import requests, os

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
	currentRequestTime = datetime.fromtimestamp(int(weather_data['dt'])).strftime('%a. %B %d, %Y at %I:%M %p')
	sunriseTime = datetime.fromtimestamp(int(weather_data['sys']['sunrise'])).strftime('%I:%M %p')
	sunsetTime = datetime.fromtimestamp(int(weather_data['sys']['sunset'])).strftime('%I:%M %p')
	
	description = weather_data['weather'][0]['description']
	
	#aquire and convert all temps to Celsius
	tempKelvin = float(weather_data['main']['temp'])
	#print "Temp in Kelvin: " + str(tempKelvin) #debug
	tempCelsius = tempKelvin - 273.15
	#print "Temp after C convert: " + str(tempCelsius) #debug
	maxTemp = float(weather_data['main']['temp_max']) - 273.15
	minTemp = float(weather_data['main']['temp_min']) - 273.15

	#check the checkbox and get Fareheidt if requested
	celsiusFlag = 'celsiusFlag' in request.form and request.form.get('celsiusFlag')
	#print celsiusFlag #debug
	tempflag = 1 #set flag to true if in C
	
	if not celsiusFlag:
		tempflag = 0 #set flag to flase if in F
		tempCelsius = tempCelsius + 32 * 9.0/5.0
		#print "Temp after F convert: " + str(tempCelsius) #debug
		maxTemp = maxTemp + 32 * 9.0/5.0
		minTemp = minTemp + 32 * 9.0/5.0
	
	pressure = weather_data['main']['pressure']
	humidity = weather_data['main']['humidity']

	return render_template('results.html', inputCity=inputCity, inputState=inputState,
		longitude=longitude, latitude=latitude, sunriseTime=sunriseTime,
		sunsetTime=sunsetTime, description=description, tempCelsius=tempCelsius,
		maxTemp=maxTemp, minTemp=minTemp, pressure=pressure, humidity=humidity, 
		currentRequestTime=currentRequestTime, tempflag=tempflag, title='Results')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=PORT)
