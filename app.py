import requests
from flask import Flask, render_template, request, redirect, url_for
import sqlite3 as sql 

app = Flask(__name__)

url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metrics&appid={}'
key = "1a4c4f306c55a790989a33c6b9d37973"

@app.route('/', methods=['GET','POST'])
def index():
	print('redirected to inedx')
	error = None
	db = sql.connect("cities.db")
	cursor = db.cursor()	
	if request.method == 'POST':
		new_city = request.form.get('city')
		r = requests.get(url.format(new_city,key)).json()
		if r['cod'] != '404':
			cursor.execute("select * from city") 
			cities = [ city[0] for city in cursor.fetchall() ]
			if new_city and new_city not in cities :
				cursor.execute(f"insert into city values('{new_city}')")
				db.commit()
		else:
			error = "Such city name does not exists, Try again"
	cursor.execute("select * from city")
	cities = [ city[0] for city in cursor.fetchall() ]
	print(cities)
	cursor.close()
	db.close()
	
	weather_data = []
	for city in cities:
		r = requests.get(url.format(city,key)).json()
		weather = {
            'city' : city,
            'temperature' : round(r['main']['temp'] - 273.15,2),
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
        }
		weather_data.append(weather)
	print(weather_data)
	return render_template('index.html', weather_data=weather_data, error = error)
	
@app.route('/clear')
def clear():
	db = sql.connect("cities.db")
	cursor = db.cursor()	
	cursor.execute("delete from city")
	db.commit()
	cursor.close()
	print("Successfully cleared")
	db.close()
	return redirect(url_for('index'))
	
if __name__ == "__main__" : 

	app.run("localhost",8088,debug=True)