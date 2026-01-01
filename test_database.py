# test_database.py - DATABASE TESTING & DEBUGGING TOOL
import database as db
import sys

def print_separator():
    print("=" * 60)

def test_database():
    """Complete database testing"""
    print("\n🔧 VISIONMATE DATABASE TESTING TOOL\n")
    print_separator()
    
    # Initialize database
    print("\n1️⃣ Initializing Database...")
    db.init_db()
    print_separator()
    
    # Test registration
    print("\n2️⃣ Testing Registration...")
    test_name = "Test User"
    test_email = "test@example.com"
    test_username = "testuser123"
    test_password = "password123"
    
    print(f"   Name: {test_name}")
    print(f"   Email: {test_email}")
    print(f"   Username: {test_username}")
    print(f"   Password: {test_password}")
    
    result = db.add_user(test_name, test_email, test_username, test_password)
    
    if result is True:
        print("   ✅ Registration successful!")
    else:
        print(f"   ❌ Registration failed: {result}")
    print_separator()
    
    # Test login with correct password
    print("\n3️⃣ Testing Login (Correct Password)...")
    success, response = db.check_user(test_username, test_password)
    
    if success:
        print(f"   ✅ Login successful! Welcome {response}")
    else:
        print(f"   ❌ Login failed: {response}")
    print_separator()
    
    # Test login with wrong password
    print("\n4️⃣ Testing Login (Wrong Password)...")
    success, response = db.check_user(test_username, "wrongpassword")
    
    if success:
        print(f"   ⚠️ SECURITY ISSUE: Login succeeded with wrong password!")
    else:
        print(f"   ✅ Correctly rejected: {response}")
    print_separator()
    
    # Test login with wrong username
    print("\n5️⃣ Testing Login (Wrong Username)...")
    success, response = db.check_user("wronguser", test_password)
    
    if success:
        print(f"   ⚠️ SECURITY ISSUE: Login succeeded with wrong username!")
    else:
        print(f"   ✅ Correctly rejected: {response}")
    print_separator()
    
    # Show all users
    print("\n6️⃣ All Users in Database:")
    users = db.get_all_users()
    
    if users:
        for user in users:
            print(f"\n   📌 User ID: {user['id']}")
            print(f"      Name: {user['name']}")
            print(f"      Email: {user['email']}")
            print(f"      Username: {user['username']}")
            print(f"      Created: {user['created_at']}")
            print(f"      Last Login: {user['last_login']}")
    else:
        print("   ⚠️ No users found")
    print_separator()
    
    # Get user info
    print("\n7️⃣ Getting User Info...")
    user_info = db.get_user_info(test_username)
    
    if user_info:
        print(f"   ✅ User found:")
        print(f"      Name: {user_info['name']}")
        print(f"      Email: {user_info['email']}")
        print(f"      Username: {user_info['username']}")
    else:
        print(f"   ❌ User not found")
    print_separator()
    
    # Cleanup option
    print("\n8️⃣ Cleanup Test User")
    print(f"   Deleting test user: {test_username}")
    deleted = db.delete_user(test_username)
    
    if deleted:
        print(f"   ✅ Test user deleted successfully")
    else:
        print(f"   ⚠️ Could not delete test user")
    print_separator()
    
    print("\n✅ DATABASE TESTING COMPLETE!\n")

def interactive_menu():
    """Interactive menu for database operations"""
    while True:
        print("\n" + "=" * 60)
        print("🗄️  VISIONMATE DATABASE MANAGER")
        print("=" * 60)
        print("\n1. View All Users")
        print("2. Add Test User")
        print("3. Test Login")
        print("4. Delete User")
        print("5. Reset Database")
        print("6. Run Full Test")
        print("7. Exit")
        print("\n" + "=" * 60)
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == "1":
            # View all users
            print("\n📋 ALL USERS:")
            users = db.get_all_users()
            if users:
                for user in users:
                    print(f"\n  ID: {user['id']} | Username: {user['username']}")
                    print(f"  Name: {user['name']}")
                    print(f"  Email: {user['email']}")
                    print(f"  Created: {user['created_at']}")
                    print(f"  Last Login: {user['last_login']}")
                    print("-" * 60)
            else:
                print("  ⚠️ No users in database")
        
        elif choice == "2":
            # Add test user
            print("\n➕ ADD TEST USER:")
            name = input("Enter name (or press Enter for 'Test User'): ").strip() or "Test User"
            email = input("Enter email (or press Enter for 'test@example.com'): ").strip() or "test@example.com"
            username = input("Enter username (or press Enter for 'testuser'): ").strip() or "testuser"
            password = input("Enter password (or press Enter for 'password123'): ").strip() or "password123"
            
            result = db.add_user(name, email, username, password)
            if result is True:
                print(f"✅ User '{username}' added successfully!")
            else:
                print(f"❌ Error: {result}")
        
        elif choice == "3":
            # Test login
            print("\n🔐 TEST LOGIN:")
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            
            success, response = db.check_user(username, password)
            if success:
                print(f"✅ Login successful! Welcome {response}")
            else:
                print(f"❌ Login failed: {response}")
        
        elif choice == "4":
            # Delete user
            print("\n🗑️  DELETE USER:")
            username = input("Enter username to delete: ").strip()
            confirm = input(f"Are you sure you want to delete '{username}'? (yes/no): ").strip().lower()
            
            if confirm == "yes":
                deleted = db.delete_user(username)
                if deleted:
                    print(f"✅ User '{username}' deleted successfully!")
                else:
                    print(f"❌ User '{username}' not found")
            else:
                print("❌ Deletion cancelled")
        
        elif choice == "5":
            # Reset database
            print("\n⚠️  RESET DATABASE:")
            confirm = input("Are you sure? This will DELETE ALL USERS! (yes/no): ").strip().lower()
            
            if confirm == "yes":
                db.reset_database()
                print("✅ Database reset successfully!")
            else:
                print("❌ Reset cancelled")
        
        elif choice == "6":
            # Run full test
            test_database()
        
        elif choice == "7":
            # Exit
            print("\n👋 Goodbye!\n")
            sys.exit(0)
        
        else:
            print("\n❌ Invalid choice. Please enter 1-7.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    db.init_db()
    
    # Check if command line argument provided
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_database()
        elif sys.argv[1] == "reset":
            db.reset_database()
            print("✅ Database reset complete!")
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Available commands: test, reset")
    else:
        # Interactive menu
        interactive_menu()