from flask_restful import Resource
class HomePage(Resource):
    def get(self):
        return render_template('hello.html', **{"greeting": "Hello from Flask!"})