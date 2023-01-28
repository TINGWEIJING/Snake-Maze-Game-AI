import math
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt

'''
The idea behind this is to have relatively well distributed obstacles across all 4 sectors of the map. Ideally, we would have a 35:65 obstacle to path ratio throughout the map, as such, cross entropy is used to compare the distribution of obstacles from the algorithm to the ideal distribution. Additionally, we purposely split the map into 4 sectors and calculate its average for this evaluation function is such that the distribution isn't too lopsided for any particular sector. I.e. the algorithm could hypothetically generate 35% of its cells as wall cells ONLY on the bottom right of the map, if we only calculate a general cross-entropy score for the entire map, we would not be able to determine whether there's anything wrong.

Steps for the fitness function:
1. Split the map into 4 equal sectors
2. Calculate the cross entropy for each sector against a targeted distribution of 35% walls, 65% open space
3. Obtain an average of the cross entropy values, the higher the average cross entropy, the worse the map generated
'''

ON = 1

CLR_MAP = {
    0: (0, 0, 0),  # black, wall
    1: (255, 255, 255),  # white, space/path
    2: (237, 28, 36),  # red, src
    3: (237, 28, 36),  # red, dest
    4: (255, 201, 14),  # blue violet, room
    5: (34, 177, 76),  # orange, route
    6: (255, 105, 180),  # hot pink, alternate main route
}


def splitMap(map_np: np.ndarray):
    # To split the map into 4 sectors,
    # all we need to do is to split each axis by half
    height = map_np.shape[0]
    width = map_np.shape[1]

    height_midpoint = height//2
    width_midpoint = width//2
    return height_midpoint, width_midpoint


def crossEntropyEval(sector_np: np.ndarray):
    # Takes in a slice of the usual map_np

    # First we calculate the total area of the sector:
    area = sector_np.shape[0] * sector_np.shape[1]
    wallCount = 0
    pathCount = 0

    # Next we obtain the number of wall cells and
    # derive path cell count from it
    # Boundaries should not be included as part of sector_np
    for y in range(0, sector_np.shape[0]-1):
        for x in range(0, sector_np.shape[1]-1):
            if sector_np[y, x] == ON:
                wallCount += 1
    pathCount = area - wallCount

    crossEntropy = -(35/100*math.log(wallCount/area) + 65/100*math.log(pathCount/area))
    return crossEntropy


def evaluate_map(map_np: np.ndarray):
    map_height = map_np.shape[0]
    map_width = map_np.shape[1]
    height_midpoint, width_midpoint = splitMap(map_np)

    sector1 = map_np[1:height_midpoint, 1:width_midpoint]
    sector2 = map_np[1:height_midpoint, width_midpoint:map_width-1]
    sector3 = map_np[height_midpoint:map_height-1, 1:width_midpoint]
    sector4 = map_np[height_midpoint:map_height-1, width_midpoint:map_width-1]

    sectors = [sector1, sector2, sector3, sector4]

    crossEntropySum = 0
    for sector in sectors:
        crossEntropySum += crossEntropyEval(sector)

    avgCrossEntropy = crossEntropySum/4
    return avgCrossEntropy


def generate_init_map(map_height: int, map_width: int):
    # * height is y, width is x
    # * so map_np[y,x]
    # * origin point is at top left
    init_map_np = np.zeros((map_height, map_width), dtype=np.uint8)

    # border wall
    # top
    init_map_np[0, :] = 1
    # bottom
    init_map_np[map_height - 1, :] = 1
    # left
    init_map_np[:, 0] = 1
    # right
    init_map_np[:, map_width - 1] = 1
    return init_map_np


def plot_map(map_np: np.ndarray, map_height: int, map_width: int):
    # convert to RGB Map
    color_map_np = np.zeros((map_np.shape[0], map_np.shape[1], 3), dtype=np.uint8)

    for y in range(map_np.shape[0]):
        for x in range(map_np.shape[1]):
            color = CLR_MAP[map_np[y, x]]
            color_map_np[y, x] = np.array(color)

    plt.figure(facecolor='black')
    plt.tight_layout()
    plt.axis("off")   # turns off axes
    plt.axis("tight")  # gets rid of white border
    plt.axis("image")  # square up the image instead of filling the "figure" space
    plt.gca().set_axis_off()
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0,
                        hspace=0, wspace=0)
    plt.margins(0, 0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.xlim([-2, map_width + 1])
    plt.ylim([map_height + 1, -2])
    plt.imshow(color_map_np, interpolation='nearest')
    # plt.gcf().set_dpi(300)
    # plt.savefig("test.png",bbox_inches='tight')
    plt.show()


def output_map_file(map_np: np.ndarray, file_name: str, file_dir: str = '../map'):
    file_dir_path = Path(file_dir)
    file_dir_path.mkdir(exist_ok=True)
    output_path = file_dir_path / file_name
    with open(str(output_path), "w") as file:
        # Writing data to a file
        for y in range(map_np.shape[0]):
            file.write(''.join(map(str, map_np[y, :].tolist()))+'\n')
