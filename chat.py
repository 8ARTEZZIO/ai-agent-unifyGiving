import streamlit as st
import openai
import time
from country_list import countries_for_language

# Set up OpenAI API key
try:
    openai.api_key = st.secrets["api_key"]
except KeyError:
    st.error("OpenAI API key is not configured. Please check your secrets file.")
    st.stop()

# Predefined credentials (for simplicity, these are stored in secrets)
try:
    USERNAME = st.secrets["USERNAME"]
    PASSWORD = st.secrets["PASSWORD"]
except KeyError:
    st.error("Login credentials are not configured. Please check your secrets file.")
    st.stop()

# Load countries
countries = list(dict(countries_for_language('en')).values())

if not countries:
    st.error("Country list could not be loaded. Please check the `countries_for_language` function.")
    st.stop()

def get_ai_response(question):
    try:
        # Use OpenAI's ChatCompletion method for chat-based models like GPT-4 and GPT-3.5-turbo
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Or 'gpt-4' if you have access
            messages=[
                {"role": "system", "content": "You are a helpful accountant and you give detailed tax breakdown and also the percentage."},
                {"role": "user", "content": question}
            ],
            max_tokens=300,  # Increase max_tokens to allow for a longer response
            temperature=0.7  # Adjust temperature for response style
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.error.RateLimitError:
        return "Rate limit exceeded. Please try again later."
    except openai.error.InvalidRequestError as e:
        return f"Invalid request: {e}"

def display_typing_effect(response_text, placeholder):
    # Split response into words for better typing effect
    words = response_text.split()
    displayed_text = ""
    
    for word in words:
        displayed_text += word + " "
        placeholder.markdown(displayed_text.strip())  # Use markdown for text wrapping
        time.sleep(0.05)  # Adjust delay for typing effect (smaller delay for better UX)

# Check if user is authenticated
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def authenticate(username, password):
    return username == USERNAME and password == PASSWORD

def login():
    st.title("Login")
    
    # Use a form for username/password login to handle form submission properly
    with st.form(key='login_form'):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.success("Login successful!")
            else:
                st.error("Invalid username or password. Please try again.")

# If the user is not authenticated, show the login form
if not st.session_state.authenticated:
    login()
else:
    # Streamlit UI
    st.title("AI Tax Donation Question")
    st.write("Select your country of residence and the country you're donating to.")

    # Dropdown for residence (Option1)
    residence = st.selectbox("I live in:", countries, index=0, help="Select your country of residence.")

    # Dropdown for donation destination (Option2)
    donation_destination = st.selectbox("I am donating money to:", countries, index=1, help="Select the country where you're donating.")

    # Format the question
    question = f"I live in {residence} and I am donating money to {donation_destination}, would I get a tax break?"

    # Display the generated question
    st.write(f"Your Question: {question}")

    # When the user presses the 'Ask' button
    if st.button('Ask', disabled=st.session_state.get('processing', False)):
        st.session_state['processing'] = True
        with st.spinner('Generating response...'):
            answer = get_ai_response(question)
        
        # Display typing effect
        st.success("AI's Response:")
        placeholder = st.empty()  # Create a placeholder for the typing effect
        display_typing_effect(answer, placeholder)
        
        st.session_state['processing'] = False
