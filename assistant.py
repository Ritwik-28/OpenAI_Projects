import time
from openai import AzureOpenAI

# Assuming these are your API details (Use environment variables or a secure method to handle these in production)
api_URI = "your_endpoint_here"
api_KEY = "your_api_key_here"
api_version = "your_api_version_here"
assistant_id = "your_assistant_id_here"
fixed_thread_id = "your_fixed_thread_id_here"

def ask_chatgpt():
    # Initialize the OpenAI Azure client (Ensure this matches the SDK's initialization method)
    client = AzureOpenAI(api_key=api_KEY,
                         api_version=api_version,
                         azure_endpoint=api_URI)

    thread_id = fixed_thread_id  # Use the fixed Thread ID

    # Create a new Message within the existing thread with specific content
    message_creation_response = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content="Task to be solved by the assistant.",  # Replace with actual task
    )

    # Extract the message ID of the newly created message (Ensure you access attributes correctly based on response type)
    last_user_message_id = message_creation_response.id

    # Create a new Run using the assistant and the fixed thread with specific instructions
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions="Instructions for the assistant.",  # Replace with actual instructions
    )

    feedback_text = ""

    # Check the status of the Run and wait for completion
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        
        if run_status.status == "completed":
            # Retrieve all messages from the thread after the run completion
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            found_last_user_message = False
            for message in messages:
                if found_last_user_message and message.role == "assistant":
                    feedback_text = message.content[0].text.value
                    break  # Found the first assistant message after the last user message
                if message.id == last_user_message_id:
                    found_last_user_message = True

            break  # Exit the loop once processing is complete
        elif run_status.status in ["expired", "failed", "cancelled"]:
            feedback_text = "Run did not complete successfully."
            break
        else:
            print("Waiting for completion...")
            time.sleep(5)

    return feedback_text.strip()
