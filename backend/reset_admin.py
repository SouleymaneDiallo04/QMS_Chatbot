import bcrypt
from database import SessionLocal, User

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def main():
    db = SessionLocal()
    admin = db.query(User).filter(User.username == "admin").first()
    if admin:
        new_hash = get_password_hash("admin123")
        admin.password_hash = new_hash
        db.commit()
        print("✅ Mot de passe admin réinitialisé à 'admin123'")
    else:
        print("Admin non trouvé, création...")
        admin_user = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            role="admin",
            site="default"
        )
        db.add(admin_user)
        db.commit()
        print("✅ Admin créé avec admin/admin123")
    db.close()

if __name__ == "__main__":
    main()