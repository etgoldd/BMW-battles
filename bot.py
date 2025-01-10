from api import *


class PRICES:
    ROAD = ResourceCounts(lumber=1, brick=1),
    SETTLEMENT = ResourceCounts(lumber=1, brick=1, grain=1, wool=1)
    CITY = ResourceCounts(grain=2, ore=3)
    DEVELOPMENT_CARD = ResourceCounts(grain=1, wool=1, ore=1)


class MyBot(CatanBot):
    
    def setup(self):
        pass

    def play(self):
        cards = self.context.get_resource_counts()
        lumber, brick, grain, wool, ore = cards
        if can_build_city:
            build_city
            return
        elif can_place_settlement:
            build_best_settlement
            return
        elif can_place_road:
            build_road
            return
        elif trade_with_bank:
            return

            

    def place_settlement_and_road(self):
        pass

    def drop_resources(self):
        resources = 
        self.context.set_resources_to_drop()
