import streamlit as st
import requests
import json

# Configure the API URL
API_URL = "https://feedback-scorecard-academia.cloudjiffy.net/"  

def main():
    st.title("Scenario Management System")
    st.subheader("Add New Scenario")

    # Create form for scenario input
    with st.form("scenario_form"):
        # Basic Information
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Scenario Name")
            type = st.selectbox("Scenario Type", ["sales", "customer"], placeholder="Select Type", index=None)  
            persona_name = st.text_input("Persona Name")
            

        voice_dict = {"Ava":"en-US-AvaMultilingualNeural", "Andrew":"en-US-AndrewMultilingualNeural"}
        with col2:
            image_url = st.text_input("Image URL")
            voice_id = st.selectbox("Voice ID", list(voice_dict.keys()), placeholder="Select Voice ID", index=None)
            difficulty_level = st.selectbox("Difficulty Level", ["easy", "medium", "hard"], placeholder="Select Level", index=None)

        # Persona Description
        persona = st.text_area("AI Persona Description")

        # Prompt
        prompt = st.text_area("Prompt")
        
        # Master Prompt - New field added
        master_prompt = st.text_area("Master Prompt", 
                                   help="Enter the master prompt for this scenario")

        submitted = st.form_submit_button("Add Scenario")

        if submitted:
            # Validate required fields client-side
            if not name or not type or not difficulty_level:
                st.error("Name, Type, and Difficulty Level are required fields")
                return

            # Prepare data for API request - send as JSON in the body instead of params
            data = {
                "name": name,
                "difficulty_level": difficulty_level,
                "prompt": prompt,
                "master_prompt": master_prompt,  # Added master_prompt field
                "type": type,  # This will map to roleplay_type in the backend
                "persona": persona,
                "persona_name": persona_name,
                "image_url": image_url
            }
            
            # Add voice_id only if selected
            if voice_id:
                data["voice_id"] = voice_dict[voice_id]

            try:
                # Make API request with JSON data
                response = requests.post(
                    f"{API_URL}/scenarios", 
                    json=data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 201:
                    st.success("Scenario created successfully!")
                    st.json(response.json())
                else:
                    st.error(f"Error creating scenario: {response.text}")
                    st.write(f"Status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to server: {str(e)}")

if __name__ == "__main__":
    main()