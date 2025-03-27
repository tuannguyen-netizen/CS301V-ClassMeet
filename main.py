from database.connection import create_database_engine, create_session
from database.models import Base, User, Class, ClassMembership, MembershipRole

def main():
    engine = create_database_engine(
        username='your_username', 
        password='your_password', 
        host='localhost', 
        database='your_database_name'
    )
    
    Base.metadata.create_all(engine)
    
    session = create_session(engine)
    
    try:
        new_user = User(
            username='johndoe', 
            email='john@example.com', 
            password='hashed_password'
        )
        session.add(new_user)
        
        new_class = Class(
            name='Python Programming',
            creator=new_user
        )
        session.add(new_class)
        
        membership = ClassMembership(
            user=new_user,
            class_=new_class,
            role=MembershipRole.teacher
        )
        session.add(membership)
        
        session.commit()
        print("User, class, and membership added successfully!")
    
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    
    finally:
        session.close()

if __name__ == "__main__":
    main()