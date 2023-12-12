from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_admin
from firebase_admin import credentials, firestore, auth
import re

app = Flask(__name__)
bcrypt = Bcrypt()

# Initialize Firebase
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


class RegistrationForm:
    def __init__(self, email, password, name, phone, address, gender,
                 height, weight, allergies, weekly_budget, weight_goal):
        self.email = email
        self.password = password
        self.name = name
        self.phone = phone
        self.address = address
        self.gender = gender
        self.height = height
        self.weight = weight
        self.allergies = allergies
        self.weekly_budget = weekly_budget
        self.weight_goal = weight_goal


@app.route('/register', methods=['POST'])
def register():
    data = request.json  # Get data from JSON request

    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    phone = data.get('phone')
    address = data.get('address')
    gender = data.get('gender')
    height = data.get('height')
    weight = data.get('weight')
    allergies = data.get('allergies')
    weekly_budget = data.get('weekly_budget')
    weight_goal = data.get('weight_goal')

    form = RegistrationForm(email, password, name, phone, address, gender,
                            height, weight, allergies, weekly_budget, weight_goal)

    if validate_registration_form(form):
        # Hash password before storing it
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            # Create user in Firebase Authentication
            auth.create_user(email=email, password=password)

            # Save user data in Firestore (add more fields if needed)
            user_ref = db.collection('users').document()
            user_ref.set({
                'email': email,
                'password': hashed_password,
                'name': name,
                'phone': phone,
                'address': address,
                'gender': gender,
                'height': height,
                'weight': weight,
                'allergies': allergies,
                'weekly_budget': weekly_budget,
                'weight_goal': weight_goal,
            })

            return jsonify({"message": "Registrasi berhasil"})
        except auth.EmailAlreadyExistsError:
            return jsonify({"error": "Email sudah digunakan"}), 400
        except auth.AuthError as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid input"}), 400


def validate_registration_form(form):
    # Perform input validation here
    # Sample validation: ensure email format and password length

    email_regex = r'\S+@\S+\.\S+'
    if not re.match(email_regex, form.email):
        return False
    if not form.password or len(form.password) < 6:
        return False

    return True

@app.route('/login', methods=['POST'])
def login():
    data = request.json  # Get data from JSON request

    email = data.get('email')
    password = data.get('password')

    try:
        # Verify login credentials with Firebase Authentication
        user = auth.get_user_by_email(email)

        # Check if password is correct (using the actual stored hash)
        stored_hashed_password = db.collection('users').where('email', '==', email).get()[0].to_dict()['password']
        if bcrypt.check_password_hash(stored_hashed_password, password):
            return jsonify({"message": "Login berhasil"})
        else:
            return jsonify({"error": "Password salah"}), 401

    except auth.AuthError as e:
        return jsonify({"error": str(e)}), 401
    except IndexError:
        return jsonify({"error": "Email tidak ditemukan"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get_profile/<string:user_id>', methods=['GET'])
def get_profile(user_id):
    try:
        print(f"Getting profile for user_id: {user_id}")
        user_data = db.collection('users').document(user_id).get().to_dict()
        print(f"User data retrieved: {user_data}")

        if user_data:
            return jsonify({"profile": user_data})
        else:
            return jsonify({"error": "User tidak ditemukan"}), 404
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Edit_profile
@app.route('/edit_profile/<string:user_id>', methods=['POST'])
def edit_profile(user_id):
    data = request.json  # Dapatkan data dari permintaan JSON

    name = data.get('name')
    phone = data.get('phone')
    address = data.get('address')
    weekly_budget = data.get('weekly_budget')
    weight_goal = data.get('weight_goal')

    try:
        # Periksa apakah pengguna ada di Firestore
        user_ref = db.collection('users').document(user_id)
        if user_ref.get().exists:
            # Update data pengguna di Firestore
            user_ref.update({
                'name': name,
                'phone': phone,
                'address': address,
                'weekly_budget': weekly_budget,
                'weight_goal': weight_goal,
            })
            return jsonify({"message": "Profil berhasil diubah"})
        else:
            return jsonify({"error": "User tidak ditemukan"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/food_users', methods=['POST'])
def add_food_users():
    data = request.json

    # Pastikan data yang dibutuhkan tersedia
    if 'nama_makanan' not in data or 'jumlah_kalori' not in data or 'porsi' not in data or 'harga' not in data:
        return jsonify({"error": "Data tidak lengkap"}), 400

    # Ambil nilai dari data JSON
    name = data['nama_makanan']
    calories = float(data['jumlah_kalori'])
    portion = float(data['porsi'])
    price = float(data['harga'])
    
    try:
        # Simpan data makanan ke Firestore
        doc_ref = db.collection('food_users').add({
            'nama_makanan': name,
            'jumlah_kalori': calories,
            'porsi': portion,
            'harga': price
        })

        return jsonify({"message": "Data makanan ditambahkan dengan sukses"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


