import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from io import StringIO
import csv
from models import setup_db, Question, Category
import random

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    
    @app.after_request
    def after_request(response):
        response.headers.add('Accesss-Control-Allow-Headers', 'Content-Type,Authorization' )
        response.headers.add('Accesss-Control-Allow-Methods', 'GET, PUT, PATCH, DELETE, POST, OPTIONS')
        
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    def retrieve_categories():

        selection = Category.query.order_by(Category.id).all()
        
        if len(selection) == 0:
            abort(404)

        data = []
        for category in selection:
            data.append(category.type)
            
        
        # data = [Category.format() for Category in selection]
        
        return jsonify(
            {
                "success": True,
                "categories": data,
                "total_categories": len(selection),
            }
        )


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """


    @app.route("/questions")
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        
        if len(selection) == 0:
            abort(404)

        paginated = paginate_questions(request,selection)

        Qdata = []
        categories = []

        for question in paginated:
            if(Category.query.filter(Category.id == question['category']).first() != None):
                Qdata.append({
                    "id": question['id'],
                    "question" : question['question'],
                    "answer" : question['answer'],
                    "category" : question['category'],
                    "difficulty" : question['difficulty']
                })

        for category in Category.query.all():
            categories.append(category.type)
  
        return jsonify(
            {
                "success": True,
                "questions" : Qdata,
                "total_questions" : len(selection),
                "categories" : categories,
                "total_categories" : len(categories)   
            }
        )

    def paginate_questions(request, selection):
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [Question.format() for Question in selection]

        current_questions = questions[start:end]

        return current_questions


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods = ["DELETE"])
    def delete_questions(question_id):
        
        quest = Question.query.filter(Question.id == question_id).one_or_none()
        if quest is None:
            abort(404)
        try:
            quest.delete()

            return jsonify({

                "success": True,
                "deleted": question_id,
                "questions": paginate_questions(request, Question.query.order_by(Question.id).all()),
                "total_questions": len(Question.query.all()),

            })

        except:
            abort(422)
        
    
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods = ["POST"])
    def create_question():
        body= request.get_json()

         
        new_question = Question(
        body.get("question", None),
        body.get("answer", None),
        body.get("category", None),
        body.get("difficulty", None),
        )
        
        if(new_question.answer is None or new_question.difficulty is None or new_question.question is None or new_question.category is None):
            abort(422)

        try:
            if(len(Question.query.filter(Question.question == new_question.question).all()) > 0):
               abort(422)
                    
            else:
               
                new_question.insert()
                
                return jsonify({
                    "success": True,
                    "question" : new_question.question,
                    "answer" : new_question.answer,
                    "category" : new_question.category,
                    "difficulty" : new_question.difficulty

                })
             
        except:
            abort(422)


    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions/search", methods=['POST'])
    def search_questions():
        
        body= request.get_json()
        if(body is None):
            abort(422)

        search_term=body.get('searchTerm', None)

        q_data = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        
        paginated = paginate_questions(request,q_data)

        Qdata = []
        categories = []

        for question in paginated:
            if(Category.query.filter(Category.id == question['category']).first() != None):
                Qdata.append({
                    "id": question['id'],
                    "question" : question['question'],
                    "answer" : question['answer'],
                    "category" : Category.query.filter(Category.id == question['category']).first().type,
                    "difficulty" : question['difficulty']
                })

                if(categories.count(Category.query.filter(Category.id == question['category']).first().type) <1):
                    categories.append(Category.query.filter(Category.id == question['category']).first().type)
            
  
        return jsonify(
            {
                "success": True,
                "questions" : Qdata,
                "total_questions" : len(q_data),
                "categories" : categories,
                "total_categories" : len(categories)   
            }
        )
        
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:id>/questions", methods=['GET'])
    def question_by_category(id):

        q_data = Question.query.all()
        chosen = Category.query.filter(Category.id == id + 1).first()   
        if(chosen is None):
            abort(404)
        q_data = Question.query.filter(Question.category == str(chosen.id)).all()
        
        paginated = paginate_questions(request,q_data)
        Qdata = []
        categories = []
        
        for question in paginated:
            if(Category.query.filter(Category.id == question['category']).first() != None):
                Qdata.append({
                    "id": question['id'],
                    "question" : question['question'],
                    "answer" : question['answer'],
                    "category" : Category.query.filter(Category.id == question['category']).first().id,
                    "difficulty" : question['difficulty']
                })

                if(categories.count(Category.query.filter(Category.id == question['category']).first().type) <1):
                    categories.append(Category.query.filter(Category.id == question['category']).first().type)
        

        return jsonify(
            {
               "success": True,
                "questions" : Qdata,
                "total_questions" : len(q_data),
                "categories" : categories,
                "total_categories" : len(categories)   
            })
    
    
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/quizzes", methods = ["POST"])
    def quiz():

        body= request.get_json()
        if body is None: 
            abort(422)
        category=body.get('quiz_category', '')
        prior_questions = body.get('previous_questions','')

        if category["type"] != "click" :
            questions_in_category = Question.query.filter(Question.category == str(Category.query.filter(Category.type == category['type']).first().id)).all()
        else:
            questions_in_category = Question.query.all()

        question_options = []
        
        for question in questions_in_category:

             if(prior_questions.count(str(question.id)) == 0):
                 question_options.append(question)
        
        if (len(question_options) >0):
            new_question = question_options[random.randint(0, len(question_options)-1)]
            
            

        else:
            return jsonify({
                "success" : True,
                "previousQuestions" : prior_questions,
                "category":category,

            })
        
        return jsonify({
            "success" : True,
            "question": Question.format(new_question),
            "previousQuestions" : prior_questions,
            "category":category,
            
        })
    

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )



    return app
