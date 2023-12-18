from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_admin
from firebase_admin import credentials, firestore, auth
import re
from rekomendasi_api.models import get_recommendation
import requests
from rekomendasi_api.models import load_data_and_model, get_recommendation
import joblib
import pandas as pd
import numpy as np
from flask import jsonify
from datetime import datetime

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


df, kmeans = load_data_and_model()

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
    data = request.json  # Get data from JSON request

    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    gender = data.get('gender')
    height = data.get('height')
    weight = data.get('weight')
    allergies = data.get('allergies')
    weight_goal = data.get('weight_goal')

    form = RegistrationForm(email, password, name, gender,
                            height, weight, allergies, weight_goal)

    if validate_registration_form(form):
        # Hash password before storing it
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            # Create user in Firebase Authentication
            user = auth.create_user(email=email, password=password)

            # Save user data in Firestore (add more fields if needed)
            user_id = user.uid  # Get the unique ID generated by Firebase Authentication
            user_ref = db.collection('users').document(user_id)
            user_ref.set({
                'user_id': user_id,  # Save the user ID in Firestore
                'email': email,
                'password': hashed_password,
                'name': name,
                'gender': gender,
                'height': height,
                'weight': weight,
                'allergies': allergies,
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

#LOGIN
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

# Route `/recommend`
@app.route('/recommend_food/<string:user_id>', methods=['POST'])
def recommend_food(user_id):
    data = request.json

    # Extract data from the request
    berat_badan = data['berat_badan']
    berat_badan_tujuan = data['berat_badan_tujuan']
    budget_makan = data['budget_makan']

    # Calculate the calorie needs based on the provided formula
    kebutuhan_kalori = (15.3 * berat_badan + 679) * (berat_badan_tujuan / berat_badan)

    # Make predictions using the KMeans model
    cluster = kmeans.predict([[kebutuhan_kalori, budget_makan]])[0]
    cluster_data = df[kmeans.labels_ == cluster]

    # Define the list of food types
    jenis_makanan = ['makanan pokok', 'makanan tambahan', 'lauk', 'susu', 'sayur', 'buah']

    # Initialize a dictionary to store recommendations by food type
    recommended_foods_dict = {}

    # Iterate over each food type
    for jenis in jenis_makanan:
        jenis_data = cluster_data[cluster_data['jenis'] == jenis]

        if not jenis_data.empty:
            # Randomly select one recommended food for each type
            recommended_food = np.random.choice(jenis_data['makanan'].tolist())
        else:
            # If no specific recommendation for the type, use basic recommendation
            recommended_food = basic_recommendations[jenis]

        # Store the recommendation in the dictionary
        recommended_foods_dict[jenis] = recommended_food

    # Return the recommendations as JSON
    return jsonify({
        "recommended_foods": recommended_foods_dict,
        "kebutuhan_kalori": kebutuhan_kalori
    })

@app.route('/get_profile/<string:user_id>', methods=['GET'])
def get_profile(user_id):
    try:
        print(f"Getting profile for user_id: {user_id}")
        user_data = db.collection('users').document(user_id).get().to_dict()
        print(f"User data retrieved: {user_data}")

        if user_data:
            # Hanya ambil informasi yang diperlukan
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

# Edit_profile
@app.route('/edit_profile/<string:user_id>', methods=['POST'])
def edit_profile(user_id):
    data = request.json  # Dapatkan data dari permintaan JSON

    # Hanya ambil nilai yang diperlukan dari data
    weight = data.get('weight'),
    weight_goal = data.get('weight_goal')

    try:
        # Periksa apakah pengguna ada di Firestore
        user_ref = db.collection('users').document(user_id)
        if user_ref.get().exists:
            # Update hanya pada data weight_goal di Firestore
            user_ref.update({
                'weight': weight,
                'weight_goal': weight_goal,
            })
            return jsonify({"message": "Profil berhasil diubah"})
        else:
            return jsonify({"error": "User tidak ditemukan"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# input makanan user
@app.route('/food_users/<string:user_id>', methods=['POST'])
def add_food_users(user_id):
    data = request.json

    # Pastikan data yang dibutuhkan tersedia
    required_fields = ['nama_makanan', 'jumlah_kalori', 'porsi', 'harga']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Data tidak lengkap"}), 400

    # Ambil nilai dari data JSON
    name = data['nama_makanan']
    calories = float(data['jumlah_kalori'])
    portion = float(data['porsi'])
    price = float(data['harga'])
    
    try:
        # Simpan data makanan ke Firestore
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        doc_ref = db.collection('food_users').add({
            'user_id': user_id,  # Tambahkan user_id
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

# Riwayat Makan User
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


@app.route('/recommendation_history/<string:user_id>', methods=['GET'])
def get_recommendation_history(user_id):
    try:
        # Dapatkan data rekomendasi dari Firestore berdasarkan user_id
        recommendation_history = db.collection('food_recommendations').where('user_id', '==', user_id).stream()

        # Inisialisasi total kalori dan total harga
        total_kalori = 0
        total_harga = 0

        # Convert hasil query menjadi list
        recommendation_history_list = [recommendation.to_dict() for recommendation in recommendation_history]

        # Iterasi melalui riwayat rekomendasi
        for recommendation_item in recommendation_history_list:
            total_kalori += recommendation_item.get('kebutuhan_kalori', 0)
            # total_harga += recommendation_item.get('total_harga', 0)  # Jika harga perlu dihitung, sesuaikan dengan struktur data rekomendasi

        # Buat respons hanya dengan informasi yang diinginkan
        response_data = {
            "recommendation_history": [
                {
                    "recommended_foods": recommendation_item["recommended_foods"],
                    "kebutuhan_kalori": recommendation_item["kebutuhan_kalori"],
                    "timestamp": recommendation_item["timestamp"]
                }
                for recommendation_item in recommendation_history_list
            ],
            "total_kalori": total_kalori,
            "total_harga": total_harga
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Logout
@app.route('/logout', methods=['POST'])
def logout():
    data = request.json  # Get data from JSON request

    user_id = data.get('user_id')  # Assuming 'user_id' is sent in the request

    try:
        # Revoke the user's session, forcing them to log in again
        auth.revoke_refresh_tokens(user_id)

        return jsonify({"message": "Logout berhasil"})
    except auth.AuthError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)