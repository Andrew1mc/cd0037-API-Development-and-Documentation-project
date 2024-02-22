import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_category_retrival(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"],True)
        self.assertNotEqual(data["total_categories"],0)
        self.assertTrue(data["total_categories"])
        self.assertTrue(len(data["categories"]))

    def test_retrieve_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"],True)
        self.assertNotEqual(data["total_questions"],0)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))


    def test_delete_questions(self):
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)

        questions = Question.query.filter(Question.id == 2).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 2)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(questions, None)

    def test_add_question(self):
        res = self.client().post("/questions", json={"question":"Who killed the cat?", "answer":"Curiosity","category":2, "difficulty":3})
        data = json.loads(res.data)
        pass


    def test_search_questions_results(self):
        res = self.client().post("/questions/search", json={"searchTerm": "what"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertEqual(len(data["questions"]), 8)

    def test_search_questions_no_results(self):
        res = self.client().post("/questions/search", json={"searchTerm": "poiahgloihdalgoiuhfdalkgha"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_questions"],0)
        self.assertEqual(len(data["questions"]), 0)


    def test_question_by_category_questions(self):
        res = self.client().get("/categories/0/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertEqual(len(data["questions"]), 3)

        res = self.client().get("/categories/5/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertEqual(len(data["questions"]), 2)

    def test_quizzes(self):
        res = self.client().post("/quizzes", json={'quiz_category': {'type': 'Science', 'id': '0'}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        

    def test_404_if_book_does_not_exist(self):
        res = self.client().delete("/questions/9999")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")


    def test_422_if_question_creation_fails(self):
        res = self.client().post("/questions", json = {"badJson":""})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()