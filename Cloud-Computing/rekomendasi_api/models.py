# models.py
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import joblib

def load_data_and_model():
    # Load the dataset from URL raw
    url_raw = 'https://raw.githubusercontent.com/Alfiami/Gastronomix-Personalized-Culinary-Companion/master/MachineLearning/Dataset/Dataset%2BHarga.xlsx'
    df = pd.read_excel(url_raw)

    # Load the KMeans model
    kmeans = joblib.load('model_kmeans.pkl')

    return df, kmeans

def get_recommendation(data, df, kmeans):
    # Extract data from the request
    berat_badan = data['berat_badan']
    berat_badan_tujuan = data['berat_badan_tujuan']
    budget_makan = data['budget_makan']

    # Calculate the calorie needs based on the provided formula
    kebutuhan_kalori = (15.3 * berat_badan + 679) * (berat_badan_tujuan / berat_badan)

    # Make predictions using the KMeans model
    cluster = kmeans.predict([[kebutuhan_kalori, budget_makan]])[0]
    cluster_data = df[kmeans.labels_ == cluster]
    recommended_foods = cluster_data[['makanan', 'jenis', 'energi_(kal)',
                                      'air_(g)', 'protein_(g)', 'lemak_(g)',
                                      'karbohidrat_(g)', 'serat_(g)', 'Harga (Rp)']].values.tolist()

    # Create a list of food types
    jenis_makanan = ['makanan pokok', 'makanan tambahan', 'lauk', 'susu', 'sayur', 'buah']

    # Basic recommendations for each type of food
    basic_recommendations = {
        'makanan pokok': 'Nasi Merah',
        'makanan tambahan': 'Keripik Tempe',
        'lauk': 'Tahu Telur',
        'sayur': 'Bayam Kukus',
        'buah': 'Semangka, segar',
        'susu': 'Susu sapi, segar'
    }

    # Select one food item from each type (or use basic recommendations)
    recommended_foods_list = []
    for jenis in jenis_makanan:
        jenis_data = df[df['jenis'] == jenis]['makanan'].tolist()
        if len(jenis_data) > 0:
            recommended_food = np.random.choice(jenis_data)
            recommended_foods_list.append(recommended_food)
        else:
            recommended_foods_list.append(basic_recommendations[jenis])

    return {
        "recommended_foods": recommended_foods,
        "jenis_makanan": jenis_makanan,
        "kebutuhan_kalori": kebutuhan_kalori
    }
