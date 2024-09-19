import streamlit as st
import openai
import requests
import json
def get_clip_details(clip_id):
    # Construct the URL with the clip ID
    url = f"https://studio-api.suno.ai/api/external/clips/?ids={clip_id}"

    # Set up the headers with the authorization token
    headers = {
        "Authorization": "Bearer 1kuenoG28FH0HTXRFHfIFfb9ECFLSnmI",
    }

    try:
        # Send the GET request to fetch clip details
        response = requests.get(url, headers=headers)

        # Raise an exception if the request was unsuccessful
        response.raise_for_status()


        # Extract the audio_url from the clip details
        clip_details = response.json()

        clips = clip_details.get("clips", [])
        if clips:
            audio_url = clips[0].get("audio_url")
            if audio_url:
                return audio_url
            else:
                print("Audio URL is not available in the clip details.")
        else:
            print("No clips found in the response.")


    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Response: {response.text}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")

    return None


def generate_music_with_suno(description_prompt, user_genre):
    # SUNO API
    suno_api_url = "https://studio-api.suno.ai/api/external/generate/"

    # SUNO API payload
    payload = {
          "topic": description_prompt,
          "tags": user_genre,

    }

    payload_str = json.dumps(payload)

    headers = {
        "Authorization": "Bearer 1kuenoG28FH0HTXRFHfIFfb9ECFLSnmI",
        "Content-Type": "text/plain;charset=UTF-8"
    }

    try:
      # Send POST request

      response = requests.post(suno_api_url, data=payload_str, headers=headers)
      data = response.json()

      st.text(f"Clip Response: {json.dumps(data, indent=4)}")

      # Extract the first clip's audio URL if available
      clips = data.get("clips")
      if clips:
          clip_id = clips[0].get("id")  # Extract the clip ID
          if clip_id:
              # Fetch the clip details using the clip ID
              return get_clip_details(clip_id)
          else:
              st.error("Clip ID is not available yet. Please check back later.")
      else:
          st.error("No clips were generated. Please check your prompt and genre input.")
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err} - Response: {response.text}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"Request error occurred: {req_err}")

    return None

# Set up OpenAI API key
# key is not shown

# Streamlit app
st.title("Book Mood Music Generator 🎶")
st.write(
    "Enter the title of your book to analyze the mood, and generate music that matches the vibe!"
)

# Book input
user_input = st.text_area(
    "Enter the title of your book here:", height=100, placeholder="Type or paste your title here..."
)
user_genre = st.text_input("Enter the genre of music you would like your song to be in:", placeholder="Type genre here...")

# Button to submit the text
if st.button("Generate Music Inspired by Your Book"):
    if not user_input.strip():
        st.warning("Please enter the book title before submitting.")
    else:
        # Analyze the book using OpenAI
        try:
            with st.spinner("Analyzing the text..."):
                response = openai.Completion.create(
                    engine="gpt-3.5-turbo-instruct",
                    prompt=f"Analyze the following book and describe the main themes, emotions, and moods:\n\n{user_input}",
                    max_tokens=150
                )

                # Extract and show the analysis from the LLM
                analysis_result = response.choices[0].text.strip()
                st.subheader("Analysis Results:")
                st.write(analysis_result)

                # make a descriptive prompt based on analysis for SUNO
                description_prompt = f"A song that reflects the following themes and emotions: {analysis_result[0:200]}"

                # Call the function to generate music using SUNO
                audio_url = generate_music_with_suno(description_prompt, user_genre)

                # Play the generated audio i
                if audio_url:
                    st.audio(audio_url, format="audio/mp3")
        except Exception as e:
            st.error(f"An error occurred: {e}")
