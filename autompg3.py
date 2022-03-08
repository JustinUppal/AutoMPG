import csv
import sys
from collections import namedtuple
import os
import logging
import requests
import argparse
from collections import defaultdict
import matplotlib.pyplot as plt

# get the root logger, set default to INFO
logger = logging.getLogger()

# stream handler, handles command line as INFO
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)

logger.addHandler(sh)

logging.info('tracing info')

Record = namedtuple("Record",
                    ["mpg", "cylinders", "displacement", "horsepower", "weight", "acceleration", "model_year", "origin",
                     "car_name"])


class AutoMPG:
    def __init__(self, make, model, year, mpg):
        self.make = str(make)
        self.model = str(model)
        self.year = (int(year) + 1900)
        self.mpg = float(mpg)

    def __repr__(self):
        return f"Make: {self.make} Model: {self.model} Year: {self.year} MPG: {self.mpg}"

    def __str__(self):
        return f" The Make is {self.make}. The Model is {self.model}. The Year is {self.year}. The MPG is {self.mpg}. "

    def __eq__(self, other):
        return self.make == other.make and self.model == other.model and self.year == other.year and self.mpg == other.mpg

    def __lt__(self, other):
        if self.make != other.make:
            return self.make < other.make
        elif self.model != other.model:
            return self.model < other.model
        elif self.year != other.year:
            return self.year < other.year
        else:
            return self.mpg < other.mpg

    def __hash__(self):
        return hash((self.make, self.model, self.year, self.mpg))


class AutoMPGData:
    def __init__(self):
        self.data = self._load_data()

    def __iter__(self):
        self._iter = 0
        return self

    def __next__(self):
        if self._iter == len(self.data):
            raise StopIteration
        ret = self.data[self._iter]
        self._iter += 1
        return ret

    def _load_data(self):
        initial_path = '/Users/justinuppal/Documents/COMP3006/auto-mpg.data'
        if not os.path.exists(initial_path):
            self._get_data()
        final_data = []
        AutoMPGRecord = []
        path = '/Users/justinuppal/Documents/COMP3006/auto-mpg.clean.txt'
        if not os.path.exists(path):
            self._clean_data()
        clean_dict = {'chevroelt': 'chevrolet', 'chevy': 'chevrolet', 'maxda': 'mazda', 'mercedes-benz': 'mercedes',
                      'toyouta': 'toyota', 'vokswagen': 'volkswagen', 'vw': 'volkswagen'}
        with open('auto-mpg.clean.txt', mode='r') as file:
            reader = csv.reader(file)
            for line in reader:
                i = Record(mpg=line[0], cylinders=line[1], displacement=line[2], horsepower=line[3],
                           weight=line[4], acceleration=line[5], model_year=line[6], origin=line[7],
                           car_name=line[8:])
                final_data.append(i)
        for final_loop in final_data:
            j = AutoMPG(final_loop.car_name[0], " ".join(final_loop.car_name[1:]), final_loop.model_year,
                        final_loop.mpg)
            if j.make in clean_dict.keys():
                j.make = clean_dict[j.make]
            AutoMPGRecord.append(j)
        return AutoMPGRecord

    def _clean_data(self):
        with open('auto-mpg.data', mode='r') as file:
            reader = csv.reader(file, delimiter='\t')
            data = []
            for row in reader:
                text = row[0].expandtabs(2) + "  " + row[1].expandtabs(2)
                data.append(text)
        with open('auto-mpg.clean.txt', 'w', encoding='UTF8', newline='') as cleaned:
            writer = csv.writer(cleaned)
            for line in data:
                writer.writerow(line.split())

    def sort_by_default(self):
        return self.data.sort()

    def sort_by_year(self):
        # year, make, model, mpg
        self.data.sort(key=lambda auto: auto.mpg)
        self.data.sort(key=lambda auto: auto.model)
        self.data.sort(key=lambda auto: auto.make)
        return self.data.sort(key=lambda auto: auto.year)

    def sort_by_mpg(self):
        # mpg, make, model, year
        self.data.sort(key=lambda auto: auto.year)
        self.data.sort(key=lambda auto: auto.model)
        self.data.sort(key=lambda auto: auto.make)
        return self.data.sort(key=lambda auto: auto.mpg)

    def _get_data(self):
        response = requests.get('https://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data')
        with open('auto-mpg.data', 'wb') as file:
            file.write(response.content)

    def mpg_by_year(self):
        mpg_by_year_dict = defaultdict(lambda: list())
        for i in self.data:
            mpg_by_year_dict[i.year].append(i.mpg)
        for k, v in mpg_by_year_dict.items():
            average_mpg = sum(v) / len(v)
            mpg_by_year_dict[k] = average_mpg
        return mpg_by_year_dict

    def mpg_by_make(self):
        mpg_by_make_dict = defaultdict(lambda: list())
        for i in self.data:
            mpg_by_make_dict[i.make].append(i.mpg)
        for k, v in mpg_by_make_dict.items():
            average_mpg = sum(v) / len(v)
            mpg_by_make_dict[k] = average_mpg
        return mpg_by_make_dict


