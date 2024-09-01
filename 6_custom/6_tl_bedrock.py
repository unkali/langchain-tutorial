from langchain_aws import ChatBedrockConverse

# Load environment variables from .env
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

llm = ChatBedrockConverse(
    model="anthropic.claude-3-5-sonnet-20240620-v1:0",
    temperature=0,
    max_tokens=None,
    # other params...
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that translates {input_language} to {output_language}.",
        ),
        ("human", "{input}"),
    ]
)

chain = prompt | llm
ai_msg = chain.invoke(
    {
        "input_language": "English",
        "output_language": "German",
        "input": "I love programming.",
    }
)
print(ai_msg.content)


