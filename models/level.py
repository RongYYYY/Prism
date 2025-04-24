# models/level.py

from models.plate import Plates
from constants import GRAY, REDD, GREEND, BLUED
import os
import pygame

IMAGE_FILENAMES = [
    "Hear.png",    # Level 1 (Heart)
    "Cloud.png",   # Level 2 (Cloud)
    "Moon.png",    # Level 3 (Moon)
    "Youtube.png", # Level 4 (YouTube)
    "Target.png",  # Level 5 (Target)
    "Map.png"      # Level 6 (Map)
]


class Level:

    level_names = ["Heart", "Cloud", "Moon", "YouTube", "Target", "Map"]
    
    level_answer = {
        3: [
            [(0, 0), GREEND, [(7, 7)]],
            [(-3, 0), BLUED, [(10, 10)]]
        ],
        2: [
            [(0, 0), BLUED, [(0, 0), (12, 0), (12, 12), (0, 12)]],
            [(3, 12), REDD, [(3, 3)]],
            [(7, 12), REDD, [(5, 5)]]
        ],
        1: [
            [(0, 0), REDD, [(0, 0), (8, 8), (16, 0), (8, -8)]],
            [(4, -4), REDD, [(5.656854249492381, 5.656854249492381)]],
            [(12, -4), REDD, [(5.656854249492381, 5.656854249492381)]]
        ],
        5: [
            [(0, 0), BLUED, [(4, 4)]],
            [(0, 0), REDD, [(7, 7)]],
            [(0, 0), GREEND, [(10, 10)]]
        ],
        4: [
            [(0, 0), REDD, [(0, 0), (13, 0), (13, 10), (0, 10)]],
            [(4, 2), GREEND, [(0, 0), (5, 3), (0, 6)]],
            [(4, 2), BLUED, [(0, 0), (5, 3), (0, 6)]]
        ],
        6: [
            [(0, 0), BLUED, [(10, 10)]],
            [(-8, 6), BLUED, [(0, 0), (8, 8), (16, 0)]],
            [(0, 0), REDD, [(5.656854249492381, 5.656854249492381)]],
            [(0, 0), GREEND, [(5.656854249492381, 5.656854249492381)]]
        ]
    }

    level_data = {
        1: [ # Heart
            {'type':1, 'color':GRAY, 'location':(10,10),'xys':[(0,0),(8,8),(16,0),(8,-8)]},
            {'type':2, 'color':GRAY, 'location':(20,20),'xys':[(4*2**0.5,4*2**0.5)]},
            {'type':2, 'color':GRAY, 'location':(15,15),'xys':[(4*2**0.5,4*2**0.5)]}
        ],
        2: [ # Cloud
            {'type':1, 'color':GRAY, 'location':(5,12),   'xys':[(0,0),(12,0),(12,12),(0,12)]},
            {'type':2, 'color':GRAY, 'location':(20,10), 'xys':[(3,3)]},
            {'type':2, 'color':GRAY, 'location':(25,15), 'xys':[(5,5)]}
        ],
        3: [ # Moon
            {'type':2, 'color':GRAY, 'location':(20,20), 'xys':[(7,7)]},
            {'type':2, 'color':GRAY, 'location':(15,15), 'xys':[(10,10)]}
        ],
        4: [ # YouTube
            {'type':1, 'color':GRAY, 'location':(5,5),  'xys':[(0,0),(13,0),(13,10),(0,10)]},
            {'type':1, 'color':GRAY, 'location':(20,15),'xys':[(0,0),(5,3),(0,6)]},
            {'type':1, 'color':GRAY, 'location':(10,20),'xys':[(0,0),(5,3),(0,6)]}
        ],
        5: [ # Target
            {'type':2, 'color':GRAY, 'location':(30,20),'xys':[(4,4)]},
            {'type':2, 'color':GRAY, 'location':(10,10),'xys':[(7,7)]},
            {'type':2, 'color':GRAY, 'location':(20,15),'xys':[(10,10)]}
        ],
        6: [ # Map
            {'type':1, 'color':GRAY, 'location':(17,5), 'xys':[(0,0),(8,8),(16,0)]},
            {'type':2, 'color':GRAY, 'location':(20,19),'xys':[(10,10)]},
            {'type':2, 'color':GRAY, 'location':(7,7),  'xys':[(4*2**0.5,4*2**0.5)]},
            {'type':2, 'color':GRAY, 'location':(8,15), 'xys':[(4*2**0.5,4*2**0.5)]}
        ]}

    def __init__(self, level_id):
        self.level_id = level_id
        self.plate_definitions = Level.level_data[level_id]
        self.answer = Level.level_answer[level_id]
        self.target = self.load_level_icon()
        self.level_name = Level.level_names[level_id - 1]

    def load(self, board):
        board.plates.clear()
        for spec in self.plate_definitions:
            plate = Plates(
                spec['type'],
                spec.get('color', GRAY),
                tuple(spec['location']),
                spec['xys']
            )
            board.add_plate(plate)

    def load_level_icon(self):
        filename = IMAGE_FILENAMES[self.level_id - 1]
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        image_dir = os.path.join(curr_dir, '..', 'images')
        path = os.path.join(image_dir, filename)
        image = pygame.image.load(path).convert_alpha()
        return image
    
    def draw_level_icon(self, screen, pos=(-100, -50), size=(400, 300)):
        icon = pygame.transform.smoothscale(self.target, size)
        # icon_rect = self.target.get_rect(center=(100, 75))
        screen.blit(icon, pos)
