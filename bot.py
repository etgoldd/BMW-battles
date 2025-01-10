from api import *
import random


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
        return

    def build_settlement(self):
        intersections= self.context.get_intersections()
        random.shuffle(intersections)
        for intersection in intersections:
            try:
                self.context.build_settlement(intersection)
                return True
            except Exceptions.NOT_ENOUGH_RESOURCES:
                return False
            except Exceptions.ILLEGAL_POSITION:
                pass

        return False



    def build_road(self):
        return

    def trade_with_bank(self):
        return



    def place_settlement_and_road(self):
        pass

    def drop_resources(self):
        resources =
        self.context.set_resources_to_drop()
