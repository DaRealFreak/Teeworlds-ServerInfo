# Teeworlds Server Info
[![Build Status](https://travis-ci.com/DaRealFreak/Teeworlds-ServerInfo.svg?branch=master)](https://travis-ci.com/DaRealFreak/Teeworlds-ServerInfo)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/DaRealFreak/Teeworlds-ServerInfo/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/DaRealFreak/Teeworlds-ServerInfo/?branch=master)
[![Coverage Status](https://coveralls.io/repos/github/DaRealFreak/Teeworlds-ServerInfo/badge.svg?branch=master)](https://coveralls.io/github/DaRealFreak/Teeworlds-ServerInfo?branch=master)

small module to retrieve the registered servers from the master server and request the player information of each server.

### Installing
This script runs with [Python 3](https://www.python.org).

Download this repository and run the setup.py to install all necessary dependencies

### Dependencies
Required:
 * [pycountry](https://pypi.org/project/pycountry/) - Extension to retrieve country codes/names based on the numeric identifier

### Usage
An example usage to retrieve the master servers, game servers and server information is in the file
[usage.py](usage.py)

## Running the tests
In the tests folder you can run each unittest individually.
The test cases should be self-explanatory.

## Development
Want to contribute? Great!
I'm always glad hearing about bugs or pull requests.

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
