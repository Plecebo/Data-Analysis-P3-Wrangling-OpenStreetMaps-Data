# -*- coding: utf-8 -*-
# Find the time and value of max load for each of the regions
# COAST, EAST, FAR_WEST, NORTH, NORTH_C, SOUTHERN, SOUTH_C, WEST
# and write the result out in a csv file, using pipe character | as the delimiter.
# An example output can be seen in the "example.csv" file.

import xlrd
import os
import csv
from zipfile import ZipFile

datafile = "2013_ERCOT_Hourly_Load_Data.xls"
outfile = "2013_Max_Loads.csv"


def open_zip(datafile):
    with ZipFile('{0}.zip'.format(datafile), 'r') as myzip:
        myzip.extractall()

def max_cv(cv):
    return max(cv)

def position_max_cv(cv):
    return cv.index(max_cv(cv))+1

def date_cv(cv, sheet):
    col = 0
    row = position_max_cv(cv)

    return xlrd.xldate_as_tuple(sheet.cell_value(row, col),0)

def parse_file(datafile):
    workbook = xlrd.open_workbook(datafile)
    sheet = workbook.sheet_by_index(0)
    coast_cv = sheet.col_values(1,start_rowx=1,end_rowx=None)
    east_cv = sheet.col_values(2,start_rowx=1,end_rowx=None)
    far_west_cv = sheet.col_values(3,start_rowx=1,end_rowx=None)
    north_cv = sheet.col_values(4,start_rowx=1,end_rowx=None)
    north_c_cv = sheet.col_values(5,start_rowx=1,end_rowx=None)
    southern_cv = sheet.col_values(6,start_rowx=1,end_rowx=None)
    south_c_cv = sheet.col_values(7,start_rowx=1,end_rowx=None)
    west_cv = sheet.col_values(8,start_rowx=1,end_rowx=None)

    data = [{
        'Station':'COAST',
        'Year': date_cv(coast_cv,sheet)[0],
        'Month': date_cv(coast_cv,sheet)[1],
        'Day': date_cv(coast_cv,sheet)[2],
        'Hour': date_cv(coast_cv,sheet)[3],
        'Max Load': max_cv(coast_cv)
    },
        {
        'Station':'EAST',
        'Year': date_cv(east_cv,sheet)[0],
        'Month': date_cv(east_cv,sheet)[1],
        'Day': date_cv(east_cv,sheet)[2],
        'Hour': date_cv(east_cv,sheet)[3],
        'Max Load': max_cv(east_cv)},
        {
        'Station':'FAR_WEST',
        'Year': date_cv(far_west_cv,sheet)[0],
        'Month': date_cv(far_west_cv,sheet)[1],
        'Day': date_cv(far_west_cv,sheet)[2],
        'Hour': date_cv(far_west_cv,sheet)[3],
        'Max Load': max_cv(far_west_cv)},
        {
        'Station':'NORTH',
        'Year': date_cv(north_cv,sheet)[0],
        'Month': date_cv(north_cv,sheet)[1],
        'Day': date_cv(north_cv,sheet)[2],
        'Hour': date_cv(north_cv,sheet)[3],
        'Max Load': max_cv(north_cv)},
        {
        'Station':'NORTH_C',
        'Year': date_cv(north_c_cv,sheet)[0],
        'Month': date_cv(north_c_cv,sheet)[1],
        'Day': date_cv(north_c_cv,sheet)[2],
        'Hour': date_cv(north_c_cv,sheet)[3],
        'Max Load': max_cv(north_c_cv)},
        {
        'Station':'SOUTHERN',
        'Year': date_cv(southern_cv,sheet)[0],
        'Month': date_cv(southern_cv,sheet)[1],
        'Day': date_cv(southern_cv,sheet)[2],
        'Hour': date_cv(southern_cv,sheet)[3],
        'Max Load': max_cv(southern_cv)},
        {
        'Station':'SOUTH_C',
        'Year': date_cv(south_c_cv,sheet)[0],
        'Month': date_cv(south_c_cv,sheet)[1],
        'Day': date_cv(south_c_cv,sheet)[2],
        'Hour': date_cv(south_c_cv,sheet)[3],
        'Max Load': max_cv(south_c_cv)},
        {
        'Station':'WEST',
        'Year': date_cv(west_cv,sheet)[0],
        'Month': date_cv(west_cv,sheet)[1],
        'Day': date_cv(west_cv,sheet)[2],
        'Hour': date_cv(west_cv,sheet)[3],
        'Max Load': max_cv(west_cv)}
    ]

    return data

def save_file(data, filename):
    with open(filename, 'w') as csvfile:
        fieldnames = ['Station', 'Year', 'Month','Day','Hour','Max Load']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter="|")
        writer.writeheader()
        writer.writerows(data)

    
def test():
    open_zip(datafile)
    data = parse_file(datafile)
    save_file(data, outfile)

    number_of_rows = 0
    stations = []

    ans = {'FAR_WEST': {'Max Load': '2281.2722140000024',
                        'Year': '2013',
                        'Month': '6',
                        'Day': '26',
                        'Hour': '17'}}
    correct_stations = ['COAST', 'EAST', 'FAR_WEST', 'NORTH',
                        'NORTH_C', 'SOUTHERN', 'SOUTH_C', 'WEST']
    fields = ['Year', 'Month', 'Day', 'Hour', 'Max Load']

    with open(outfile) as of:
        csvfile = csv.DictReader(of, delimiter="|")
        for line in csvfile:
            station = line['Station']
            if station == 'FAR_WEST':
                for field in fields:
                    # Check if 'Max Load' is within .1 of answer
                    if field == 'Max Load':
                        max_answer = round(float(ans[station][field]), 1)
                        max_line = round(float(line[field]), 1)
                        assert max_answer == max_line

                    # Otherwise check for equality
                    else:
                        assert ans[station][field] == line[field]

            number_of_rows += 1
            stations.append(station)

        # Output should be 8 lines not including header
        assert number_of_rows == 8

        # Check Station Names
        assert set(stations) == set(correct_stations)

        
if __name__ == "__main__":
    test()
