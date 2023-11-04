import openai
import tiktoken


def call_llm(user_query, conversation=None, system_prompt=None, model="gpt3.5-turbo", temperature=0) -> tuple[
    str, list[dict], int, openai.ChatCompletion]:
    """
    :param user_query:
    :param conversation:
    :param system_prompt:
    :return:
    """
    if conversation is None:
        conversation = []
    if system_prompt is not None:
        if conversation[0]["role"] != "system":
            conversation.insert(0, {"role": "system", "text": system_prompt})

    conversation.append({"role": "user", "text": user_query})

    # switch the model if it is beyond the token limit
    tokenizer = tiktoken.get_encoding("cl100k_base")
    if len(list(tokenizer.encode(str(conversation)))) > 3000:
        model = "gpt-3.5-turbo-16k"

    response = openai.ChatCompletion.create(
        model=model,
        messages=conversation,
        temperature=temperature,
    )
    conversation.append(
        {"role": "assistant", "content": response.choices[0].message["content"]}
    )

    return (
        response.choices[0].message["content"],
        conversation,
        response["usage"]["total_tokens"],
        response,
    )
