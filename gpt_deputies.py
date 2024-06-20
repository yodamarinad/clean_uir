from g4f.client import Client
from g4f.Provider import RetryProvider, Phind, FreeChatgpt, Liaobots

import g4f.debug
g4f.debug.logging = True

client = Client(
    provider=RetryProvider([Phind, FreeChatgpt, Liaobots], shuffle=False)
)
response = client.chat.completions.create(
    model="",
    messages=[{"role": "user", "content": "structure json missing_141_people.json "}],
)
print(response.choices[0].message.content)
