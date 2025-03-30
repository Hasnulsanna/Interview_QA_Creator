prompt_template = """
You are an expert in Sustainable Development Goals (SDGs) and global sustainability initiatives.  
Your goal is to help individuals, students, and professionals deepen their understanding of SDGs  
by generating insightful and thought-provoking questions based on the text below:  

------------  
{text}  
------------  

Create questions that will enhance understanding and encourage critical thinking about the SDGs.  
Ensure that the questions cover key concepts, challenges, and solutions related to sustainable development.  

QUESTIONS:
"""

# We can use a refine template to make the answer better , its by giving the prev generated questions to a new refined prompt template to check if there is any irrevelant questions avaiable 

refine_template = ("""
You are an expert in sustainable development and global initiatives.  
Your goal is to provide well-informed, accurate, and insightful answers related to the United Nations’ Sustainable Development Goals (SDGs).  

We have received an initial answer: {existing_answer}.  
We have the option to refine this response or provide additional details if necessary, based on the context below.  

------------  
{text}  
------------  

Given the new context, refine or expand the original response in English.  
If the context does not add relevant information, please provide the original response.  

ANSWER:  
"""
)
