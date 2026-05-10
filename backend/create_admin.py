import bcrypt
from database import SessionLocal, User

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def main():
    db = SessionLocal()
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin_user = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            role="admin",
            site="default"
        )
        db.add(admin_user)
        db.commit()
        print("✅ Admin user created: admin / admin123")
    else:
        print("Admin already exists")
    db.close()

if __name__ == "__main__":
    main()