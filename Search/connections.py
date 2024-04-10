from enum import Enum
from data_preprocessing import DataFrame
import heapq
import csv
from datetime import datetime, timedelta
import copy
import time
import os
import csv

class CostFunctions(Enum):
    STOPS = 'stops'
    DISTANCE = 'distance'
    PRICE = 'price'
    ARRIVALTIME= 'arrivaltime'

class Graphs(Enum):
    MINISCHEDULE = 'mini-schedule.csv'
    SCHEDULE = 'schedule.csv'


class Connection():
    def __init__(self):
        self.schedule_graph = {}
        self.mini_schedule_graph = {}
        self.problem_data = []
        self.pb_file_name = 'problems.csv'
        self.sln_file_name = 'solutions.csv'
        self.sln_header = ['ProblemNo', 'Connection', 'Cost']  # sln columns
        self.problem_details = {}
        self.graph = {}
        self.sortest_costs = {}
        self.connection = None
        self.cost = None
        self.pb_no = None
        self.paths = []
        self.start_time_dp = None
        self.start_time_ds = None
        self.end_time_dp = None
        self.end_time_ds = None
        self.explored_neighbors = 0

    def parse_time(self, time_str):
        return datetime.strptime(time_str, "%H:%M:%S")

    def is_next_day(self, time1_str, time2_str, is_new_train = False):
        time1 = self.parse_time(time1_str)
        time2 = self.parse_time(time2_str)
        if is_new_train:
            time1 += timedelta(minutes=10)

        # If time2 is earlier than time1, it's the next day
        return time2 < time1

    def is_new_day(self, schedule_departure, schedule_n_s_arrival):
        '''
        i. if departure is greater than next station arrival

        '''
        schedule_departure = self.parse_time(schedule_departure)
        schedule_n_s_arrival = self.parse_time(schedule_n_s_arrival)

        return schedule_departure > schedule_n_s_arrival

    def is_train_missed(self, current_cost, target_train_departure, is_initial = False):
        target_train_departure_time = self.parse_time(target_train_departure)

        # Adding 10 minutes to the current train's arrival time if this is not initial time
        # handle the case 23:50+:00
        current_cost = int(current_cost.total_seconds()) % (24 * 3600)
        if not is_initial:
            current_cost += 10 * 60

        target_train_departure_delta = timedelta(hours=target_train_departure_time.hour,
                                                 minutes=target_train_departure_time.minute,
                                                 seconds=target_train_departure_time.second)

        target_train_departure_seconds = target_train_departure_delta.total_seconds()
        # Check if the target train's departure is earlier than the current train's adjusted arrival
        return target_train_departure_seconds < current_cost

    def parse_custom_time_format(self, time_str):
        parts = time_str.split(':')
        padded_parts = (['0'] * (4 - len(parts))) + parts
        days, hours, minutes, seconds = map(int, padded_parts)

        return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    def timedelta_to_custom_format(self, tdelta):
        total_seconds = int(tdelta.total_seconds())
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days:02}:{hours:02}:{minutes:02}:{seconds:02}"

    def update_timedelta(self, current_cost, time_str, is_train_missed=False, is_new_day=False):
        # Extract days from the original timedelta
        days = current_cost.days
        times = time_str.split(':')

        current_cost_seconds = int(current_cost.total_seconds()) % (24 * 3600)
        new_time_seconds = int(self.parse_custom_time_format(time_str).total_seconds()) % (24 * 3600)

        # Calculate the time difference in seconds
        time_difference = abs(new_time_seconds - current_cost_seconds)

        # Check if the time difference is more than 24 hours (86400 seconds)
        if is_train_missed or is_new_day or current_cost_seconds >= new_time_seconds or time_difference > 86400:
            days += 1
        if is_train_missed and is_new_day:
            days += 1

        # Create a new timedelta with the updated days, hours, minutes, and seconds
        updated_td = timedelta(days=days, hours=int(times[0]), minutes=int(times[1]), seconds=int(times[2]))
        return updated_td

    def dijkstra(self):

        self.explored_neighbors = 0
        if self.problem_details.get('graph') == Graphs.SCHEDULE.value:
            self.graph = self.schedule_graph
        else:
            self.graph = self.mini_schedule_graph
        # Shortest costs initialized to infinity
        self.shortest_costs = {station: float('infinity') for station in self.graph}

        arrival_time = None
        if self.problem_details['cost'] == CostFunctions.DISTANCE.value or self.problem_details['cost'] == CostFunctions.STOPS.value:
            self.shortest_costs[self.problem_details.get('source')] = 0
            cost = 0
        elif self.problem_details['cost'] == CostFunctions.PRICE.value:
            self.shortest_costs[self.problem_details.get('source')] = 1
            cost = 1
        elif self.problem_details['cost'].startswith(CostFunctions.ARRIVALTIME.value):
            long_away = self.parse_custom_time_format("10000:06:00:00")
            self.shortest_costs = {station: long_away for station in self.graph}
            time = self.parse_custom_time_format(self.problem_details['cost'].split()[1].strip())
            self.shortest_costs[self.problem_details.get('source')] = time
            cost = time
            arrival_time = self.problem_details['cost'].split()[1].strip()

        initial_path_info = StationPathInfo(cost=cost, station_code=self.problem_details.get('source'), arrival_time=arrival_time)

        priority_queue = []
        heapq.heappush(priority_queue, initial_path_info)

        # Track paths leading to nodes
        self.paths = []
        #tmp_graph = copy.deepcopy(self.graph)
        visited = []

        while priority_queue:

            current_path_info = heapq.heappop(priority_queue)

            current_cost = current_path_info.cost

            current_station = current_path_info.station_code

            if current_station == self.problem_details.get('destination'):
                self.paths = current_path_info.path
                self.cost = current_path_info.cost
                break

            # If the current node's cost is already larger than the stored shortest, skip it
            if current_cost > self.shortest_costs[current_station]:
                continue


            # Explore neighbors
            for t_id, schedule in self.graph[current_station].items():

                if schedule.get('next_station_code') is None:
                    continue

                if self.problem_details['cost'] == CostFunctions.DISTANCE.value:
                    cost = current_cost + schedule.get('distance')
                elif self.problem_details['cost'] == CostFunctions.PRICE.value:
                    if (not current_path_info.train_id is None and  (self.is_next_day(schedule['arrival_time'], schedule['next_stoppage_arrival_time']) or
                             schedule.get('train_id') != current_path_info.train_id)):
                        cost = current_cost + 1
                    else:
                        cost = current_cost
                elif self.problem_details['cost'] == CostFunctions.STOPS.value:
                    cost = current_cost + 1
                elif self.problem_details['cost'].startswith(CostFunctions.ARRIVALTIME.value):
                    is_train_missed = False
                    if  (schedule.get('train_id') != current_path_info.train_id and
                            self.is_train_missed(current_cost, schedule.get('departure_time'), current_path_info.train_id is None)):
                        is_train_missed = True
                    is_new_day = self.is_new_day(schedule.get('departure_time'), schedule.get('next_stoppage_arrival_time'))
                    cost = self.update_timedelta(current_cost, schedule.get('next_stoppage_arrival_time'), is_train_missed, is_new_day)

                # sometimes same cost from different station might come up with best solution.
                # no need for distance and stop cost functions
                if (cost < self.shortest_costs[schedule.get('next_station_code')] or
                        ((self.problem_details['cost'].startswith(CostFunctions.ARRIVALTIME.value) or self.problem_details['cost'] == CostFunctions.PRICE.value) and cost <= self.shortest_costs[schedule.get('next_station_code')])):

                    self.explored_neighbors +=1
                    self.shortest_costs[schedule.get('next_station_code')] = cost
                    path = copy.deepcopy(current_path_info.path)

                    if current_path_info.train_id == schedule.get('train_id'):
                        path[-1][1].append(schedule.get('next_stoppage'))
                    else:
                        path.append((schedule.get('train_id'), [schedule.get('stoppage'),schedule.get('next_stoppage') ]))


                    path_info = StationPathInfo(cost=cost, station_code=schedule.get('next_station_code'),
                                                parent_station_code= schedule.get('station_code'),
                                                train_id=schedule.get('train_id'), stoppage=schedule.get('stoppage'),
                                                next_stoppage=schedule.get('next_stoppage'),
                                                arrival_time=schedule.get('arrival_time'),
                                                next_station_arrival_time = schedule.get('next_stoppage_arrival_time'),
                                                path=path)

                    heapq.heappush(priority_queue, path_info)
    def raed_problems(self):
        with open(self.pb_file_name, newline='', encoding='utf-8') as csvfile:
            data_reader = csv.reader(csvfile)
            next(data_reader)
            for data in data_reader:
                self.problem_data.append(data)

    def process_data(self):

        self.start_time_dp = time.time()
        df = DataFrame('schedule.csv')
        df.process_data()
        self.end_time_dp = time.time()
        data_preprocessing_time = (self.end_time_dp - self.start_time_dp) * 1000
        print('schedule', data_preprocessing_time)

        self.start_time_dp = time.time()

        self.schedule_graph = df.graph
        df = DataFrame('mini-schedule.csv')
        df.process_data()
        self.mini_schedule_graph = df.graph
        self.end_time_dp = time.time()
        data_preprocessing_time = (self.end_time_dp - self.start_time_dp) * 1000
        print('mini, schedule', data_preprocessing_time)

    def best_connections(self):
        self.process_data()
        self.raed_problems()
        self.initialize_solution_file()
        for i, pb in enumerate(self.problem_data):
            self.problem_details['source'] = pb[1]
            self.problem_details['destination'] = pb[2]
            self.problem_details['graph'] = pb[3].strip()
            self.problem_details['cost'] = pb[4]
            self.pb_no = pb[0]
            self.start_time_ds = time.time()

            self.dijkstra()
            self.end_time_ds = time.time()

            self.write_solution()

        # end_time = time.time()
        # execution_time = end_time - start_time
        # print(f"Execution time: {execution_time} seconds")
        print('Solutions have been written in solutions.csv file')
    def prepare_solution_format(self):
        # create solution format
        self.connection = ''
        if self.shortest_costs[self.problem_details.get('destination')] != float('infinity'):
            if self.problem_details['cost'].startswith(CostFunctions.ARRIVALTIME.value):
                self.cost = self.timedelta_to_custom_format(self.cost)
                
            #print(self.pb_no, self.path)
            for i, train in enumerate(self.paths):
                self.connection += train[0] + ' : ' + train[1][0] + ' -> ' + train[1][len(train[1])-1]
                if i != (len(self.paths) -1):
                    self.connection += ' ; '

            # New part: calculating and saving the required details
            no_of_trains = len(self.paths)
            no_of_stations = sum(len(train[1]) for train in self.paths)
            path_finding_time = (self.end_time_ds - self.start_time_ds) * 1000

            self.save_to_csv(no_of_trains, no_of_stations, self.pb_file_name,  path_finding_time)
        else:
            print("There is no path from " + self.problem_details.get('source') + " to " + self.problem_details.get(
                'destination'))



    def save_to_csv(self, no_of_trains, no_of_stations, file_name, computation_time):
        # Define the file path for 'summary.csv'
        summary_file_path = 'summary.csv'

        # Check if the file exists and its size to determine if headers are needed
        file_exists = os.path.isfile(summary_file_path)
        write_headers = not file_exists or os.path.getsize(summary_file_path) == 0

        # Now open the file for appending
        with open(summary_file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # If the file is new or empty, write the headers
            if write_headers:
                writer.writerow(['pb_no', 'no_of_trains', 'no_of_stations', 'file_name','cost_function', 'computation_time', 'explored_neighbors'])

            # Write the data row
            cost = self.problem_details['cost']
            if self.problem_details['cost'].startswith('arrivaltime'):
                cost = 'arrivaltime'

            writer.writerow([self.pb_no, no_of_trains, no_of_stations, self.problem_details.get('graph').split('.')[0], cost,  computation_time, self.explored_neighbors])

    # E
    def initialize_solution_file(self):
        """
        Initializes the solution file. If the file exists, it clears the file and adds a header.
        If the file doesn't exist, it creates a new file and adds a header.
        """
        with open(self.sln_file_name, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(self.sln_header)

    def write_solution(self):
        self.prepare_solution_format()
        # Open the file in append mode
        with open(self.sln_file_name, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write the entry
            writer.writerow([self.pb_no,self.connection,self.cost])

class StationPathInfo:
    def __init__(self, cost, station_code, parent_station_code=None, train_id=None, stoppage=None, next_stoppage=None, arrival_time=None, next_station_arrival_time=None, path=[]):
        self.cost = cost
        self.station_code = station_code
        self.parent_station_code = parent_station_code
        self.train_id = train_id
        self.stoppage = stoppage
        self.next_stoppage = next_stoppage
        self.arrival_time = arrival_time
        self.next_station_arrival_time = next_station_arrival_time
        self.path = path

    # special method for heapq handling
    def __lt__(self, other):
        return self.cost < other.cost


if __name__ == "__main__":
    d = Connection()
    d.best_connections()

