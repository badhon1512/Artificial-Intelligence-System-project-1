import csv

class DataFrame():

    def __init__(self, file_name):
        self.file_name = file_name
        self.raw_data = []
        self.graph = {}

    def get_data(self):
        with open(self.file_name, newline='', encoding='utf-8') as csvfile:
            data_reader = csv.reader(csvfile)
            next(data_reader)
            for data in data_reader:
                self.raw_data.append(data)

    def process_data(self):
       self.get_data()
       s= 0

       for i in range(len(self.raw_data) - 1):
           s +=1
           schedule = self.raw_data[i]
           station = schedule[3].strip()

           updated_schedule = {}
           updated_schedule['train_id'] = schedule[0].strip("'")
           updated_schedule['stoppage'] = schedule[2]
           updated_schedule['next_stoppage'] = None
           updated_schedule['station_code'] = station
           updated_schedule['arrival_time'] = schedule[5].strip("'")
           updated_schedule['departure_time'] = schedule[6].strip("'")
           updated_schedule['distance'] = 0
           updated_schedule['next_station_code'] = None

           if (len(self.raw_data) - 1) != i and schedule[0] == self.raw_data[i + 1][0]:  # Check if it's the same train
               updated_schedule['distance'] = int(self.raw_data[i + 1][7]) - int(schedule[7])
               updated_schedule['next_station_code'] = self.raw_data[i + 1][3].strip()
               updated_schedule['next_stoppage'] = self.raw_data[i + 1][2]
               updated_schedule['next_stoppage_arrival_time'] = self.raw_data[i + 1][5].strip("'")

           if station not in self.graph:
               self.graph[station] = {}

           self.graph[station][schedule[0]] = updated_schedule


       #print(self.file_name, len(self.graph), s, len(self.raw_data))
if __name__ == "__main__":
    d = DataFrame('mini-schedule.csv')
    d.process_data()
    print(len(d.graph))
