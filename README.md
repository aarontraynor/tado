# tado-geolocation

A simple Python script to automatically set a Tado system to Home/Away based on the geolocation of devices connected to the Tado account.

A log file `log.txt` will be created to track when a device changes state and when the Tado system is set to Home/Away.

## Requirements
- Poetry >=1.6.1
- Python >=3.8.1

## First-time setup
`poetry install`

## Usage (via Docker)
`docker build -t tado-geolocation .`
`docker run -d --name tado tado-geolocation -u $TADO_USERNAME -p $TADO_PASSWORD`

## Usage (Manual)
`poetry run python main.py -u $TADO_USERNAME -p $TADO_PASSWORD`
