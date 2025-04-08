from app.dao.user_dao import UserDAO
from app.models.user import User

# Khởi tạo UserDAO để tương tác với MongoDB
dao = UserDAO()

# Tạo user mẫu
user = User(
    user_id=1,
    username="test_user",
    email="test@example.com",
    password="testpassword123"
)

# Lưu user vào MongoDB
dao.create(user)
print("User created successfully!")