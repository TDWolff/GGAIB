from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
import google.generativeai as genai
import dotenv
import os

# Load environment variables from .env file
dotenv.load_dotenv()

# Initialize the generative AI model
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Start a chat session with the model
g_model = genai.GenerativeModel('gemini-pro')
chat = g_model.start_chat(history=[])

# Create a Blueprint for the API
chat_api = Blueprint('chat_api', __name__, url_prefix='/api')
api = Api(chat_api)

# Initial instruction to the AI model
chat.send_message("From now on you are a grader, meant to only grade and give feedback on submitted code blocks. You will be given a prompt with certain requirements for a code to fulfill. Then you will be given a block of code and you are to grade this block of code based on the requirements given to you. You will grade the code on a 0 to 1.0 scale, no more no less. If the code meets all the requirements give it a 0.9. If the code is very bad and does not meet the requirements it gets a 0.55 (lowest possible score for a submission, do not go any lower than a 0.55). If some things are wrong then you determine what grade the student deserves between 0.55 to 0.9. If the code goes above and beyond the requirements then it can get above a 0.9, but this should be very rare. You will also give 2-3 sentence of feedback on why the student got the grade they got and what they should do to improve their code submission. Only give back the grade and the feedback, dont reply the rubric and dont say weather its a reused score.")

class ChatAPI:
    class _Chat(Resource):
        def post(self):
            ''' Handle sending a message to the chatbot '''
            try:
                body = request.get_json(force=True)
            except Exception as e:
                return {'message': f'Failed to decode JSON object: {e}'}, 400
            
            prompt = body.get('prompt')
            code_block = body.get('code_block')
            
            if not prompt:
                return {'message': 'Prompt is required'}, 400
            
            if not code_block:
                return {'message': 'Code block is required'}, 400
            
            # Escape double quotes in the code block
            escaped_code_block = code_block.replace('"', '\\"')
            
            try:
                # Send prompt and escaped code block to the AI model and get a response
                message = f"Prompt: {prompt}\n\nCode Block:\n{escaped_code_block}\n\n The code blocks must meet the requirements or at least go near them, if they do not meet the requirements you can give them somewhere between a .55 and .9 depending on how far off they are, if they return a different response with the correct code go a little more towards the .9 side, be a little lenient on the grading. Additionally you need to return your feedback in 1-2 sentences, many code blocks will not follow basic convention of Java ie they might provide code where Main class is not present and instead the code blocks are written off of another class. Make sure you remember that, and if someone gives the same code back to you, make sure that you give the same grade as they havent changed anything, you must remember the previous code blocks and grades given to them. But in your response, only include the note that says you reused the same score if they used the same code, otherwise dont mention anything else about remembering score."
                response = chat.send_message(message)
                return jsonify({'response': response.text})
            except Exception as e:
                return {'message': f'An error occurred: {e}'}, 500

# Add resources to the API
api.add_resource(ChatAPI._Chat, '/grader')

