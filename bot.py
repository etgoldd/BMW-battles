from api import *
import random
import math

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
        resources = API.get_resource_counts()
        total = sum(resources)
        for res_index, res_count in enumerate(resources):
            resources[res_index] = math.ceil(res_count / 2)
        diff = total - sum(resources)
        for _ in range(diff):
            while True:
                dropped_res = random.randint(0, 5)
                if resources[dropped_res] > 0:
                    resources[res_index] -= 1
                    break
        self.context.set_resources_to_drop(resources)

            