from api import *


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

            

    def place_settlements_and_roads(self):
        pass
