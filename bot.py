# LUMBER = <Resources.LUMBER: 0>
# BRICK = <Resources.BRICK: 1>
# GRAIN = <Resources.GRAIN: 2>
# WOOL = <Resources.WOOL: 3>
# ORE = <Resources.ORE: 4>

from api import *
import random
import math
from typing import Tuple

class PRICES:
    ROAD = ResourceCounts(lumber=1, brick=1),
    SETTLEMENT = ResourceCounts(lumber=1, brick=1, grain=1, wool=1)
    CITY = ResourceCounts(grain=2, ore=3)
    DEVELOPMENT_CARD = ResourceCounts(grain=1, wool=1, ore=1)

class MyBot(CatanBot):
    fixed_land_value = [16, 16, 16, 16, 16, 0]
    virtual_land_value = [16, 16, 16, 16, 16, 0]
    divide_when_taken = [2, 2, 2, 2, 2, 2]

    land_num_to_score = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}

    def set_fixed_land_value_to_virtual(self):
        self.fixed_land_value = self.virtual_land_value

    def rank_land(self, position: Tuple[int, int]):
        land = self.context.get_land(position)
        if land is None:
            return 0
        land_num = self.context.get_number(position)
        land_score = self.land_num_to_score[land_num]
        value = self.virtual_land_value[land.value] * land_score
        # self.virtual_land_value[land.value] /= self.divide_when_taken[land.value]
        return value

    def rank_intersection(self, position: Tuple[int, int]):
        terrains: List[Tuple[int, int]] = self.context.get_adjacent_terrains(position)
        self.virtual_land_value = self.fixed_land_value[::]
        res = sum(self.rank_land(land_pos) for land_pos in terrains)
        self.set_fixed_land_value_to_virtual()
        return res

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
        return

    def build_road(self):
        return

    def trade_with_bank(self):
        return

    def place_settlement_and_road(self):
        best_position: Position | None = None
        best_rank = 0
        for position in self.context.get_intersections():
            if self.context.get_current_building(position):
                continue
            rank = self.rank_intersection(position)
            if rank > best_rank:
                best_position = position
                best_rank = rank
        if best_position:
            self.context.build_settlement(best_position)
            self.context.build_road(self.context.get_adjacent_edges(best_position)[0])

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

            