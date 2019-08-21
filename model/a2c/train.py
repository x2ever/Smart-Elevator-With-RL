
import os
import datetime
import numpy
import gym
import gym_building
from stable_baselines.common.vec_env import SubprocVecEnv
from stable_baselines.common.policies import MlpPolicy, MlpLstmPolicy, MlpLnLstmPolicy
from stable_baselines.bench import Monitor
from stable_baselines.results_plotter import load_results, ts2xy
from stable_baselines import A2C
import sys
sys.path.append(".")
from model.setting import people

TIMESTEPS = 10000000001

best_mean_reward = -numpy.inf
n_steps = 550000
log_directory = os.path.dirname(os.path.realpath(__file__)) + "/a2c-log/"
model_directory = os.path.dirname(os.path.realpath(__file__)) + "/a2c-models/"


def callback(_locals, _globals):
    """
    Callback called at each step (for DQN an others) or after n steps (see ACER or PPO2)
    :param _locals: (dict)
    :param _globals: (dict)
    """
    global best_mean_reward, n_steps
    if (n_steps + 1) % 5000 == 0:
        print("Saving new best model")
        _locals['self'].save(
            model_directory + 'a2c-model_' + str(n_steps + 1) + '.pkl')
    n_steps += 1
    return True


if __name__ == "__main__":
    os.makedirs(log_directory, exist_ok=True)
    os.makedirs(model_directory, exist_ok=True)

    env = SubprocVecEnv([lambda: Monitor(gym.make('gym_building:building-v0', people=people, num_of_lift=3, height_of_building=5), log_directory, allow_early_resets=True) for i in range(32)])

    model = A2C(
        env=env,
        policy=MlpLnLstmPolicy,
        verbose=1,
        tensorboard_log="./a2c_tensorboard/",
        lr_schedule='middle_drop',
        full_tensorboard_log=True,
        n_steps=25
    )

    # model = A2C.load(model_directory + "a2c-model_55000.pkl")
    # model.set_env(env=env)

    model.learn(
        total_timesteps=TIMESTEPS,
        callback=callback
    )
