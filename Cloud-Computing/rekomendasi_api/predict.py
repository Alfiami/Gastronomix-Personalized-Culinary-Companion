import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import load_model
import pandas as pd

# Load data
df = pd.read_excel('Dataset+Harga.xlsx', sheet_name='Dataset (Gizi + Harga)')

# Pilih fitur yang akan digunakan untuk klastering
X = df[['energi_(kal)', 'Harga (Rp)']]

# Load model KMeans
kmeans_model = load_model('recommendation_model_kmeans.h5')

def get_recommendation(kebutuhan_kalori, budget_makan):
    try:
        # Predict the cluster using KMeans
        cluster = kmeans_model.predict(np.array([[kebutuhan_kalori, budget_makan]]))[0]

        # Define food recommendations based on cluster
        klaster_rekomendasi = {
            0: 'Nasi Merah',
            1: 'Keripik Tempe',
            2: 'Tahu Telur',
            3: 'Bayam Kukus',
            4: 'Semangka, segar',
            5: 'Susu sapi, segar'
        }

        # Map cluster to food recommendation
        recommended_food = klaster_rekomendasi[cluster]

        return recommended_food, cluster.tolist()

    except Exception as e:
        return {'error': str(e)}
