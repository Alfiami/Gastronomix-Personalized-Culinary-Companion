from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_admin
from firebase_admin import credentials, firestore, auth
import re, os
import requests
from datetime import datetime
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)
bcrypt = Bcrypt()

url_raw = 'https://raw.githubusercontent.com/Alfiami/Gastronomix-Personalized-Culinary-Companion/master/MachineLearning/Dataset/Dataset%2BHarga.xlsx'
df = pd.read_excel(url_raw)

# Load the KMeans model
kmeans = joblib.load('model_kmeans.pkl')

# Basic recommendations for each type of food
basic_recommendations = {
    'makanan pokok': 'Nasi Merah',
    'makanan tambahan': 'Keripik Tempe',
    'lauk': 'Tahu Telur',
    'sayur': 'Bayam Kukus',
    'buah': 'Semangka, segar',
    'susu': 'Susu sapi, segar'
}

# Initialize Firebase
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

class RegistrationForm:
    def __init__(self, email, password, name, gender,
                 height, weight, allergies, weight_goal):
        self.email = email
        self.password = password
        self.name = name
        self.gender = gender
        self.height = height
        self.weight = weight
        self.allergies = allergies
        self.weight_goal = weight_goal

@app.route('/register', methods=['POST'])
def register():
    try:
        print("Received registration request")
        data = request.json

        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        gender = data.get('gender')
        height = data.get('height')
        weight = data.get('weight')
        allergies = data.get('allergies')
        weight_goal = data.get('weight_goal')

        form = RegistrationForm(email, password, name, gender, height, weight, allergies, weight_goal)

        if validate_registration_form(form):
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            user = auth.create_user(email=email, password=hashed_password)

            user_id = user.uid
            user_ref = db.collection('users').document(user_id)
            user_ref.set({
                'user_id': user_id,
                'email': email,
                'password': hashed_password,
                'name': name,
                'gender': gender,
                'height': height,
                'weight': weight,
                'allergies': allergies,
                'weight_goal': weight_goal,
            })

            recommendations_ref = db.collection('recommendations').document(user_id)
            recommendations_ref.set({
                'recommended_foods': {},
                'kebutuhan_kalori': 0
            })

            print("Registration successful")
            return jsonify({
                "message": "Registration successful",
            }), 200

    except auth.EmailAlreadyExistsError:
        print("Email is already in use")
        return jsonify({"error": "Email is already in use"}), 400
    except Exception as e:
        print(f"Error during registration: {str(e)}")
        return jsonify({"error": str(e)}), 500

    print("Invalid input")
    return jsonify({"error": "Invalid input"}), 400
    
def validate_registration_form(form):
    email_regex = r'\S+@\S+\.\S+'
    if not re.match(email_regex, form.email):
        return False
    if not form.password or len(form.password) < 6:
        return False
    return True

