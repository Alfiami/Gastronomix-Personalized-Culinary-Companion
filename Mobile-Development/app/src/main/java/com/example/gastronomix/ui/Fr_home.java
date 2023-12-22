package com.example.gastronomix.ui;

import android.annotation.SuppressLint;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.cardview.widget.CardView;
import androidx.fragment.app.Fragment;

import com.android.volley.Request;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.example.gastronomix.R;
import com.example.gastronomix.data.UserPreference;
import com.example.gastronomix.databinding.FragmentFrHomeBinding;

import org.json.JSONException;
import org.json.JSONObject;

import android.view.inputmethod.InputMethodManager;

public class Fr_home extends Fragment {

    private EditText etBudget;
    private Button btnSend;

    private CardView lyNoFood;
    private LinearLayout lyPredictFood;

    private TextView txtJumlahKalori;

    private TextView txtKarbo;

    private TextView txtProtein;

    private TextView txtSayur;
    private TextView txtSusu;
    private TextView txtBuah;
    private TextView txtTambahan;

    private FragmentFrHomeBinding frHomeBinding = null;

    private String userId = "";
    private SharedPreferences preferences = null;

    public Fr_home() {
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        frHomeBinding = FragmentFrHomeBinding.inflate(getLayoutInflater());
        etBudget = frHomeBinding.edtBudget;
        btnSend = frHomeBinding.btnSave;
        lyNoFood = frHomeBinding.lyNoFood;
        preferences = UserPreference.getPreferences(requireContext());

        if (getArguments() != null) {
            userId = getArguments().getString("userId", preferences.getString("userId", ""));
        }
        return frHomeBinding.getRoot();
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        lyPredictFood = view.findViewById(R.id.ly_predict_food);
        txtJumlahKalori = view.findViewById(R.id.tv_jumlah_kalori);
        txtSayur = view.findViewById(R.id.tv_sayur);
        txtSusu = view.findViewById(R.id.tv_susu);
        txtBuah = view.findViewById(R.id.tv_buah);
        txtKarbo = view.findViewById(R.id.tv_karbohidrat);
        txtProtein = view.findViewById(R.id.tv_protein);
        txtTambahan = view.findViewById(R.id.tv_lauk_tambahan);

        btnSend.setOnClickListener((view1) -> {
            closeKeyboard();
            String budgetString = etBudget.getText().toString().trim();

            if (!budgetString.isEmpty()) {
                int budget = Integer.parseInt(budgetString);
                getPredictFood(userId, budget);
            } else {
                Toast.makeText(requireContext(), "Please enter a valid budget", Toast.LENGTH_SHORT).show();
            }
        });


    }


    // Method to close the keyboard
    private void closeKeyboard() {
        View view = getActivity().getCurrentFocus();
        if (view != null) {
            InputMethodManager imm = (InputMethodManager) getActivity().getSystemService(Context.INPUT_METHOD_SERVICE);
            imm.hideSoftInputFromWindow(view.getWindowToken(), 0);
        }
    }

    private void getPredictFood(String userId, Integer budget) {
        String getUserIdUrl = "https://gastronomix-api-txbmicprqq-et.a.run.app/recommend_food/" + userId;
        JSONObject requestData = new JSONObject();
        try {
            requestData.put("budget_makan", budget);
        } catch (JSONException e) {
            e.printStackTrace();
        }

        @SuppressLint("SetTextI18n") JsonObjectRequest request = new JsonObjectRequest(
                Request.Method.POST,
                getUserIdUrl,
                requestData,
                response -> {
                    try {
                        if (response.has("recommended_foods")) {

                            Double kalori = response.getDouble("kebutuhan_kalori");
                            JSONObject recommendedFoods = response.getJSONObject("recommended_foods");


                            String makananPokok = recommendedFoods.getString("makanan pokok");
                            String makananTambahan = recommendedFoods.getString("makanan tambahan");
                            String lauk = recommendedFoods.getString("lauk");
                            String susu = recommendedFoods.getString("susu");
                            String sayur = recommendedFoods.getString("sayur");
                            String buah = recommendedFoods.getString("buah");

                            lyNoFood.setVisibility(View.GONE);

                            txtJumlahKalori.setText(kalori.toString());
                            txtKarbo.setText(makananPokok);
                            txtSayur.setText(sayur);
                            txtSusu.setText(susu);
                            txtBuah.setText(buah);
                            txtProtein.setText(lauk);
                            txtTambahan.setText(makananTambahan);

                            lyPredictFood.setVisibility(View.VISIBLE);


                        } else {
                            String errorMessage = "Gagal mendapat data Predict Food. Tanggapan tidak valid.";
                            Toast.makeText(requireContext(), errorMessage, Toast.LENGTH_SHORT).show();
                            Log.e("Login", errorMessage);
                        }
                    } catch (JSONException e) {
                        e.printStackTrace();
                        String errorMessage = "Gagal mendapat data Predict Food. Kesalahan JSON.";
                        Toast.makeText(requireContext(), errorMessage, Toast.LENGTH_SHORT).show();
                        Log.e("Login", errorMessage);
                    }
                },
                error -> {
                    Log.e("Login", "Error: " + error.toString());
                    String errorMessage = "Gagal mendapat data Predict Food. Kesalahan jaringan.";
                    Toast.makeText(requireContext(), errorMessage, Toast.LENGTH_SHORT).show();
                }
        );

        Volley.newRequestQueue(requireContext()).add(request);

    }


}

