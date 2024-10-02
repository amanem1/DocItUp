# import streamlit_mermaid as stmd
import streamlit as st
import base64
from io import BytesIO
import requests
from question_session import questions
from openai_data import get_response_from_gpt3,correct_mermaid_code
import streamlit.components.v1 as stmd
import os
from pathlib import Path
from dotenv import load_dotenv


GITHUB_REPO = "amanem1/DocItUp"  # Your repo name
FILE_PATH = "user_search.txt"  # Path to the file you want to update
FILE_OUTPUT_PATH = "generated_output.txt"

#the path of the .env file should be in the folder only , else please change accordingly
dotenv_path = Path('flowai/local.env')
load_dotenv()


# Get the api key from the environment  variable

github_key=os.getenv('github_token')

prompt_user_input = "" # this is only for the prompt
user_input = ""
text_file = ""
updated_input_text = ""
updated_output_text = ""

###############################
# adding html instead of stmd.streamlitHere's a version of your render_mermaid function that includes zooming with mouse scroll and dragging for panning:

def render_mermaid(code):
    html = f"""
    <div id="mermaid-container" style="overflow: hidden; height: 100%; width: 100%;">
        <div id="mermaid-content" style="transform-origin: 0 0;">
            <pre class="mermaid">
            {code}
            </pre>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/panzoom/9.4.0/panzoom.min.js"></script>
    <script>
    // Initialize Mermaid
    mermaid.initialize({{ startOnLoad: true }});

    // Wait for the Mermaid to finish rendering, then apply panzoom
    document.addEventListener("DOMContentLoaded", function() {{
        const mermaidContent = document.getElementById('mermaid-content');
        const panzoomInstance = panzoom(mermaidContent, {{
            zoomDoubleClickSpeed: 1,
            maxZoom: 4,
            minZoom: 0.5,
            bounds: true,
            boundsPadding: 0.1
        }});

        // Allow zoom with scroll wheel
        mermaidContent.addEventListener('wheel', function(event) {{
            if (event.ctrlKey) {{
                event.preventDefault();
                const delta = event.deltaY > 0 ? -0.05 : 0.05;
                panzoomInstance.zoomTo(mermaidContent.clientWidth / 2, mermaidContent.clientHeight / 2, delta);
            }}
        }});
    }});
    </script>
    """
    stmd.html(html, height=500, scrolling=False)







# Function to read the file from GitHub
def read_github_file():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {github_key}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = base64.b64decode(response.json()['content']).decode('utf-8')
        return content, response.json()['sha']  # Return file content and SHA (for updating)
    else:
        return None, None
    


def read_github_output_file():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_OUTPUT_PATH}"
    headers = {"Authorization": f"token {github_key}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = base64.b64decode(response.json()['content']).decode('utf-8')
        return content, response.json()['sha']  # Return file content and SHA (for updating)
    else:
        return None, None
    




# Function to update the file in GitHub

def update_github_file(new_content, sha):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {github_key}"}
    
    data = {
        "message": "Updating user search data",
        "content": base64.b64encode(new_content.encode('utf-8')).decode('utf-8'),
        "sha": sha
    }

    response = requests.put(url, headers=headers, json=data)
    if response.status_code != 200:
        None
    else:
        st.success(".")



def update_github_output_file(new_content, sha):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_OUTPUT_PATH}"
    headers = {"Authorization": f"token {github_key}"}
    
    data = {
        "message": "Updating user search data",
        "content": base64.b64encode(new_content.encode('utf-8')).decode('utf-8'),
        "sha": sha
    }
    
    response = requests.put(url, headers=headers, json=data)
###############################



#states available
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'responses' not in st.session_state:
    st.session_state.responses = []
if 'quiz_finished' not in st.session_state:
    st.session_state.quiz_finished = False
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""


inputs =[]

# directory for text file 
script_dir = Path(__file__).parent.absolute()

# Construct the path to the datasets folder
datasets_dir = os.path.join(script_dir, 'datasets')

os.makedirs(datasets_dir, exist_ok=True)





def clean_mermaid_code(code_block):
    # Split the input block by lines and remove leading/trailing spaces
    lines = code_block.strip().splitlines()

    # Filter out the lines containing triple backticks
    cleaned_lines = [line for line in lines if "```" not in line]

    string = cleaned_lines
    # Join the remaining lines into a single string
    return "\n".join(cleaned_lines)


def mermaid_to_svg(mermaid_code):
    graphbiz_url = "https://mermaid.ink/svg/"
    encoded_mermaid = base64.urlsafe_b64encode(mermaid_code.encode()).decode()
    url = f"{graphbiz_url}{encoded_mermaid}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        return None

def get_svg_download_link(svg_content, filename="diagram.svg"):
    b64 = base64.b64encode(svg_content).decode()
    href = f'<a href="data:image/svg+xml;base64,{b64}" download="{filename}">Download SVG</a>'
    return href



