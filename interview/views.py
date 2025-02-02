import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
import google.generativeai as genai

# Configure your Google Gemini API key
genai.configure(api_key="AIzaSyCGjJ999Bti0r_aNFBXyythnQXkStLjMFo")

# Index view - where users enter their job role and experience
def index(request):
    if request.method == "POST":
        job_role = request.POST.get("job_role")
        experience = request.POST.get("experience")
        request.session['job_role'] = job_role
        request.session['experience'] = experience
        return redirect('start_interview')
    return render(request, 'index.html')

# Start interview view - generates questions based on the entered job role and experience
def start_interview(request):
    job_role = request.session.get('job_role', 'Software Engineer')
    experience = request.session.get('experience', '0')

    # Generate interview questions
    questions = generate_questions(job_role, experience)
    
    # Save questions in session
    request.session['questions'] = questions  
    request.session['answers'] = []  # Initialize empty list for answers
    
    return redirect('interview_page')  # Redirect to interview page

# Function to generate interview questions based on job role and experience
def generate_questions(job_role, experience):
    prompt = f"Generate 10 technical interview questions for a {job_role} with {experience} years of experience."
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
 # Ensure response text is split properly and remove any numbers from the start of each question
    questions = response.text.strip().split("\n")
    cleaned_questions = [q.lstrip("0123456789. ").strip() for q in questions]  # Remove numbers and spaces at the start of each question
    
    return cleaned_questions

# Interview page view - displays generated interview questions
def interview_page(request):
    current_question_index = request.session.get('current_question_index', 0)
    questions = request.session.get('questions', [])
    
    # Check if we have more questions to ask
    if current_question_index < len(questions):
        question = questions[current_question_index]
    else:
        return redirect('result_page')  # All questions answered, go to results page

    return render(request, 'interview.html', {
        "question": question,  # Pass only the question without the number
    })

