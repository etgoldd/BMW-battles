from api import *


class PRICES:
    ROAD = ResourceCounts(lumber=1, brick=1),
    SETTLEMENT = ResourceCounts(lumber=1, brick=1, grain=1, wool=1)
    CITY = ResourceCounts(wool=2, ore=3)
    DEVELOPMENT_CARD = ResourceCounts(grain=1, wool=1, ore=1)


class MyBot(CatanBot):
    
    def setup(self):
        pass

    def play(self):
        pass

    def place_settlement_and_road(self):
        pass

    def drop_resources(self):
        resources = 
        self.context.set_resources_to_drop()
