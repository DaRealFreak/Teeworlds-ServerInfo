# Teeworlds Server Info
[![Build Status](https://img.shields.io/travis/com/DaRealFreak/Teeworlds-ServerInfo.svg?style=flat-square)](https://travis-ci.com/DaRealFreak/Teeworlds-ServerInfo)
[![Scrutinizer](https://img.shields.io/scrutinizer/g/DaRealFreak/Teeworlds-ServerInfo.svg?style=flat-square)](https://scrutinizer-ci.com/g/DaRealFreak/Teeworlds-ServerInfo/?branch=master)
[![Coveralls github](https://img.shields.io/coveralls/github/DaRealFreak/Teeworlds-ServerInfo.svg?style=flat-square)](https://coveralls.io/github/DaRealFreak/Teeworlds-ServerInfo?branch=master)
[![GitHub license](https://img.shields.io/github/license/DaRealFreak/Teeworlds-ServerInfo.svg?style=flat-square)](https://github.com/DaRealFreak/Teeworlds-ServerInfo/blob/master/LICENSE.md)  
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
