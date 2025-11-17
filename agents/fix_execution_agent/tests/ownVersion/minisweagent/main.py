from fixcodeagent.agents.default import DefaultAgent
from fixcodeagent.models.litellm_model import LitellmModel
from fixcodeagent.environments.local import LocalEnvironment


model = LitellmModel(model_name="deepseek/deepseek-chat", model_kwargs={"api_key": "sk-75db9bf464d44ee78b5d45a655431710"})
env = LocalEnvironment()

agent = DefaultAgent(model=model, env=env)
status, result = agent.run("Your task here")
print("Status:", status)
print("Result:", result)
