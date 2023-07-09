from unittest import TestCase

from app import app
from models import db, Users

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

class UserTestCase(TestCase):
    
    def setUp(self):
        """Add sample pet."""

        Users.query.delete()

        user = Users(first_name="Jon", last_name="Snow", image_url="https://media.gq-magazine.co.uk/photos/62ac38f82da9f5f89888eba9/1:1/w_667,h_667,c_limit/jon-snow-series-1200.jpeg")
        db.session.add(user)
        db.session.commit()

        self.user_id = user.id
        self.user = user


    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()


    def test_list_users(self):
        with app.test_client() as client:
            resp = client.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Jon', html)


    def test_add_user(self):
        with app.test_client() as client:
            data = {
              'first_name': 'John',
              'last_name': 'Doe',
              'url': 'https://example.com/johndoe.jpg'
              }
            resp = client.post("/users/new", data = data, follow_redirects=True)
            user = Users.query.filter_by(first_name='John', last_name='Doe').first()
            self.assertEqual(resp.status_code, 200)
            self.assertIsNotNone(user)


    def test_edit_user(self):
        with app.test_client() as client:
            resp = client.get(f'/users/{self.user_id}/edit')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Edit Profile', html)



    def test_delete_user(self):
        with app.test_client() as client:
            resp = client.post(f'/users/{self.user_id}/delete',follow_redirects=True )
            deleted_user = Users.query.get(self.user_id)

            self.assertEqual(resp.status_code, 200)
            self.assertIsNone(deleted_user)