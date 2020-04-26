import csv

def get_coordinates():
    coordinates = []
    with open('CharlottesvillePopulationData.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                # print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                lat_coor = float(row[6])
                long_coor = float(row[6])
                print(f'Coordinates: {lat_coor}, {long_coor}')
                line_count += 1
                coordinates.append((lat_coor, long_coor))
                if(line_count > 10):
                    break
        print(f'Processed {line_count} lines.')
        return coordinates


print(get_coordinates())