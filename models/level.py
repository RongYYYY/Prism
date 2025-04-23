# models/level.py

from models.plate import Plates
from constants import GRAY, REDD, GREEND, BLUED

class Level:
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
