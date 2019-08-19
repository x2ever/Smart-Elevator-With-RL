
import os
import datetime
import numpy
import gym
import gym_building
from stable_baselines.common.vec_env import SubprocVecEnv
from stable_baselines.common.policies import MlpPolicy, MlpLstmPolicy, MlpLnLstmPolicy
from stable_baselines.bench import Monitor
from stable_baselines.results_plotter import load_results, ts2xy
from stable_baselines import ACER
import sys
sys.path.append(".")
from model.setting import people

TIMESTEPS = 10000000001

best_mean_reward = -numpy.inf
n_steps = 0
log_directory = os.path.dirname(os.path.realpath(__file__)) + "/acer-log/"
model_directory = os.path.dirname(os.path.realpath(__file__)) + "/acer-models/"


def callback(_locals, _globals):
    """
    Callback called at each step (for DQN an others) or after n steps (see ACER or PPO2)
    :param _locals: (dict)
    :param _globals: (dict)
    """
    global best_mean_reward, n_steps
    if (n_steps + 1) % 90000 == 0:
        x, y = ts2xy(load_results(log_directory), 'timesteps')
        if len(x) > 0:
            mean_reward = numpy.mean(y[-100:])
            print(x[-1], 'timesteps')
            print("Best mean reward: {:.2f} - Last mean reward per episode: {:.2f}".format(
                best_mean_reward, mean_reward))

        if mean_reward > best_mean_reward:
            best_mean_reward = mean_reward
            print("Saving new best model")
            _locals['self'].save(
                model_directory + 'acer-model_' + str(n_steps + 1) + '.pkl')
    n_steps += 1
    return True


if __name__ == "__main__":
    os.makedirs(log_directory, exist_ok=True)
    os.makedirs(model_directory, exist_ok=True)

    env = SubprocVecEnv([lambda: Monitor(gym.make('gym_building:building-v0', people=people, num_of_lift=3, height_of_building=5), log_directory, allow_early_resets=True) for i in range(4)])

    model = ACER(
        env=env,
        policy=MlpLnLstmPolicy,
        verbose=1,
        tensorboard_log="./acer_tensorboard/",
        learning_rate= 0.01,
        lr_schedule = 'double_linear_con'
    )

    model.learn(
        total_timesteps=TIMESTEPS,
        callback=callback
    )