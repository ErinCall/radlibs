from __future__ import unicode_literals

LIBS_FOR_NOW = {
    'Animal': [
        'cat',
        'dog',
        'buffoon',
    ],
    'Song': [
        'Black Skinhead',
        'Blood On The Leaves',
    ],
    'Loot': [
        'potion of booze',
        '+5 sword of sharpness',
    ],
}

def load_lib(lib_name):
    return LIBS_FOR_NOW[lib_name]
