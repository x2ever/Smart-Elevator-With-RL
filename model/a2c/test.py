import gym
import gym_building
import sys
import os
import numpy as np
import time
sys.path.append(".")

from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import SubprocVecEnv
from stable_baselines import A2C

from model.setting import people

model_directory = os.path.dirname(os.path.realpath(__file__)) + "/a2c-models/"

n_cpu = 1
env = SubprocVecEnv([lambda: gym.make('gym_building:building-v0', people=people, num_of_lift=3, height_of_building=5) for i in range(1)])

model = A2C.load(model_directory + "a2c-model_660000.pkl")

obs = env.reset()

while True:
    action, _states = model.predict(np.concatenate(([obs for i in range(32)])))
    obs, rewards, dones, info = env.step(action)
    env.render()
