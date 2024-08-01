import os

from dotenv import load_dotenv
from waitress import serve

from core import app, db    

load_dotenv()

with app.app_context():
    db.create_all()


mode = os.getenv("ENVIRONMENT")

if __name__ == "__main__":
    if mode == "prod":
        serve(app, host="0.0.0.0", port=8000, threads=4)
    else:
        app.run(host="0.0.0.0", port=8080, debug=True)
