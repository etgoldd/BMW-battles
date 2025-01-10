# LUMBER = <Resources.LUMBER: 0>
# BRICK = <Resources.BRICK: 1>
# GRAIN = <Resources.GRAIN: 2>
# WOOL = <Resources.WOOL: 3>
# ORE = <Resources.ORE: 4>

from api import *
import random
import math


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
    min_count_to_trade = 6

    def set_fixed_land_value_to_virtual(self):
        self.fixed_land_value = self.virtual_land_value

    def rank_land(self, position):
        land = self.context.get_land(position)
        if land is None:
            return 0
        land_num = self.context.get_number(position)
        if land_num is None:
            return 0
        land_score = self.land_num_to_score[land_num]
        value = self.virtual_land_value[land.value] * land_score
        # self.virtual_land_value[land.value] /= self.divide_when_taken[land.value]
        return value

    def rank_intersection(self, position):
        terrains = self.context.get_adjacent_terrains(position)
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
        self.context.log_info("building city")
        buildings = self.context.get_player_buildings(self.context.get_player_index())
        for pos, building in buildings:
            if building == Buildings.SETTLEMENT:
                self.context.log_info("found settlement")
                e = self.context.build_city(pos)
                if e == Exceptions.OK:
                    return True
                else:
                    return False
        return False

    def build_settlement(self):
        self.context.log_info("building settlement")
        intersections= self.context.get_intersections()
        random.shuffle(intersections)
        for intersection in intersections:
            e = self.context.build_settlement(intersection)
            self.context.log_info("built settlement")
            if e == Exceptions.OK:
                return True
            elif e == Exceptions.NOT_ENOUGH_RESOURCES:
                return False
            elif e == Exceptions.ILLEGAL_POSITION:
                pass

        return False

    def build_road(self):
        self.context.log_info("building road")
        edges= self.context.get_edges()
        random.shuffle(edges)
        for edge in edges:
            e = self.context.build_road(edge)
            if e == Exceptions.OK:
                return True
            elif e == Exceptions.NOT_ENOUGH_RESOURCES:
                return False
            elif e == Exceptions.ILLEGAL_POSITION:
                pass
        return

    def trade_with_bank(self):
        self.context.log_info("trading with bank")
        res_counts = self.context.get_resource_counts()
        min_resource = res_counts.index(min(res_counts))
        for i, count in enumerate(res_counts):
            if count >= self.min_count_to_trade:
                self.context.log_info(f"trading {i} with {min_resource}")
                self.context.maritime_trade(Resources(i), Resources(min_resource))
                return True
        return False

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
        resources = self.context.get_resource_counts()
        total = sum(resources)
        for res_index, res_count in enumerate(resources):
            resources[res_index] = math.ceil(res_count / 2)
        diff = total - sum(resources)
        for _ in range(diff):
            while True:
                dropped_res = random.randrange(0, 5)
                if resources[dropped_res] > 0:
                    resources[res_index] -= 1
                    break
        self.context.set_resources_to_drop(resources)

    def get_player_terrains(self, player_index: int) -> set[Position]:
        buildings = self.context.get_player_buildings(player_index)
        my_terrains = set()
        for building in buildings:
            building: tuple[Position, Buildings]
            my_terrains.union(self.context.get_adjacent_terrains(building[0]))
        return my_terrains
    
    def get_other_player_indexes(self) -> list[int]:
        """
        Returns a list of the player indexes that aren't ours
        """
        indexes = []
        for player_index in range(4):
            if player_index == self.context.get_player_index():
                continue
            if len(self.context.get_player_buildings(player_index)) == 0:
                indexes.append(player_index)
        return indexes

    def move_robber(self):
        """
        Generates the set of terrains that we aren't on and the enemy is on
        """
        my_terrains = self.context.get_player_terrains(self.context.get_player_index())
        random.shuffle(my_terrains)
        other_terrain_groups = [self.get_player_terrains(index) for index in self.get_other_player_indexes()]
        enemy_terrains = set()
        for other_terrains in other_terrain_groups:
            enemy_terrains.union(other_terrains)
        target_terrains: set[Position] = enemy_terrains.difference(my_terrains)

        best_target: Position = target_terrains[0]
        best_score = self.land_num_to_score[self.context.get_number(best_target)]
        for target_terrain in target_terrains:
            if self.context.get_number(target_terrain) > best_score:
                best_score = self.context.get_number(target_terrain)
                best_target = target_terrain
        for player_index in self.get_other_player_indexes():
            if self.context.move_robber(best_target, player_index) == Exceptions.OK:
                return
            
            