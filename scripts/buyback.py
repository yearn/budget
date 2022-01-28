# process buyback table from yfistats.com

import csv
import json

BUYBACK = "Ignore:Buying YFI"
INPUT = "reports/2022-01-28-yfi-crv-buy-backs.csv"
OUPUT = "reports/2022-01-28-yfi-crv-buy-backs.json"


def process():
    data = []
    with open(INPUT, "r") as csv_file:
        column_to_name = {"timestamp": 1, "yfiAmount": 6, "usdValue": -2, "tokenAmount": -3, "token": -4, "hash": 2}
        csv_reader = csv.reader(csv_file, delimiter=",")
        for lines in csv_reader:
            if lines[-1] == BUYBACK:
                j = {}
                for col, i in column_to_name.items():
                    j[col] = lines[i]
                data.append(j)

    with open(OUPUT, "w") as json_file:
        json.dump(data, json_file)


def main():
    process()
    print("Done!")
