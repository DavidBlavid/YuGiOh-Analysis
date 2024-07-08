import cv2
import os
import json
from tqdm import tqdm
import easyocr
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import csv
import re

from Region import Region

IMAGE_PATH = 'img'
REGION_PATH = 'points.json'
VERBOSE = True


def get_image_paths(path=IMAGE_PATH):
    """
    Returns a list of all image paths in the given directory
    """
    images = os.listdir(path)
    image_paths = [os.path.join(path, image) for image in images]
    return image_paths

def get_region_data(path=REGION_PATH):
    """
    Returns the region data from the given json file
    """

    regions_dict = []

    with open('points.json', 'r') as f:
        regions_dict = json.load(f)
    
    return regions_dict

def get_image_results(image_path, regions_dict):

    regions = []
    final_regions_dict = {}

    for current_region in regions_dict:

        TL = current_region['TL']
        TR = current_region['TR']
        BL = current_region['BL']
        BR = current_region['BR']

        # get the image region
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = image.crop((TL[0], TL[1], BR[0], BR[1]))

        # convert the image to a numpy array
        image = np.array(image)

        region = Region(
            current_region['player'],
            current_region['opponent'],
            current_region['game'],
            current_region['TL'],
            current_region['TR'],
            current_region['BL'],
            current_region['BR'],
            image
        )

        regions.append(region)
        final_regions_dict[current_region['game']] = region
    
    results = {}

    for region_index in range(0, len(regions)-1, 2):
        region1 = regions[region_index]
        region2 = regions[region_index + 1]

        region2.game = region1.game

        game = region1.game
        win = region1.get_win()

        results[game] = win
    
    return results, final_regions_dict

def get_full_results(image_base_path=IMAGE_PATH, regions_dict=REGION_PATH, save=False):

    image_paths = get_image_paths(image_base_path)
    regions_data = get_region_data(regions_dict)
    
    full_results = {}
    full_regions = {}

    for image_path in tqdm(image_paths, leave=False):

        round_number = int(re.search(r'\d+', image_path).group(0))

        results, regions = get_image_results(image_path, regions_data)

        full_results[round_number] = results
        full_regions[round_number] = regions

    if save:
        # save to results.json
        with open('results.json', 'w') as f:
            json.dump(full_results, f, indent=4)
    
    return full_results, full_regions

if __name__ == '__main__':

    full_results, full_regions = get_full_results()

    missing_scores_counter = 0

    with open('results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['round', 'player', 'opponent', 'game', 'winner', 'winner_name', 'loser_name'])

        for round_number, results in full_results.items():

            # remove leading zeros
            round_number = int(round_number)

            for game, winner in results.items():
                player, opponent = game.split('-')

                winner_name = player if winner == 1 else opponent
                loser_name = player if winner == 0 else opponent

                writer.writerow([round_number, player, opponent, game, winner, winner_name, loser_name])

                if winner == '0.5':
                    missing_scores_counter += 1

    
        
    print(f'Saved {len(full_results)} rounds to results.csv')

    if missing_scores_counter > 0:
        print(f'{missing_scores_counter} scores missing!')