import os, json

AGENT_HOME = [[-3, 6], [-3, 5], [-2, 5], [-3, 4], [-2, 4], [-1, 4]]


class Agent:

    def __init__(self, request_dict):
        self.request_dict = request_dict
        file_path = 'heuristics.json'
        self.env = {}
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                self.env = json.load(file)

        self.active_pegs = self.get_active_pegs(self.request_dict['A'])


    def get_move(self):

        #print(request_dict['A'])

        agent_moves = []
        if len(self.active_pegs):
            # formatted_key = f"[{str(active_pegs[0][0])}, {str(active_pegs[0][1])}]"
            # possible_moves = self.env.get(formatted_key).get('neighbors')
            # agent_moves.append(active_pegs[0])
            # agent_moves.append(possible_moves[0])
            agent_moves = self.get_best_moves()
        # print(agent_moves)
        # print(self.request_dict)
        return agent_moves

    def get_active_pegs(self, my_pegs_position):

        return [pos for pos in my_pegs_position if pos not in AGENT_HOME]




    def get_best_moves(self):
        best_reward = float('-inf')

        sorted_active_pegs = sorted(self.active_pegs, key=lambda peg: peg[1], reverse=False)  # Sort by y-coordinate
        best_move = [sorted_active_pegs[0]]
        #print(sorted_active_pegs)
        for peg in sorted_active_pegs:

            # Check for hop moves
            hop_path, hop_reward = self.handle_hops(peg)
            if hop_path and len(hop_path) > 1 and hop_reward > best_reward:
                best_reward = hop_reward
                best_move = hop_path

            # Check for simple moves
            simple_move, simple_reward = self.get_best_simple_move(peg)
            if  simple_reward > best_reward:
                best_reward = simple_reward
                if(peg == sorted_active_pegs[0]):
                    best_reward += .75
                best_move = simple_move
        return best_move

    def get_best_simple_move(self, peg):
        peg_formatted_key = json.dumps(peg)
        neighbors = self.env.get(peg_formatted_key, {}).get('neighbors', [])
        best_reward = float('-inf')
        best_move = None

        for neighbor in neighbors:

            if not self.position_occupied(neighbor):
                neighbor_reward = self.get_moving_reward(peg, neighbor, 'single')

                if neighbor_reward > best_reward:
                    best_reward = neighbor_reward
                    best_move = [peg, neighbor]

        return best_move, best_reward

    def handle_hops(self, peg):
        # check for each peg till the end
        queue = [(peg, [peg])]
        best_hop = {'position': None, 'reward': float('-inf'), 'path': []}
        visited = set()

        while queue:
            current_peg, path = queue.pop(0)
            visited.add(tuple(current_peg))

            for direction in self.get_all_directions(current_peg):
                next_hop = self.calculate_next_hop(current_peg, direction)

                if json.dumps(next_hop) not in self.env:
                    continue

                if next_hop and tuple(next_hop) not in visited:
                    new_path = path + [next_hop]
                    reward = self.get_moving_reward(path[0], next_hop, 'hop')

                    if reward > best_hop['reward']:
                        best_hop = {'position': next_hop, 'reward': reward, 'path': new_path}

                    queue.append((next_hop, new_path))
                    visited.add(tuple(next_hop))

        return best_hop['path'], best_hop['reward']
    def calculate_next_hop(self, current_peg, direction):
        over_peg = [current_peg[0] + direction[0], current_peg[1] + direction[1]]
        landing_pos = [over_peg[0] + direction[0], over_peg[1] + direction[1]]

        if self.is_valid_hop(over_peg, landing_pos):
            return landing_pos
        return None

    def is_valid_hop(self, over_peg, landing_pos):
        return (self.position_occupied(over_peg) and not self.position_occupied(landing_pos))

    def position_occupied(self, pos):
        return any(pos in pegs for pegs in self.request_dict.values())


    def get_all_directions(self, peg):
        # Return all 6 possible directions in a hexagonal grid
        return [(1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1)]

    def get_heuristic(self, position):
        # Retrieve the heuristic value for the position from the board data
        pos_key = json.dumps(position)
        if pos_key in self.env:
            return self.env[pos_key]['heuristic']
        else:
            return float('inf')

    def get_moving_reward(self, source, target, type='hop'):
        # Retrieve the heuristic value for the position from the board data
        source_key = json.dumps(source)
        target_key = json.dumps(target)
        if source_key in self.env and target_key in self.env:
             reward = self.env[source_key]['heuristic'] - self.env[target_key]['heuristic']

             # if reward < 0:
             #     reward -= 1000
             #
             if source[1] > target[1]:
                 reward -= 2  # Penalize backward moves
             if source[0] == target[0]:
                 reward -= 1  # Penalize pure lateral moves
                 # if source[0] < target[0]:
                 #     reward -= 100

             return reward
        else:
            return float('-inf')



if __name__ == '__main__':
    AGENT_HOME = [[-3, 6], [-3, 5], [-2, 5], [-3, 4], [-2, 4], [-1, 4]]

    request_dict = {'A': [[-3, 6], [-3, 5], [-2, 5], [2, -5], [2, -4]], 'B': [[-1, 2], [2, 0], [-2, 2], [1, -4], [3, -6]],
     'C': [[1, -2], [5, -2], [-3, 0], [3, -1], [6,
                                                -3]]}

    print(request_dict.values())
    agent = Agent(request_dict)

    print(agent.get_move())

