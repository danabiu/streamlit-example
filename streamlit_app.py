# Import necessary libraries
import openai
import streamlit as st
import time

# Set your OpenAI API key here directly (not recommended for security reasons)
# It's better to use an environment variable or a secret management system
openai.api_key = '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'

# Set your OpenAI Assistant ID here
assistant_id = 'asst_ETJL6CJL9fHBsYhqbgngtkHa'

# Initialize the OpenAI client (ensure to set your API key in the sidebar within the app)
client = openai

# Initialize session state variables for chat control
if "start_chat" not in st.session_state:
    st.session_state.start_chat = True
    

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

# Set up the Streamlit page with a title and icon
st.set_page_config(
    page_title="AI-Tecnoiglesia",
    page_icon=":speech_balloon:",
    initial_sidebar_state="expanded",
    
    
)


# URL del logotipo
logo_url = "https://tecnoiglesia.com/wp-content/uploads/2023/11/Tecnoiglesia-new-logo.png"

# Agregar el logotipo en la barra lateral
st.sidebar.markdown(
    f"<div style='text-align: center;'><img src='{logo_url}' width='100'></div>", 
    unsafe_allow_html=True
)

if st.session_state.start_chat:
        # Create a thread once and store its ID in session state
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id


    # Sidebar button to redirect to a webpage
button_html = """
<a href="https://tecnoiglesia.com" target="_blank">
    <button class="btn" style=" margin: 17px; font-family: 'Poppins'; font-weight: regular; color: white; background-color: #FF5001; padding: 10px 20px; border-radius: 5px; border: none; cursor: pointer;">
        <i class="fa fa-arrow-left"></i> Regresar a Tecnoiglesia
        </button>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
</a>
<style>
}
</style>
"""

st.sidebar.markdown(button_html, unsafe_allow_html=True)
    # Define the function to process messages with citations

def process_message_with_citations(message):
    """Extract content and annotations from the message and format citations as footnotes."""
    message_content = message.content[0].text
    annotations = message_content.annotations if hasattr(message_content, 'annotations') else []
    citations = []

    # Iterate over the annotations and add footnotes
    for index, annotation in enumerate(annotations):
        # Replace the text with a footnote
        message_content.value = message_content.value.replace(annotation.text, f' [{index + 1}]')

        # Gather citations based on annotation attributes
        if (file_citation := getattr(annotation, 'file_citation', None)):
            # Retrieve the cited file details (dummy response here since we can't call OpenAI)
            cited_file = {'filename': 'cited_document.pdf'}  # This should be replaced with actual file retrieval
            citations.append(f'[{index + 1}] {file_citation.quote} from {cited_file["filename"]}')
        elif (file_path := getattr(annotation, 'file_path', None)):
            # Placeholder for file download citation
            cited_file = {'filename': 'downloaded_document.pdf'}  # This should be replaced with actual file retrieval
            citations.append(f'[{index + 1}] Click [here](#) to download {cited_file["filename"]}')  # The download link should be replaced with the actual download path

    # Add footnotes to the end of the message content
    full_response = message_content.value + '\n\n' + '\n'.join(citations)
    return full_response


# Main chat interface setup
st.title("Asistente Tecnoiglesia ✨")
st.write("¡Bienvenido a la 𝗜𝗔 de Tecnoiglesia! ¿Como te podemos ayudar hoy?")

# Only show the chat interface if the chat has been started
if st.session_state.start_chat:
    # Initialize the model and messages list if not already in session state
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4-1106-preview"
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing messages in the chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input for the user
    if prompt := st.chat_input("Escribe un mensaje..."):
        # Add user message to the state and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Add the user's message to the existing thread
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        # Create a run with additional instructions
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id
        )

    
        # Poll for the run to complete and retrieve the assistant's messages
        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )

        # Retrieve messages added by the assistant
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages 
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            full_response = process_message_with_citations(message)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            with st.chat_message("assistant"):
                st.markdown(full_response, unsafe_allow_html=True)
