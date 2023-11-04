import time

import openai
import tiktoken

from app.utils.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def call_llm(
    user_query,
    conversation=None,
    system_prompt=None,
    model="gpt-4",
    temperature=0,
) -> tuple[str, list[dict], int, openai.ChatCompletion]:
    """
    :param user_query:
    :param conversation:
    :param system_prompt:
    :return:
    """
    if conversation is None:
        conversation = []
    if system_prompt is not None and len(conversation) > 0:
        if conversation[0]["role"] != "system":
            conversation.insert(0, {"role": "system", "content": system_prompt})

    conversation.append({"role": "user", "content": user_query})

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


def get_video_topics(transcript):
    """
    Parses video transcripts into distinct topics
    :param transcript: timestamped transcript of video, with keys: text, start, duration
    :return:
    """
    # format transcript into format:
    # ___s
    # line of text
    # ___s
    # line of text
    # ...
    MAX_RETRIES = 10
    transcript_strings = []
    transcript_string = ""
    tokenizer = tiktoken.get_encoding("cl100k_base")
    for line in transcript:
        if len(tokenizer.encode(str(transcript_string))) > 14000:
            transcript_strings.append(transcript_string)
            transcript_string = ""
        transcript_string += f"""
        {line['start']}s
        {line['text']}
        """
        # add if last line
        if line == transcript[-1]:
            transcript_strings.append(transcript_string)

    topics = []
    for transcript_string in transcript_strings:
        prompt = f"""Please assist me in meticulously organizing this YouTube transcript.

                Chunking: Dissect the transcript into individual, question-based categories, ensuring each segment maintains sufficient length and detail.
                Timestamps: Every section should be accompanied by a timestamp in the format ___s. Exclusion: Topic descriptions aren't expected to have timestamps.
                [TOPIC] Sections: Craft sections labeled as [TOPIC] so that they are both detailed and self-explanatory, making them search-result friendly.
                Topic Titles: Titles should be expressive and thorough. Avoid overly terse or vague titles.
                Context Buzzwords: Extract 3 pertinent "buzzwords" from each segment of the video to encapsulate its essence. These buzzwords should be embedded within the topic title. It's essential that these buzzwords are explicitly mentioned in the transcript.

                Be sure to exclude text that is for introductory purposes or outros


                For examples to exclude:
                "Have a good day and thanks for watching my video!", "Welcome to my youtube channel! Lets get started with the video..."


                For example thats positive:

                For a video chronicling Nazi Germany's ascent:

                [TOPIC: Adolf Hitler, World War II, Propaganda]
                156s
                Hitler's leadership precipitated the inception of World War II, leveraging propaganda and symbols like the Swastika to consolidate the Reich's power.

                For a tutorial on baking chocolate chip cookies:

                [TOPIC: Flour, Eggs, Chocolate Chips]
                73s
                Key ingredients encompass 1 cup of flour, 3 eggs, and 1 cup of chocolate chips. Additionally, ensure the oven is preheated to 350 degrees Fahrenheit.

                Please Process this Transcript: {transcript_string}
                """

        retries = 0
        while retries < MAX_RETRIES or len(topics) == 0:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-16k",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are the YouTube chunker. Your job is to chunk youtube video transcripts into specific topics, to be searched through. ",
                        },
                        {"role": "user", "content": prompt},
                    ],
                )
                topics_raw = response.choices[0]["message"]["content"]
                # parse topics
                for topic in topics_raw.split("[TOPIC:")[1:]:
                    if topic != "":
                        topic = topic.split("]")
                        timestamp = topic[1].split("s")[0].strip()
                        # text is everything after the timestamp
                        s_index = topic[1].find("s")
                        text = topic[1][s_index + 1 :].strip()
                        topics.append(
                            {
                                "topic": topic[0],
                                "text": text,
                                "startTime": int(float(timestamp)),
                            }
                        )
                print(f"Parsed {len(topics)} topics from transcript")

                return topics
            except openai.error.OpenAIError as error:
                if "rate limit" in str(error).lower() or "502" in str(error).lower():
                    retries += 1
                    print(
                        f"Error occurred: {error}. Retry {retries}/{MAX_RETRIES} in 60 seconds."
                    )
                    time.sleep(60)
                else:
                    raise
            except Exception as e:
                print(e)
                retries += 1
                print(
                    f"Error occurred: {e}. Retry {retries}/{MAX_RETRIES} in 60 seconds."
                )
                time.sleep(60)
