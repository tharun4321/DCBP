def get_user(user_id):
    import sqlite3
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # VULNERABLE: Direct string concatenation in SQL query
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
    
    result = cursor.fetchone()
    conn.close()
    return result

# Example usage
user_input = input("Enter user ID: ")  # Could be malicious: "1 OR 1=1"
user = get_user(user_input)
print(user)