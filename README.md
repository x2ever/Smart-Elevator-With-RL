# Smart-Elevator-With-RL

## TODO LIST

- ~~Make an editable building simulator~~ ___Done___
- ~~Convert the simulator to custom gym environment~~  ___Done___
- ~~Add render function which can be used for testing models~~  ___Done___
- Implement a greedy algorithm for comparison between models
- Add noise missions to the environment
- Define the disorder of the environment.
- Observe the performance change between the models according to the disorder. 

## Installation

__Install stable-baselines__

- Follow the instruction in this [document](https://stable-baselines.readthedocs.io/en/master/guide/install.html)

__Install Gym env__

    cd Smart-Elevator-With-RL
    python -m pip install -e gym-building

### Train

    cd Smart-Elevator-With-RL
    python model\A2C\train.py

### Test

    cd Smart-Elevator-With-RL
    python model\A2C\test.py
