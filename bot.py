from api import *
import random
import math


class PRICES:
    ROAD = ResourceCounts(lumber=1, brick=1),
    SETTLEMENT = ResourceCounts(lumber=1, brick=1, grain=1, wool=1)
    CITY = ResourceCounts(grain=2, ore=3)
    DEVELOPMENT_CARD = ResourceCounts(grain=1, wool=1, ore=1)

class MyBot(CatanBot):
    # [LUMBER, BRICK, GRAIN, WOOL, ORE, DESERT]
    fixed_land_value = [16, 16, 16, 16, 16, 0]
    virtual_land_value = [16, 16, 16, 16, 16, 0]
    divide_when_taken = [0.7, 0.7, 0.7, 0.7, 0.7, 0.7]

    land_num_to_score = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1, 7: 0}
    min_count_to_trade = 6
    development_card_chance = 3

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
        return value

    def rank_intersection(self, position):
        terrains = self.context.get_adjacent_terrains(position)
        self.virtual_land_value = self.fixed_land_value[::]
        res = sum(self.rank_land(land_pos) for land_pos in terrains)
        self.set_fixed_land_value_to_virtual()
        return res

    def setup(self):
        self.current_stage = 1
        self.city_amounts = 0

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
        elif self.try_build_development_cards():
            return
        return

    def try_build_development_cards(self):
        if random.randint(0, self.development_card_chance):
            if self.context.buy_development_card() == Exceptions.OK:
                return True
        return False

    def before_dice(self):
        dev_cards:  DevelopmentCardCounts = self.context.get_development_cards()
        if dev_cards[DevelopmentCards.YEAR_OF_PLENTY] > 0:
            requested_counts: ResourceCounts = ResourceCounts()
            requested_counts[self.most_needed_resource()] = 2  # Request all.
            self.context.play_year_of_plenty(requested_counts)
        elif dev_cards[DevelopmentCards.MONOPOLY] > 0:
            self.context.play_monopoly(self.most_needed_resource())
        elif dev_cards[DevelopmentCards.ROAD_BUILDING] > 0:
            pass # self.context.play_road_building(self.)  # TODO: fix
        elif dev_cards[DevelopmentCards.KNIGHT] > 0:
            self.context.play_knight()

    def build_city(self):
        buildings = self.context.get_player_buildings(self.context.get_player_index())
        for pos, building in buildings:
            if building == Buildings.SETTLEMENT:
                e = self.context.build_city(pos)
                if e == Exceptions.OK:
                    self.city_amounts += 1
                    return True
                else:
                    return False
        return False

    def build_settlement(self):
        intersections= self.context.get_intersections()
        random.shuffle(intersections)
        for intersection in intersections:
            e = self.context.build_settlement(intersection)
            if e == Exceptions.OK:
                self.context.log_info("built settlement")
                return True
            elif e == Exceptions.NOT_ENOUGH_RESOURCES:
                return False
            elif e == Exceptions.ILLEGAL_POSITION:
                pass

        return False

    def build_road(self):
        edges= self.context.get_edges()
        random.shuffle(edges)
        for edge in edges:
            e = self.context.build_road(edge)
            if e == Exceptions.OK:
                self.context.log_info("built road")
                return True
            elif e == Exceptions.NOT_ENOUGH_RESOURCES:
                return False
            elif e == Exceptions.ILLEGAL_POSITION:
                pass
        return

    def most_needed_resource(self):
        res_counts = self.context.get_resource_counts()
        return Resources(res_counts.index(min(res_counts)))

    def trade_with_bank(self):
        res_counts = self.context.get_resource_counts()
        min_resource = self.most_needed_resource()
        for i, count in enumerate(res_counts):
            if count >= self.min_count_to_trade:
                self.context.log_info(f"trading {i} with {min_resource}")
                self.context.maritime_trade(i, Resources(min_resource))
                return True
        return False

    def place_settlement_and_road(self):
        position_ranks = [(position, self.rank_intersection(position))
                          for position in self.context.get_intersections()]
        self.context.log_info(position_ranks)
        position_ranks.sort(key=lambda x: x[1], reverse=True)
        self.context.log_info(position_ranks)
        for pos in position_ranks:
            e = self.context.build_settlement(pos[0])
            if e == Exceptions.OK:
                self.context.log_info(f"built settlement at {pos[0]}")
                self.context.build_road(self.context.get_adjacent_edges(pos[0])[0])
                break

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
            my_terrains = my_terrains.union(self.context.get_adjacent_terrains(building[0]))
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
        my_terrains = self.get_player_terrains(self.context.get_player_index())
        target_terrains = set(self.context.get_terrains()).difference(my_terrains)
        target_terrains.remove((0,0))
        best_score = 0
        best_target = None
        for target_terrain in target_terrains:
            if self.context.get_number(target_terrain) is not None and self.land_num_to_score.get(self.context.get_number(target_terrain)) > best_score:
                best_score = self.land_num_to_score.get(self.context.get_number(target_terrain))
                best_target = target_terrain
        if self.context.move_robber(best_target, -1) != Exceptions.ILLEGAL_PLAYER_INDEX:
            return
            
            