def main():
    title = st.title("DocItUp:")
    st.header("Instantly Transform Ideas into Flow Diagrams with Just One Prompt!")

    st.subheader("Answer the following questions to identify your role in the team\n can choose more than one option if performing multiple roles\n (product manager,software lead ,software developer)")


    if not st.session_state.quiz_finished:
        current_q = questions[st.session_state.current_question]
        
        st.write(f"Question {st.session_state.current_question + 1} of {len(questions)}")
        st.write(current_q["question"])
        
        # Use checkboxes for multiple selections
        selected_options = []
        for option in current_q["options"]:
            if st.checkbox(option, key=f"q_{st.session_state.current_question}_{option}"):
                selected_options.append(option)
        
        if st.button("Submit", key=f"submit_{st.session_state.current_question}"):
            if selected_options:
                st.session_state.responses.append(selected_options)
                
                if st.session_state.current_question < len(questions) - 1:
                    st.session_state.current_question += 1
                else:
                    st.session_state.quiz_finished = True
                
                st.rerun()
            else:
                st.error("Please select at least one option before submitting.")
    else:
        st.write("Quiz completed!")
        st.write("Your responses:")
        for i, response in enumerate(st.session_state.responses):
            st.write(f"Question {i+1}: {', '.join(response)}")
        
        # Role determination logic
        pm_count = sum(any(option in response for option in [
            "Defining product features and roadmap",
            "Market analysis and user needs",
            "Product management software (e.g., Jira, Trello)",
            "Work with cross functional teams"
        ]) for response in st.session_state.responses)
        
        sle_count = sum(any(option in response for option in [
            "Architecting software solutions and managing technical teams",
            "Technical feasibility and resource allocation",
            "Project management and team collaboration tools",
            "Work with software team members mostly "
        ]) for response in st.session_state.responses)
        
        se_count = sum(any(option in response for option in [
            "Writing and debugging code",
            "Implementation details and coding challenges",
            "Integrated Development Environment (IDE)",
            "Work with members within software team "
        ]) for response in st.session_state.responses)
        
        if pm_count >= sle_count and pm_count >= se_count:
            role = "Product Manager"
            text_file = os.path.join(datasets_dir, 'manager.txt')
        elif sle_count >= pm_count and sle_count >= se_count:
            role = "Software Lead Engineer"
            text_file = os.path.join(datasets_dir, 'leadsoftwaremanager.txt')
        else:
            role = "Software Engineer"
            text_file = os.path.join(datasets_dir, 'softwareengineer.txt')
        
        st.markdown("""
        <style>
        .big-font {
            font-size:20px !important;
            font-weight: bold;
        }
        .highlight {
            background-color: #f0f0f0;
            padding: 15px;
            border-radius: 10px;
            border: 2px solid #333;
            color: black;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<p class="big-font">Based on your answers, your role is likely:</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="highlight">{role}</div>', unsafe_allow_html=True)
        
        # Add text input for user feedback
        st.write("Enter a prompt for the flow diagram.")
        user_input = st.text_area("Your input:", value=st.session_state.user_input, height=150)
        
        prompt_user_input = f" {user_input} ,give only mermaid js code , dont write a word more than that.  " 
        
        if st.button("Submit "):
            st.session_state.user_input = user_input
            st.success("Thank you , creating diagram....!")
            # st.write("Your feedback:", st.session_state.user_input)
        
            
            # Process feedback and generate Mermaid diagram
            if user_input:
                answer = get_response_from_gpt3(prompt_user_input,role,text_file)
                code = clean_mermaid_code(answer)
                st.subheader("Generated  Diagram:")
                # mermaid_chart = stmd.st_mermaid(code, height=400)
                render_mermaid(code)
                # showing code also now
                st.subheader("Code to attach in Draw.io (https://app.diagrams.net/) as mermaid extension")
                st.code(code, language='mermaid')
                existing_data, file_sha = read_github_file()
                existing_output_data , output_file_sha = read_github_output_file()
                print(existing_data)
                print(existing_output_data)

                if existing_data is None:
                     updated_text = user_input 
                else:

                    updated_text = existing_data + f"\n{user_input} {role}" 

                update_github_file(updated_text,file_sha)
                

                
                # Get the SVG content
                svg_content = mermaid_to_svg(code)
                
                if svg_content:
                    st.markdown(get_svg_download_link(svg_content), unsafe_allow_html=True)
                    if existing_output_data is None:
                        updated_output_text = code
                    else:
                        updated_output_text = existing_output_data +f"\n{code}"
                    update_github_output_file(updated_output_text,output_file_sha)
                    
                else:
                    # having a way to again retry the code and fix syntax issues  if any .
                    updated_code = correct_mermaid_code(code)
                    # mermaid_chart = stmd.st_mermaid(updated_code , height = 400)
                    render_mermaid(updated_code)
                    svg_content =  mermaid_to_svg(updated_code)
                    st.subheader("updated Code:")
                    st.code(code, language='mermaid')
                    if existing_output_data is None:
                        updated_output_text = updated_code
                    else:
                        updated_output_text = existing_output_data +f"\n{updated_code}"
                    update_github_output_file(updated_output_text,output_file_sha)

            else:
                st.warning("Please enter your diagram requirements.")
        
        if st.button("Restart Quiz"):
            st.session_state.current_question = 0
            st.session_state.responses = []
            st.session_state.quiz_finished = False
            st.session_state.user_input = ""
            st.rerun()
    

    st.markdown("<hr>", unsafe_allow_html=True)  # Optional line separator

    st.markdown(
    """
    <div style='text-align: center;'>
        Made by <strong>Amanem</strong> with ❤️ 
    </div>
    """, 
    unsafe_allow_html=True
)





if __name__ == "__main__":
    main()














