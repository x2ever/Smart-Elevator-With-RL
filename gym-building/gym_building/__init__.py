from gym.envs.registration import register

register(
    id='building-v0',
    entry_point='gym_building.envs:BuildingEnv',
)