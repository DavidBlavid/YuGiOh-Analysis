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

# images get rescaled to this size
# before we crop out the regions from REGION_PATH
RESIZE_WIDTH = 440
RESIZE_HEIGHT = 370


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

        # resize to the resize width and height
        image = cv2.resize(image, (RESIZE_WIDTH, RESIZE_HEIGHT))

        # convert to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # convert to PIL image
        image = Image.fromarray(image)

        # crop the image
        # here we crop out the region defined in the json file
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

    # we save information about missing games
    missing_scores_info = []

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

                if winner == 0.5:

                    score_info = {
                        'round': int(round_number),
                        'player': player,
                        'opponent': opponent,
                        'game': game,
                        'winner': winner,
                        'winner_name': winner_name,
                        'loser_name': loser_name
                    }

                    # append the missing score to the list
                    missing_scores_info.append(score_info)

                    # we dont save missing scores
                    # but we inform the user
                    continue

                writer.writerow([round_number, player, opponent, game, winner, winner_name, loser_name])
    
    print(f'Saved {len(full_results)} rounds to results.csv')

    if len(missing_scores_info) > 0:
        print(f'\n{len(missing_scores_info)} game{'s are' if len(missing_scores_info) > 1 else ' is'} missing')

        for missing_score in missing_scores_info:
            print(f'Round {missing_score["round"]}: {missing_score["game"]} ({missing_score["round"]}.png)')