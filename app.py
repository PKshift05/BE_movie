
from flask_cors import CORS
from services import app

CORS(app)
if __name__ == '__main__':
    app.run(debug=True)





