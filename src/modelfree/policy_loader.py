"""Load serialized policies of different types."""

from baselines.common.vec_env.dummy_vec_env import DummyVecEnv
from baselines.ppo2 import ppo2

from modelfree.gym_compete_conversion import load_zoo_agent
from modelfree.simulation_utils import ResettableAgent
from modelfree.utils import StatefulModel, ZeroAgent, make_single_env


def load_baselines_mlp(agent_name, env, env_name, _, sess):
    # TODO: Find a way of loading a policy without training for one timestep.
    def agent_fn(env, sess):
        return ZeroAgent(env.action_space.shape[0])

    def make_env():
        return make_single_env(env_name=env_name, seed=0, agent_fn=agent_fn, out_dir=None)

    denv = DummyVecEnv([make_env])

    with sess.as_default():
        with sess.graph.as_default():
            model = ppo2.learn(network="mlp", env=denv,
                               total_timesteps=1,
                               seed=0,
                               nminibatches=4,
                               log_interval=1,
                               save_interval=1,
                               load_path=agent_name)

    stateful_model = StatefulModel(denv, model, sess)
    trained_agent = ResettableAgent(get_action_in=stateful_model.get_action,
                                    reset_in=stateful_model.reset)

    return trained_agent


AGENT_LOADERS = {
    "zoo": load_zoo_agent,
    "mlp": load_baselines_mlp,
}


def get_agent_any_type(agent, agent_type, env, env_name, index, sess=None):
    try:
        return AGENT_LOADERS[agent_type](agent, env, env_name, index, sess=sess)
    except KeyError:
        raise ValueError(f"Unrecognized agent type '{agent_type}'")