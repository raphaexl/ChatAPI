
import tiktoken
import openai
from chat import models

MAX_RESPONSE_TOKENS = 500
OVERALL_MAX_TOKENS = 4096
PROMPT_MAX_TOKEN = OVERALL_MAX_TOKENS - MAX_RESPONSE_TOKENS
TOKEN_LIMIT = 4096  # Adjust this based on your requirements

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = 0
    for message in messages:
        num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":  # if there's a name, the role is omitted
                num_tokens += -1  # role is always required and always 1 token
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens


def send_message(messages, model_name, max_response_tokens=MAX_RESPONSE_TOKENS):
    try:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=messages,
            temperature=0.5,
            max_tokens=max_response_tokens,
            top_p=0.9,
            frequency_penalty=0,
            presence_penalty=0,
        )
        return (False, response['choices'][0]['message']['content'])
    except openai.error.Timeout as e:
        #Handle timeout error, e.g. retry or log
        return (True, f"OpenAI API request timed out: {e}")
    except openai.error.APIError as e:
        #Handle API error, e.g. retry or log
        return (True, f"OpenAI API returned an API Error: {e}")
        pass
    except openai.error.APIConnectionError as e:
        #Handle connection error, e.g. check network or log
        return (True, f"OpenAI API request failed to connect: {e}")
    except openai.error.InvalidRequestError as e:
        #Handle invalid request error, e.g. validate parameters or log
        return (True, f"OpenAI API request was invalid: {e}")
    except openai.error.AuthenticationError as e:
        #Handle authentication error, e.g. check credentials or log
        return (True, f"OpenAI API request was not authorized: {e}")
    except openai.error.PermissionError as e:
        #Handle permission error, e.g. check scope or log
        return (True, f"OpenAI API request was not permitted: {e}")
    except openai.error.RateLimitError as e:
        #Handle rate limit error, e.g. wait or log
        return (True, f"OpenAI API request exceeded rate limit: {e}")



def make_prompt(conversation:models.Conversation, prompt):
    youtube_video = None
    error = None

    try:
        youtube_video = models.YouTubeVideo.objects.get(video_id=conversation.youtube_video)
        # print("Got the YouTube video: ", youtube_video)
    except models.YouTubeVideo.DoesNotExist:
        # print("YouTube video not found with ID: ", conversation.youtube_video)
        error = {'message': f'YouTube video not found with ID: {conversation.youtube_video}', 'status': 404}
        return error, []
    base_system_message = f"You are a helpful assistant, provided with this youtube video details, answer any related question and even non related ones\n" 
    if youtube_video.include_title:
        base_system_message + f"youtube video title: {youtube_video.title}\n"
    base_system_message += f"youtube video script: {youtube_video.script}\n" 
    if youtube_video.include_description:
        base_system_message + f"youtube video description: {youtube_video.description}\n"
    if youtube_video.include_tags:
        base_system_message + f"video tags: {youtube_video.tags}"
    system_message = f"{base_system_message.strip()}"
    last_messages = models.Message.objects.filter(conversation_id=conversation.pk).order_by('-id')[:9]
    messages=[
        {"role": "system", "content": system_message},
    ]
    for msg in last_messages:
        if msg.message_type == 'US':
            messages.append({"role": "user", "name":msg.sender.username, "content": msg.text})
        else:
            messages.append({"role": "assistant", "name":"Bot", "content": msg.text})
    messages.append({"role": "user", "name":conversation.initiator.username, "content": prompt})
    # print("Token counting now , ")
    token_count = num_tokens_from_messages(messages)
    # print("Token optimization, we have found ", token_count)
    # remove first message while over the token limit
    while token_count > PROMPT_MAX_TOKEN:
        if len(messages) > 3:
            messages.pop(1)
        else:
            break
        token_count = num_tokens_from_messages(messages)
    if token_count > TOKEN_LIMIT:
        error = {'message': 'Token limit exceeded', 'status': 400}
    # print("messages ", messages)
    return error, messages

def askGPT(conversation_id, prompt, chatgpt_model_name='gpt-3.5-turbo'):
    conversation = models.Conversation.objects.get(id=conversation_id)
    error, messages = make_prompt(conversation, prompt)
    has_error = True
    if error is not None:
        return (has_error, error['message'])
    has_error, response = send_message(messages, chatgpt_model_name, MAX_RESPONSE_TOKENS)
    return (has_error, response)