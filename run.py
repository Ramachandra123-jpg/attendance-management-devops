from app import create_app
from app import config, db

if __name__ == "__main__":
    print("=========================================")
    print(" Employee Management System - starting up ")
    print("=========================================")

    db.test_connection()

    app = create_app()
    print(f"[OK] Server started at http://localhost:{config.SERVER_PORT}")
    print("     Default login -> username: admin  |  password: admin123")
    app.run(host="0.0.0.0", port=config.SERVER_PORT, debug=False)
