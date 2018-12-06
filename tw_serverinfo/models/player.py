#!/usr/local/bin/python
# coding: utf-8

from pycountry import countries

from tw_serverinfo.utility.countries import custom_countries


class Player(object):
    """Player Model Template, containing properties for all possible attributes of players"""
    _name = ''
    _clan = ''
    _country_index = '-1'
    _score = 0
    _ingame = False

    def __init__(self, name: str, clan: str = '', country: int = -1, score: int = 0, ingame: bool = False) -> None:
        """Initializing function

        :type name: str
        :type clan: str
        :type country: int
        :type score: int
        :type ingame: bool
        """
        self.name = name
        self.clan = clan
        self.country = str(country)
        self.score = score
        self.ingame = ingame

    def __repr__(self) -> str:
        """Reprint function, displays player details instead of instance information

        :return:
        """
        return 'Player(name={name:s}, clan={clan:s}, country={country:s}, country_index={country_index:d}, ' \
               'score={score:d}, ingame={ingame!r})'.format(name=self.name, clan=self.clan, country=self.country,
                                                            country_index=self.country_index, score=self.score,
                                                            ingame=self.ingame)

    def __eq__(self, other) -> bool:
        """Check for equality of objects

        :type other: Player
        :return:
        """
        return self.name == other.name and self.clan == other.clan

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def clan(self) -> str:
        return self._clan

    @clan.setter
    def clan(self, clan: str) -> None:
        self._clan = clan

    @property
    def country(self) -> str:
        if self._country_index in custom_countries:
            return custom_countries[self._country_index]['name']
        else:
            return countries.get(numeric=str(self._country_index)).name

    @country.setter
    def country(self, country: str) -> None:
        if country in custom_countries:
            self._country_index = country
        else:
            zfilled_country = country.zfill(3)
            # only allow to set indexes which are known
            try:
                self._country_index = countries.get(numeric=zfilled_country).numeric
            except KeyError:
                pass

    @property
    def country_code(self) -> str:
        if self._country_index in custom_countries:
            return custom_countries[self._country_index]['code']
        else:
            return countries.get(numeric=str(self._country_index)).alpha_2

    @property
    def country_index(self) -> int:
        return int(self._country_index)

    @property
    def score(self) -> int:
        return self._score

    @score.setter
    def score(self, score: int) -> None:
        self._score = score

    @property
    def ingame(self) -> bool:
        return self._ingame

    @ingame.setter
    def ingame(self, ingame: bool) -> None:
        self._ingame = ingame
