from utils import load_image

# image load dictionary
hex_images = {
    'sun': load_image('Sun_Red.png'),
    'spaceship': load_image('spaceship.png'),
    'population': load_image('icon_population.png'),
    'production': load_image('icon_gear.png'),
    'power': load_image('icon_power.png'),
    'plus': load_image('icon_plus.png'),
    'minus': load_image('icon_minus.png'),
    'icon': load_image('icon_minus.png'),
    'tropical': load_image('Planet_Tropical.png'),
    'snowy': load_image('Planet_Snowy.png'),
    'ocean': load_image('Planet_Ocean.png'),
    'lunar': load_image('Planet_Lunar.png'),
    'muddy': load_image('Planet_Muddy.png'),
    'cloudy': load_image('planet_Cloudy.png'),
    'next_turn': load_image('icon_next_turn.png')
}

# planet types dictionary
planet_types = {
    'tropical': {
        'population_growth_rate': 8,
        'production_bonus': 3,
        'image': 'tropical'
    },
    'ocean': {
        'population_growth_rate': 7,
        'production_bonus': 4,
        'image': 'ocean'
    },
    'cloudy': {
        'population_growth_rate': 6,
        'production_bonus': 5,
        'image': 'cloudy'
    },
    'snowy': {
        'population_growth_rate': 5,
        'production_bonus': 6,
        'image': 'snowy'
    },
    'muddy': {
        'population_growth_rate': 4,
        'production_bonus': 7,
        'image': 'muddy'
    },
    'lunar': {
        'population_growth_rate': 3,
        'production_bonus': 8,
        'image': 'lunar'
    }
}
