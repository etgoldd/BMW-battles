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
        self.cards = self.context.get_resource_counts()
        if self.build_city():
            return
        elif self.build_settlement():
            return
        elif self.build_road():
            return
        elif self.trade_with_bank():
            return
        return 

    def build_city(self):
        buildings = self.context.get_player_buildings(self.context.get_player_index())
        for pos, building in buildings:
            if building == Buildings.SETTLEMENT:
                self.context.build_city(pos)
    
    def build_settlement(self):
        return
    
    def build_road(self):
        return
    
    def trade_with_bank(self):
        return

            

    def place_settlement_and_road(self):
        pass

    def drop_resources(self):
        resources = 
        self.context.set_resources_to_drop()
