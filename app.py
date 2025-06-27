import streamlit as st
import requests
import json

# Configure the API URL
API_URL = "https://scenario-fetching-temp.cloudjiffy.net/"  

def fetch_master_prompts(roleplay_type=None):
    """Fetch master prompts from the API"""
    try:
        params = {}
        if roleplay_type:
            params['roleplay_type'] = roleplay_type
        
        response = requests.get(f"{API_URL}/master_prompts", params=params)
        if response.status_code == 200:
            return response.json().get('master_prompts', [])
    except:
        pass
    return []

def fetch_scenario(roleplay_type, difficulty_level):
    """Fetch a specific scenario"""
    try:
        response = requests.get(f"{API_URL}/scenarios/{roleplay_type}/{difficulty_level}")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching scenario: {str(e)}")
    return None

def main():
    st.title("Scenario Management System")
    
    # Add tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["Add Scenario", "Test Scenario", "Master Prompt Management"])
    
    with tab1:
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

            # Master Prompt Section
            st.subheader("Master Prompt Configuration")
            
            # Option to choose between existing master prompt or custom
            master_prompt_option = st.radio(
                "Master Prompt Option",
                ["Use Default", "Select Existing", "Custom"],
                horizontal=True
            )
            
            master_prompt_value = None
            master_prompt_id = None
            
            if master_prompt_option == "Select Existing":
                # Fetch master prompts (optionally filtered by type)
                master_prompts = fetch_master_prompts(type if type else None)
                
                if master_prompts:
                    # Create options for selectbox
                    prompt_options = {f"{mp['name']} (ID: {mp['id']})": mp for mp in master_prompts}
                    selected_prompt = st.selectbox(
                        "Select Master Prompt",
                        options=list(prompt_options.keys()),
                        placeholder="Choose a master prompt"
                    )
                    
                    if selected_prompt:
                        selected_mp = prompt_options[selected_prompt]
                        master_prompt_id = selected_mp['id']
                        # Show preview of selected prompt
                        with st.expander("Preview Selected Master Prompt"):
                            st.text(selected_mp['prompt'])
                else:
                    st.warning("No master prompts available. You can create a custom one below.")
                    master_prompt_option = "Custom"
            
            elif master_prompt_option == "Custom":
                master_prompt_value = st.text_area(
                    "Custom Master Prompt",
                    help="Enter your custom master prompt here. This will override the default master prompt.",
                    height=200
                )

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
                    "type": type,  # This will map to roleplay_type in the backend
                    "persona": persona,
                    "persona_name": persona_name,
                    "image_url": image_url
                }
                
                # Add voice_id only if selected
                if voice_id:
                    data["voice_id"] = voice_dict[voice_id]
                
                # Add master prompt configuration
                if master_prompt_option == "Select Existing" and master_prompt_id:
                    data["master_prompt_id"] = master_prompt_id
                elif master_prompt_option == "Custom" and master_prompt_value:
                    data["master_prompt"] = master_prompt_value
                # If "Use Default" is selected, we don't add anything and let the backend use DEFAULT_MASTER_PROMPT

                try:
                    # Debug: Print what we're sending
                    st.write("Sending data to API:")
                    st.json(data)
                    
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
    
    with tab2:
        st.subheader("Test Scenario Fetching")
        st.write("Use this to test what data is returned when fetching a scenario")
        
        col1, col2 = st.columns(2)
        with col1:
            test_type = st.selectbox("Test Roleplay Type", ["sales", "customer"], key="test_type")
        with col2:
            test_difficulty = st.selectbox("Test Difficulty", ["easy", "medium", "hard"], key="test_difficulty")
        
        if st.button("Fetch Scenario"):
            scenario = fetch_scenario(test_type, test_difficulty)
            if scenario:
                st.success("Scenario fetched successfully!")
                
                # Check if master_prompt is present
                if 'master_prompt' in scenario:
                    st.info(f"✓ Master prompt is present (length: {len(scenario['master_prompt'])})")
                else:
                    st.error("✗ Master prompt is NOT present in the response!")
                
                # Display the full scenario data
                st.json(scenario)
                
                # Show master prompt preview if available
                if 'master_prompt' in scenario and scenario['master_prompt']:
                    with st.expander("Master Prompt Preview"):
                        st.text(scenario['master_prompt'][:500] + "..." if len(scenario['master_prompt']) > 500 else scenario['master_prompt'])
            else:
                st.error("Failed to fetch scenario")

    with tab3:
        # Master Prompt Management
        st.subheader("Master Prompt Management")
        
        # Show existing master prompts
        st.write("### Existing Master Prompts")
        master_prompts = fetch_master_prompts()
        if master_prompts:
            for mp in master_prompts:
                with st.expander(f"{mp['name']} (Type: {mp.get('roleplay_type', 'All')})"):
                    st.text(mp['prompt'])
                    st.write(f"ID: {mp['id']}")
        else:
            st.info("No master prompts found")
        
        st.write("### Create New Master Prompt")
        
        col1, col2 = st.columns(2)
        with col1:
            mp_name = st.text_input("Master Prompt Name", key="mp_name")
            mp_type = st.selectbox(
                "Roleplay Type (Optional)", 
                ["", "sales", "customer"], 
                key="mp_type",
                help="Leave empty to make this master prompt available for all types"
            )
        
        mp_prompt = st.text_area("Master Prompt Content", key="mp_prompt", height=150)
        
        if st.button("Create Master Prompt"):
            if mp_name and mp_prompt:
                try:
                    data = {
                        "name": mp_name,
                        "prompt": mp_prompt
                    }
                    if mp_type:
                        data["roleplay_type"] = mp_type
                    
                    response = requests.post(
                        f"{API_URL}/master_prompts", 
                        json=data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        st.success("Master prompt created successfully!")
                        st.rerun()  # Refresh to show new master prompt in the list
                    else:
                        st.error(f"Error creating master prompt: {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to server: {str(e)}")
            else:
                st.error("Name and prompt content are required")

if __name__ == "__main__":
    main()