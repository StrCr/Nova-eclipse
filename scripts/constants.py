from scripts.resourceManager import ResourceManager
from scripts.settings import settings


resource_manager = ResourceManager(settings.images_dir)

# image load dictionary
hex_images = {
    'sun': resource_manager.load_image('Sun_Red.png'),
    'spaceship': resource_manager.load_image('spaceship.png'),
    'transport_spaceship': resource_manager.load_image('transport.png'),
    'population': resource_manager.load_image('icon_population.png'),
    'production': resource_manager.load_image('icon_gear.png'),
    'fuel': resource_manager.load_image('icon_fuel_2.png'),
    'tropical': resource_manager.load_image('Planet_Tropical.png'),
    'snowy': resource_manager.load_image('Planet_Snowy.png'),
    'ocean': resource_manager.load_image('Planet_Ocean.png'),
    'lunar': resource_manager.load_image('Planet_Lunar.png'),
    'muddy': resource_manager.load_image('Planet_Muddy.png'),
    'cloudy': resource_manager.load_image('planet_Cloudy.png'),
    'next_turn': resource_manager.load_image('icon_next_turn.png')
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
