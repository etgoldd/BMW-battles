# LUMBER = <Resources.LUMBER: 0>
# BRICK = <Resources.BRICK: 1>
# GRAIN = <Resources.GRAIN: 2>
# WOOL = <Resources.WOOL: 3>
# ORE = <Resources.ORE: 4>

from api import *
from typing import Tuple

class MyBot(CatanBot):
    fixed_land_value = [16, 16, 16, 16, 16, 0]
    virtual_land_value = [16, 16, 16, 16, 16, 0]
    divide_when_taken = [2, 2, 2, 2, 2, 2]

    land_num_to_score = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}

    def set_virtual_land_value_to_fixed(self):
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
        self.set_virtual_land_value_to_fixed()
        return res
    
    def setup(self):
        pass

    def play(self):
        pass

    def place_settlements_and_roads(self):
        pass
