import openai
import os
from dotenv import load_dotenv
from pathlib import Path



#the path of the .env file should be in the FLOWAI folder only , else please change accordingly
dotenv_path = Path('flowai/local.env')


load_dotenv()

openai.api_key=os.getenv('api_key')
with open(r"datasets\manager.txt" , 'r') as file:
    filecontent = file.read()
    print(filecontent)

def get_response_from_gpt3(prompt_text , User_role , reference_file):
    with open(reference_file, 'r') as file:
        file_contents = file.read()
    prompt = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f""" 

    As an exceptional Mermaid JS developer, your role extends beyond just coding. You will need to take on the responsibilities of a {User_role}. 
    Your main objective is to design and visualize solutions using flowcharts, mind maps, or graphs that best capture the essence of the user's needs also use {file_contents} as knowledge base for the specific role .

Key tasks:

User-Centered Design: Collaborate with users to understand their requirements, challenges, and objectives. Translate their needs into clear, visual solutions using Mermaid JS, ensuring clarity and functionality.

Lead Software Architecture: You will design modular, scalable systems, presenting high-level architectural diagrams, workflows, and processes. You should ensure the flow of information is seamless and intuitive.

Decision Making: Based on the complexity and type of problem, choose the most appropriate visualization technique (e.g., flowchart for process flow, mind map for brainstorming, or graph for relationships) to communicate the solution effectively.

Iterative Development: Work with development teams to ensure the visual solutions align with software engineering principles, iterating and improving them as necessary.

Technical Leadership: As the Lead Engineer, ensure that the technical solutions are feasible and in line with the overall software architecture, guiding developers on implementation and best practices. 

NOTE : you have to give only mermaid js code ouptut nothing else.           





"""},
            {"role": "user", "content": prompt_text},
        ],
        max_tokens=700,
    )
    return prompt.choices[0].message.content


