import sys
import os

# Thêm thư mục app vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app.routes import app

if __name__ == "__main__":
    app.run(debug=True)