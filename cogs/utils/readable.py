import random
import typing

import voxelbotutils as vbu


# function that takes a number and returns a string of that number in roman numerals
def roman_numeral(integer: int) -> str:
    numerals = [
        ('M', 1000),
        ('CM', 900),
        ('D', 500),
        ('CD', 400),
        ('C', 100),
        ('XC', 90),
        ('L', 50),
        ('XL', 40),
        ('X', 10),
        ('IX', 9),
        ('V', 5),
        ('IV', 4),
        ('I', 1),
    ]
    result = []
    for numeral, value in numerals:
        while integer >= value:
            result.append(numeral)
            integer -= value
    return ''.join(result)

def readable_list(bot: vbu.Bot, size: typing.Optional[int] = None, items: typing.Optional[list] = None):
    if items:
        readable_items = [f'a {bot.get_emoji(i.emoji)} **{i.name}**' if i.amount == 1 else f'{i.amount} {bot.get_emoji(i.emoji)} **{i.name}**s' for i in items]
        
        if size:
            return ', '.join(readable_items) + f' and **{size} {"inch" if size == 1 else "inches"}**'
        return ' and '.join(readable_items) if len(readable_items) <= 2 else ', '.join(readable_items)
    
    return  f'**{size} inches**'


def random_name(*, include_url: typing.Optional[bool] = False) -> typing.Union[str, set]:
    """
    Get neat lil random name

        Returns:
            person (set) if include_url: Set containing random name and URL
            name (str) if not include_url: Random name
    """

    person = random.choice([
        ('Obama', 'https://upload.wikimedia.org/wikipedia/commons/8/8d/President_Barack_Obama.jpg'),
        ('Dick roberts', 'https://upload.wikimedia.org/wikipedia/en/9/9a/Trollface_non-free.png'),
        ('Johnny from Johhny Johhny yes papa', 'https://i.kym-cdn.com/entries/icons/original/000/018/357/johny.jpg'),
        ('Shrek', 'https://i.kym-cdn.com/photos/images/original/000/744/400/8d2.jpg'),
        ('Schlöpp', 'https://cdn.discordapp.com/avatars/393305855929483264/4a587bef97a8a5e8e82e7bfad205aa40.webp?size=256'),
        ('Bob', 'https://www.dictionary.com/e/wp-content/uploads/2019/11/coomer-2.png'),
        ('Walter', 'https://i.kym-cdn.com/entries/icons/original/000/031/015/cover5.jpg'),
        ('Napoleon bonaparte', 'https://upload.wikimedia.org/wikipedia/commons/9/91/David_napoleon.jpg'),
        ('Bob ross', 'https://upload.wikimedia.org/wikipedia/en/7/70/Bob_at_Easel.jpg'),
        ('Thanos', 'https://media.discordapp.net/attachments/861715293615947868/861722164872347688/thanos_icon.png'),
        ('Don Vito', 'https://upload.wikimedia.org/wikipedia/en/e/ef/Vincent_Margera.jpg'),
        ('Bill cosby', 'https://media.discordapp.net/attachments/861715293615947868/861717855975243786/unknown.png'),
        ('Your step-sis', 'https://i.kym-cdn.com/entries/icons/original/000/027/905/Screen_Shot_2018-12-19_at_12.36.40_PM.jpg'),
        ('Pp god', 'https://upload.wikimedia.org/wikipedia/commons/7/7c/Cima_da_Conegliano%2C_God_the_Father.jpg'),
        ('Random guy', 'https://upload.wikimedia.org/wikipedia/en/c/cc/Wojak_cropped.jpg'),
        ('Genie', 'https://media.discordapp.net/attachments/861715293615947868/861719344384049172/unknown.png'),
        ('Your mom', 'https://static7.depositphotos.com/1066655/774/i/950/depositphotos_7746239-stock-photo-angry-mother-and-frying-pan.jpg'),
        ('Your daughter', 'https://media.discordapp.net/attachments/861715293615947868/861719759577415712/unknown.png'),
        ('Big Man Tyrone', 'https://www.famousbirthdays.com/headshots/based-tyrone-4.jpg'),
        ('Vin Diesel', 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Vin_Diesel_by_Gage_Skidmore_2.jpg/266px-Vin_Diesel_by_Gage_Skidmore_2.jpg'),
        ('Ben Shapiro', 'https://media.discordapp.net/attachments/861715293615947868/861720348793896970/unknown.png'),
        ('Local bitch-boy', 'https://media.discordapp.net/attachments/861715293615947868/861720556901761065/unknown.png'),
        ('Average pp bot enjoyer', 'https://i.kym-cdn.com/entries/icons/facebook/000/026/152/gigachad.jpg'),
    ])
    return person if include_url else person[0]