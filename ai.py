import os
import openai
from openai import OpenAI

openai.api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()
# Твой vector_store_id (замени на реальный)
VECTOR_STORE_ID = "vs_67b4ef548bbc819182d55efc4ddccc9b"
assistant = 'asst_5mQEyfb3mUIw3oUNsdGOGGd0'


import time

# Создание потока
def create_threads(message:list):
    thread = client.beta.threads.create(
        messages=message,
        tool_resources={"file_search": {"vector_store_ids": ["vs_67b4ef548bbc819182d55efc4ddccc9b"]}}
)
    print("Threads is ready")
    return thread.id

# Запуск выполнения ассистента
def create_run(thread_id, assistant_id):
    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

# Ожидание завершения выполнения
    while run.status in ["queued", "in_progress"]:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

# Получение сообщений
def message_list(thread_id):

    messages = client.beta.threads.messages.list(thread_id=thread_id)

    for msg in messages.data:
        if msg.role == "assistant":
            return "\n".join(block.text.value for block in msg.content if hasattr(block, "text"))

    return None  # Если сообщений ассистента нет

def delete_threads(thread_id):
    response = client.beta.threads.delete(thread_id)
    print("Threads is deleted")
def create_message(thread_id, message):
    thread_message = client.beta.threads.messages.create(
        thread_id,
        role="user",
        content=message,
    )
# def edit_instructions(assistant, new_instructions:str, old_instructions:str):
#     instructions = old_instructions + '\n' + new_instructions
#     my_updated_assistant = client.beta.assistants.update(
#         assistant_id=assistant,
#         instructions=instructions,
#     )
# old_instructions = client.beta.assistants.retrieve(assistant).instructions
# # edit_instructions(assistant, 'new', old_instructions)
# batch_input_file = client.files.create(
#     file=open("data.jsonl", "rb"),
#     purpose="batch"
# )
#
# print(batch_input_file)