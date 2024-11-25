## Identifying Airports with ADS-B Data!

This is a data science/visualization project that focuses on using pulled ADS-B data to identify airports in Florida. 
The code can be adapted to anywhere in the world where ADS-B data is available.

This app depends on having an API key from the Sentinal satellite imagery API. You'll need to create an account with them, but they have a free 30 day trial which is what I used to make this app. (https://www.sentinel-hub.com/develop/api/) 

To run the app, you'll need to add your api key to the docker-compose.yml template I've provided, and then run "docker compose build". Then run "docker compose up" and go to the link provided in your terminal/console window.

The coolest part of this project is clicking a hex on the plotly map, and then viewing a satellite image of that area.

![Screen Recording 2024-11-25 at 1 40 26 PM](https://github.com/user-attachments/assets/e602f521-187f-4001-9d16-5ecb9240df35)