# LOGIN
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    try:
        user = auth.get_user_by_email(email)
        
        stored_hashed_password = db.collection('users').where('email', '==', email).get()[0].to_dict()['password']
        if bcrypt.check_password_hash(stored_hashed_password, password):
            return jsonify({"message": "Login berhasil"}), 200
        else:
            return jsonify({"error": "Password salah"}), 401
    except auth.AuthError as e:
        return jsonify({"error": str(e)}), 401
    except IndexError:
        return jsonify({"error": "Email tidak ditemukan"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/recommend_food/<string:user_id>', methods=['POST'])
def recommend_food(user_id):
    try:
        data = request.json

        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        user_data = db.collection('users').document(user_id).get().to_dict()

        if not user_data:
            return jsonify({"error": "User not found"}), 404

        berat_badan = float(user_data.get('weight', 0))
        berat_badan_tujuan = float(user_data.get('weight_goal', 0))

        budget_makan = data.get('budget_makan')

        # Periksa apakah budget_makan adalah angka
        if not isinstance(budget_makan, (int, float)):
            return jsonify({"error": "Invalid budget_makan value"}), 400

        budget_makan = float(budget_makan)

        kebutuhan_kalori = (15.3 * berat_badan + 679) * (berat_badan_tujuan / berat_badan)

        cluster = kmeans.predict([[kebutuhan_kalori, budget_makan]])[0]
        cluster_data = df[kmeans.labels_ == cluster]

        jenis_makanan = ['makanan pokok', 'makanan tambahan', 'lauk', 'susu', 'sayur', 'buah']
        recommended_foods_dict = {}

        for jenis in jenis_makanan:
            jenis_data = cluster_data[cluster_data['jenis'] == jenis]

            if not jenis_data.empty:
                recommended_food = np.random.choice(jenis_data['makanan'].tolist())
            else:
                recommended_food = basic_recommendations[jenis]

            recommended_foods_dict[jenis] = recommended_food

        recommendations_ref = db.collection('recommendations').document(user_id)
        recommendations_ref.set({
            'recommended_foods': recommended_foods_dict,
            'kebutuhan_kalori': kebutuhan_kalori
        })

        return jsonify({
            "recommended_foods": recommended_foods_dict,
            "kebutuhan_kalori": kebutuhan_kalori
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/save_recommendation', methods=['POST'])
def save_recommendation():
    data = request.json
    user_id = data.get('user_id')

    user_data = db.collection('users').document(user_id).get().to_dict()

    if not user_data:
        return jsonify({"error": "User not found"}), 404

    recommended_foods = data.get('recommended_foods')
    kebutuhan_kalori = data.get('kebutuhan_kalori')

    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d %H:%M:%S")

    recommendations_ref = db.collection('recommendations').document(user_id)
    recommendations_ref.set({
        'recommended_foods': recommended_foods,
        'kebutuhan_kalori': kebutuhan_kalori,
        'tanggal_simpan': date_time.split()[0],
        'waktu_simpan': date_time.split()[1]
    })

    return jsonify({
        "message": "Rekomendasi makanan berhasil disimpan"
    })

@app.route('/get_recommendation/<string:user_id>', methods=['GET'])
def get_recommendation(user_id):
    recommendations = db.collection('recommendations').document(user_id).get().to_dict()

    if not recommendations:
        return jsonify({"error": "Data not found"}), 404

    return jsonify(recommendations), 200

@app.route('/get_profile/<string:user_id>', methods=['GET'])
def get_profile(user_id):
    try:
        print(f"Getting profile for user_id: {user_id}")
        user_data = db.collection('users').document(user_id).get().to_dict()
        print(f"User data retrieved: {user_data}")

        if user_data:
            profile_info = {
                'name': user_data.get('name'),
                'email': user_data.get('email'),
                'weight': user_data.get('weight'),
                'weight_goal': user_data.get('weight_goal')
            }

            return jsonify({"profile": profile_info})
        else:
            return jsonify({"error": "User tidak ditemukan"}), 404
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/edit_profile/<string:user_id>', methods=['POST'])
def edit_profile(user_id):
    data = request.json

    weight = data.get('weight'),
    weight_goal = data.get('weight_goal')

    try:
        user_ref = db.collection('users').document(user_id)
        if user_ref.get().exists:
            user_ref.update({
                'weight': weight,
                'weight_goal': weight_goal,
            })
            return jsonify({"message": "Profil berhasil diubah"})
        else:
            return jsonify({"error": "User tidak ditemukan"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/food_users/<string:user_id>', methods=['POST'])
def add_food_users(user_id):
    data = request.json

    required_fields = ['nama_makanan', 'jumlah_kalori', 'porsi', 'harga']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Data tidak lengkap"}), 400

    name = data['nama_makanan']
    calories = float(data['jumlah_kalori'])
    portion = float(data['porsi'])
    price = float(data['harga'])
    
    try:
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        doc_ref = db.collection('food_users').add({
            'user_id': user_id,
            'nama_makanan': name,
            'jumlah_kalori': calories,
            'porsi': portion,
            'harga': price,
            'tanggal': date_time.split()[0],
            'jam': date_time.split()[1]
        })

        return jsonify({"message": "Data makanan ditambahkan dengan sukses"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/food_history/<string:user_id>', methods=['GET'])
def get_food_history(user_id):
    try:
        # Dapatkan data makanan dari Firestore berdasarkan user_id
        food_history = db.collection('food_users').where('user_id', '==', user_id).stream()

        # Inisialisasi total kalori dan total harga
        total_kalori = 0
        total_harga = 0

        # Convert hasil query menjadi list
        food_history_list = [food.to_dict() for food in food_history]

        # Iterasi melalui riwayat makanan
        for food_item in food_history_list:
            total_kalori += food_item.get('jumlah_kalori', 0)
            total_harga += food_item.get('harga', 0)

        # Buat respons hanya dengan informasi yang diinginkan
        response_data = {
            "food_history": [
                {
                    "nama_makanan": food_item["nama_makanan"],
                    "total_kalori": food_item["jumlah_kalori"],
                    "total_harga": food_item["harga"],
                    "tanggal": food_item["tanggal"],
                    "jam": food_item["jam"]
                }
                for food_item in food_history_list
            ],
            "total_harga": total_harga,
            "total_kalori": total_kalori
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/logout', methods=['POST'])
def logout():
    data = request.json

    user_id = data.get('user_id')

    try:
        auth.revoke_refresh_tokens(user_id)

        return jsonify({"message": "Logout berhasil"})
    except auth.AuthError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
