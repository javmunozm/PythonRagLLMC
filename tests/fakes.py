from collections.abc import Sequence

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage


class FakeToolChatModel(GenericFakeChatModel):
    def bind_tools(self, tool : Sequence, **kwargs):
        return self

def fake_llm(*respuestas: str | AIMessage) -> FakeToolChatModel:
    msgs = [r if isinstance(r, AIMessage) else AIMessage(content=r) for r in respuestas]
    return FakeToolChatModel(messages=iter(msgs))
 