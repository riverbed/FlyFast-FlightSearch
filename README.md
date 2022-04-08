# FlyFast - FlightSearch

This repository contains the source code for the FlightSearch of FlyFast.

For the source code of the WebUI, head over to the [WebUI](https://github.com/Aternity/FlyFast-WebUI). This will provide a WebUI to make calls to  the FlightSearch.

To view the full source code and to run the whole application through Docker, head over to [FlyFast](https://github.com/Aternity/FlyFast).

## Requirements

1. [Git](https://git-scm.com/) (Optional)
2. a Docker host, for example [Docker Desktop](https://www.docker.com/products/docker-desktop) (Optional)
3. [Python 3.7](https://www.python.org/downloads/release/python-370/) (Required)
4. [WebUI](https://github.com/Aternity/FlyFast-WebUI) (Required Only For Having A UI)

## Getting Started
1. Clone/download this repository.
    ```
    git clone https://github.com/Aternity/FlyFast-FlightSearch.git
    ```
2. Using the terminal, change the directory to the folder of this project.
    ```
    cd FlyFast-FlightSearch
    ```
3. You can either start the application using [Python](#step-by-step-using-python) or [Docker](#step-by-step-using-docker).

## Step by Step Using Python
1. Install the dependencies required to run this application:
    ```
    pip install -r requirements.txt
    ```
2. Make sure to set the environment variables for the application.
    - `COLLECTOR_URL` is the APM Collector URL, which should be on port `9411`, if you are using the [Aternity APM Collector](https://hub.docker.com/r/aternity/apm-collector).

      For example, with Bash:
      ```
      export COLLECTOR_URL="http://localhost:9411/api/v2/spans"
      ```
      or with Powershell:
      ```
      $env:COLLECTOR_URL="http://localhost:9411/api/v2/spans"
      ```
3. Start the application and open [http://localhost:8080](http://localhost:8080) to view it in your browser.
    ```
    py src/main.py
    ```

## Step by Step Using Docker
1. Build our docker:
    ```
    docker build . -t Search
    ```
2. Run our docker container, make sure to set the environment variables for the application:
    - `COLLECTOR_URL` is the APM Collector URL, which should be on port `9411`, if you are using the [Aternity APM Collector](https://hub.docker.com/r/aternity/apm-collector).
    ```
    docker run --rm -p 8080:8080 -e COLLECTOR_URL=http://localhost:9411/api/v2/spans Search
    ```
3. Open [http://localhost:8080](http://localhost:8080) to view it in your browser.

## API Request

| Functionality      | API Request        | Fields   |
| ------------------ |------------------- | -------- |
| Airport Typeahead  | `/flightsearchapi/airportypeahead?searchtxt=${text}&limit=${limit}`                                                   | - `text` - text<br/>- `limit` - limit response |
| Single Trip        | `/flightsearchapi/searchflight?from=${from}&to=${to}&departure=${departureDate}&seat=${seatType}`                     | - `from` - 3 Letter Airport<br/> - `to` - 3 Letter Airport<br/> - `departureDate` - MM-DD-YYYY<br/> - `seatType` - Economy, Premium Economy, Business, First |
| Round Trip         | `/flightsearchapi/searchflight?from=${from}&to=${to}&departure=${departureDate}&return={returnDate}&seat=${seatType}` | - `from` - 3 Letter Airport<br/> - `to` - 3 Letter Airport<br/> - `departureDate` - MM-DD-YYYY<br/> - `returnDate` - MM-DD-YYYY<br/>- `seatType` - Economy, Premium Economy, Business, First |

## API Response
### Airport Typeahead Response
```
[
  {
    "value": ${airport},
    "name": ${airportName},
    "city": ${city},
    "region": ${region},
    "country": ${country}
  }
]
```
### Single Trip Response
```
[
  [
    {
      "from": ${from}, 
      "to": ${to}, 
      "flights": [
        { 
          "id": ${id},
          "flightNumber": ${flightNumber},
          "airline": ${airline},
          "from": ${from}, 
          "to": ${to}, 
          "departureTime": ${departureTime}, 
          "arrivalTime": ${arrivalTime}, 
          "seat": ${seat},
          "fare": ${fare}
        },
        { 
          "id": ${id},
          "flightNumber": ${flightNumber},
          "airline": ${airline},
          "from": ${from}, 
          "to": ${to}, 
          "departureTime": ${departureTime}, 
          "arrivalTime": ${arrivalTime}, 
          "seat": ${seat},
          "fare": ${fare}
        }
      ],
      "departureTime": ${departureTime}, 
      "arrivalTime": ${arrivalTime}, 
      "fare": ${fare}
    }
  ]
]
```
### Round Trip Response
response[0][0] - Contains to flight details

response[0][1] - Contains return flight details
```
[
  [
    {
      "from": ${from}, 
      "to": ${to}, 
      "flights": [
        { 
          "id": ${id},
          "flightNumber": ${flightNumber},
          "airline": ${airline},
          "from": ${from}, 
          "to": ${to}, 
          "departureTime": ${departureTime}, 
          "arrivalTime": ${arrivalTime}, 
          "seat": ${seat},
          "fare": ${fare}
        },
        { 
          "id": ${id},
          "flightNumber": ${flightNumber},
          "airline": ${airline},
          "from": ${from}, 
          "to": ${to}, 
          "departureTime": ${departureTime}, 
          "arrivalTime": ${arrivalTime}, 
          "seat": ${seat},
          "fare": ${fare}
        }
      ],
      "departureTime": ${departureTime}, 
      "arrivalTime": ${arrivalTime}, 
      "fare": ${fare}
    }
  ],
  [
    {
      "from": ${from}, 
      "to": ${to}, 
      "flights": [
        { 
          "id": ${id},
          "flightNumber": ${flightNumber},
          "airline": ${airline},
          "from": ${from}, 
          "to": ${to}, 
          "departureTime": ${departureTime}, 
          "arrivalTime": ${arrivalTime}, 
          "seat": ${seat},
          "fare": ${fare}
        },
        { 
          "id": ${id},
          "flightNumber": ${flightNumber},
          "airline": ${airline},
          "from": ${from}, 
          "to": ${to}, 
          "departureTime": ${departureTime}, 
          "arrivalTime": ${arrivalTime}, 
          "seat": ${seat},
          "fare": ${fare}
        }
      ],
      "departureTime": ${departureTime}, 
      "arrivalTime": ${arrivalTime}, 
      "fare": ${fare}
    }
  ]
]
```