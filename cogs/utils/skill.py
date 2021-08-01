import voxelbotutils as vbu


def get_level_by_exp(experience: int) -> int:
    exp_per_level = [
        0,      50,     175,        # 1 2 3
        375,    675,    1_175,      # 4 5 6
        1_925,  2_925,  4_425,      # 7 8 9
        6_425,  9_925,  14_925,     # 10 11 12
        22_425, 32_425, 47_425,     # 13 14 15
        67_425, 97,425, 147_425,    # 17 18 19,
        222_425                     # 20
    ]
    for i, e in reversed(list(enumerate(exp_per_level))):
        if experience >= e:
            return i

async def update_skill(db: vbu.DatabaseConnection, user_id: int, skill_name: str, experience: int):
    await db('''
        INSERT INTO user_skill (user_id, name, experience) VALUES ($1, $2, $3)
        ON CONFLICT (user_id, name) DO UPDATE SET experience = user_skill.experience + $3
        ''', user_id, skill_name, experience)