# Record answer - records user's speech and stores the answer
def record_answer(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            answer_text = data.get("answer", "")

            if not answer_text:
                return JsonResponse({"error": "No answer provided"}, status=400)

            # Get the current question from the session
            current_question_index = request.session.get('current_question_index', 0)
            questions = request.session.get('questions', [])
            question_text = questions[current_question_index] if current_question_index < len(questions) else ""

            # Store the answer in the session
            answers = request.session.get("answers", [])
            answers.append(answer_text)
            request.session["answers"] = answers

            # Validate the answer and get feedback
            validation_result = validate_answer(question_text, answer_text)

            # After validation, move to the next question
            if current_question_index < len(questions) - 1:
                # Increment only after answer validation
                request.session['current_question_index'] = current_question_index + 1
                next_question = questions[current_question_index + 1]
            else:
                next_question = 'No more questions.'

            return JsonResponse({
                "answer": answer_text,
                "score": validation_result['score'],
                "feedback": validation_result['feedback'],
                "next_question": next_question
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid method, use POST."}, status=405)

# Function to validate the answer using Gemini and generate a score and feedback
from django.shortcuts import render
from django.http import JsonResponse
import google.generativeai as genai
# Function to validate the answer using Gemini and generate a score and feedback
def validate_answer(question_text, answer_text):
    # Create a prompt for the Gemini model
    prompt = f"Evaluate the following answer for the technical interview question: '{question_text}'\nAnswer: '{answer_text}'\nProvide a score out of 10 along with feedback on areas (grammar, language) for improvement."
    
    # Initialize the Gemini model
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    
    # Debugging: Print the raw response
    print("Raw Response from Gemini:", response.text)
    
    if not response.text:
        return {"score": "N/A", "feedback": "No feedback available."}
    
    # Convert the response to lowercase for easier searching
    response_lower = response.text.lower()
    
    # Extract the score
    score = "N/A"
    if "score" in response_lower:
        # Find the position of "score"
        score_index = response_lower.find("score")
        # Extract the text after "score"
        score_text = response.text[score_index:].split()
        # Look for a number in the next few words
        for word in score_text[1:]:  # Skip the word "score"
            if word.isdigit():
                score = word
                break
    
    # Extract the feedback
    feedback = "No feedback available."
    if "feedback" in response_lower:
        # Find the position of "feedback"
        feedback_index = response_lower.find("feedback")
        # Extract the text after "feedback"
        feedback = response.text[feedback_index:].replace("Feedback:", "").strip()
    
    # Debugging: Print parsed score and feedback
    print("Parsed Score:", score)
    print("Parsed Feedback:", feedback)
    
    return {
        "score": score,
        "feedback": feedback
    }
    # Initialize the Gemini model
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    
    # Debugging: Print the raw response
    print("Raw Response from Gemini:", response.text)
    
    if not response.text:
        return {"score": "N/A", "feedback": "No feedback available."}
    
    # Convert the response to lowercase for easier searching
    response_lower = response.text.lower()
    
    # Extract the score
    score = "N/A"
    if "score" in response_lower:
        # Find the position of "score"
        score_index = response_lower.find("score")
        # Extract the text after "score"
        score_text = response.text[score_index:].split()
        # Look for a number in the next few words
        for word in score_text[1:]:  # Skip the word "score"
            if word.isdigit():
                score = word
                break
    
    # Extract the feedback
    feedback = "No feedback available."
    if "feedback" in response_lower:
        # Find the position of "feedback"
        feedback_index = response_lower.find("feedback")
        # Extract the text after "feedback"
        feedback = response.text[feedback_index:].replace("Feedback:", "").strip()
    
    # Debugging: Print parsed score and feedback
    print("Parsed Score:", score)
    print("Parsed Feedback:", feedback)
    
    return {
        "score": score,
        "feedback": feedback
    }

    for line in validation_result:
        if line.lower().startswith("score:"):
            score = line.replace("Score:", "").strip()
        elif line.lower().startswith("feedback:"):
            feedback = line.replace("Feedback:", "").strip()
    
    # Debugging: Print parsed score and feedback
    print("Parsed Score:", score)
    print("Parsed Feedback:", feedback)
    
    # If no score or feedback, return default values
    if not score:
        score = "N/A"
    if not feedback:
        feedback = "No feedback available."
    
    return {
        "score": score,
        "feedback": feedback
    }

# Endpoint to go to the next question after speech is recognized or timeout
def next_question(request):
    questions = request.session.get('questions', [])
    current_question_index = request.session.get('current_question_index', 0)

    # Debugging: Print session data
    print("Session Questions:", questions)
    print("Current Question Index:", current_question_index)

    # Ensure we are not exceeding the number of available questions
    if current_question_index + 1 < len(questions):
        # Increment to the next question after answer is recorded and validated
        request.session['current_question_index'] = current_question_index + 1
        next_question = questions[current_question_index + 1]
        request.session.save()  # Ensure session is saved
        return JsonResponse({'next_question': next_question})
    else:
        return JsonResponse({'next_question': 'No more questions.'})  # No more questions to ask

# Result page view - shows results of the interview and feedback

# Function to extract grammar issues from the feedback
def extract_grammar_issues(feedback):
    if not feedback:
        return "No grammar issues."
    
    # Look for grammar-related keywords
    grammar_keywords = ["grammar", "language", "sentence structure"]
    for keyword in grammar_keywords:
        if keyword in feedback.lower():
            return feedback
    
    return "No grammar issues."

def extract_suggestions(feedback):
    if not feedback:
        return "No suggestions."
    
    # Look for suggestion-related keywords
    suggestion_keywords = ["suggest", "improve", "recommend"]
    for keyword in suggestion_keywords:
        if keyword in feedback.lower():
            return feedback
    
    return "No suggestions."

# Endpoint to go to the next question after speech is recognized or timeout
def next_question(request):
    questions = request.session.get('questions', [])
    current_question_index = request.session.get('current_question_index', 0)

    # Ensure we are not exceeding the number of available questions
    if current_question_index + 1 < len(questions):
        # Increment to the next question after answer is recorded and validated
        request.session['current_question_index'] = current_question_index + 1
        next_question = questions[current_question_index + 1]
        return JsonResponse({'next_question': next_question})
    else:
        return JsonResponse({'next_question': 'No more questions.'})  # No more questions to ask

# Result page view - shows results of the interview and feedback
def result_page(request):
    answers = request.session.get('answers', [])
    questions = request.session.get('questions', [])
    results = []

    for i in range(len(answers)):
        question = questions[i] if i < len(questions) else 'No Question'
        answer = answers[i] if i < len(answers) else 'No Answer'

        # Assuming validate_answer function is used to get the score and feedback
        validation_result = validate_answer(question, answer)
        score = validation_result.get("score", "N/A")
        feedback = validation_result.get("feedback", "No feedback")
        
        # Extract grammar issues and suggestions from the feedback
        grammar = extract_grammar_issues(feedback)
        suggestions = extract_suggestions(feedback)
        
        
        results.append({
            'question': question,
            'answer': answer,
            'score': score,
            'grammar': grammar,
            'improvements': suggestions
        })

    return render(request, 'result.html', {"results": results})

# Function to extract grammar issues from the feedback
def extract_grammar_issues(feedback):
    # Check if feedback is None or empty
    if not feedback:
        return "No grammar issues."
    
    # Assuming feedback contains a section "Grammar issues:"
    if "Grammar issues:" in feedback:
        return feedback.split("Grammar issues:")[1].split("Suggestions:")[0].strip()
    
    return "No grammar issues."

# Function to extract suggestions from the feedback
def extract_suggestions(feedback):
    # Check if feedback is None or empty
    if not feedback:
        return "No suggestions."
    
    # Assuming feedback contains a section "Suggestions:"
    if "Suggestions:" in feedback:
        return feedback.split("Suggestions:")[1].strip()
    
    return "No suggestions."