def main():
    parser = argparse.ArgumentParser(description='Parse data from AutoMPG Record')
    parser.add_argument('-s', type=str, help='This argument will return a certain sort order')
    parser.add_argument('-DEBUG', help='This will add to the debug logs')
    parser.add_argument('-o', type=str,
                        help='specify the name of a file to which output should be written')
    parser.add_argument('-p', action='store_true',
                        help='allows the user to specify that graphical output using matplotlib should be created.')
    parser.add_argument('-d', choices=['make', 'year'],
                        help='return a dictionary of average MPG sorted by make or year.')
    parser.add_argument('command', help='this will print the information you have specified ')

    args = parser.parse_args()

    test = AutoMPGData()

    if args.command == 'print':
        if args.s == 'mpg':
            test.sort_by_mpg()
        if args.s == 'year':
            test.sort_by_year()
        if args.s == 'default':
            test.sort_by_default()
        if args.o:
            with open(args.o, 'w') as f:
                f.write('Make,Model,Year,MPG\n')
                for i in test:
                    f.write('{},{},{},{}\n'.format(i.make, i.model, i.year, i.mpg))
        if not args.o:
            for i in test:
                sys.stdout.write('{},{},{},{}\n'.format(i.make, i.model, i.year, i.mpg))

    final_dict = dict()
    if args.d == 'make':
        initial_dict = test.mpg_by_make()
        initial_list = []
        for i in sorted(initial_dict.keys()):
            initial_list.append((i, initial_dict[i]))
        final_dict = initial_list
        header = 'This is the average MPG by Make'
        if args.p:
            x = []
            y = []
            for k, v in final_dict:
                x.append(k)
                y.append(v)
            plt.scatter(x, y, alpha=.5)
            plt.title('{}'.format(header))
            plt.xlabel('Make')
            plt.ylabel('Average MPG')
            plt.show()
    if args.d == 'year':
        initial_dict2 = test.mpg_by_year()
        initial_list2 = []
        for i in sorted(initial_dict2.keys()):
            initial_list2.append((i, initial_dict2[i]))
        final_dict = initial_list2
        header = 'Average MPG by Year'
        if args.do_plot:
            x = []
            y = []
            for k, v in final_dict:
                x.append(k)
                y.append(v)
            plt.scatter(x, y, alpha=.5)
            plt.title('{}'.format(header))
            plt.xlabel('year')
            plt.ylabel('Average MPG')
            plt.show()
    if final_dict and args.o:
        with open(args.o, 'a') as f:
            f.write('{}\n'.format(header))
            for i in final_dict:
                f.write('{},{}\n'.format(i[0], i[1]))
    elif final_dict:
        for i in final_dict:
            sys.stdout.write('{},{}\n'.format(i[0], i[1]))


#       test.sort_by_default()
#       print(test.data)
#       test.sort_by_year()
#       print(test.data)
#       test.sort_by_mpg()
#       print(test.data)
#       test._get_data()
#     print(test.mpg_by_year())
#     print(test.mpg_by_make())

if __name__ == "__main__":
    main()
