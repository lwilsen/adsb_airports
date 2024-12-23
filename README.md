## Identifying Airports with ADS-B Data!

This is a data science/visualization project that focuses on using pulled ADS-B data to identify airports in Florida, and to track the flight paths of specific flights.
The code can be adapted to anywhere in the world where ADS-B data is available.

This app depends on having an API key from the Sentinal satellite imagery API. You'll need to create an account with them, but they have a free 30 day trial which is what I used to make this app. (https://www.sentinel-hub.com/develop/api/) 

To run the app, you'll need to add your api key to the docker-compose.yml template I've provided, and then run:
```
docker compose build
```
followed by:
```
docker compose up
```
and go to the localhost link provided in your terminal/console window.

Here's a quick demo of the app's functionality!

![App Demo](adsb_proj_demo.gif)