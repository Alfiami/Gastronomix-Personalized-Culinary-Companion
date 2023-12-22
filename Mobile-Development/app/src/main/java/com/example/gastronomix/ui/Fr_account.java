package com.example.gastronomix.ui;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.android.volley.Request;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.example.gastronomix.R;
import com.example.gastronomix.data.UserPreference;
import com.example.gastronomix.databinding.FragmentFrAccountBinding;
import com.example.gastronomix.databinding.FragmentFrHomeBinding;

import org.json.JSONException;
import org.json.JSONObject;


public class Fr_account extends Fragment {

    private SharedPreferences preferences = null;

    private FragmentFrAccountBinding fragmentFrAccountBinding = null;

    private String userId = "";
    private Button btnLogout;

    private EditText edtNama;
    private EditText edtEmail;
    private EditText edtBerat;
    private EditText edtTujuan;

    public Fr_account() {

    }


    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        fragmentFrAccountBinding = FragmentFrAccountBinding.inflate(getLayoutInflater());
        preferences = UserPreference.getPreferences(requireContext());
        btnLogout = fragmentFrAccountBinding.btnLogout;
        edtNama = fragmentFrAccountBinding.edtNamaProfile;
        edtEmail = fragmentFrAccountBinding.edtEmailProfile;
        edtBerat = fragmentFrAccountBinding.edtBeratProfile;
        edtTujuan = fragmentFrAccountBinding.edtTujuanProfile;


        if (getArguments() != null) {
            userId = getArguments().getString("userId", preferences.getString("userId", ""));

        }

        getUserProfile(userId);


        return fragmentFrAccountBinding.getRoot();
    }


    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        btnLogout.setOnClickListener((view1 -> {

            SharedPreferences.Editor editor = preferences.edit();
            editor.putString("userId", "");
            editor.apply();

            Intent intent = new Intent(requireContext(), Login.class);
            intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TASK | Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
            requireActivity().finish();

        }));

    }


    private void getUserProfile(String userId) {
        String getUserProfileUrl = "https://gastronomix-api-txbmicprqq-et.a.run.app/get_profile/" + userId;

        JSONObject requestData = new JSONObject();

        JsonObjectRequest request = new JsonObjectRequest(
                Request.Method.GET,
                getUserProfileUrl,
                requestData,
                response -> {
                    try {
                        if (response.has("profile")) {
                            JSONObject userProfile = response.getJSONObject("profile");

                            String nama = userProfile.getString("name");
                            String email = userProfile.getString("email");
                            String berat = userProfile.getString("weight");
                            String tujuan = userProfile.getString("weight_goal");

                            edtNama.setText(nama);
                            edtEmail.setText(email);
                            edtBerat.setText(berat);
                            edtTujuan.setText(tujuan);


                        } else {
                            String errorMessage = "Gagal mendapat data user profile. Tanggapan tidak valid.";
                            Toast.makeText(requireContext(), errorMessage, Toast.LENGTH_SHORT).show();
                            Log.e("Get Profile", errorMessage);
                        }
                    } catch (JSONException e) {
                        e.printStackTrace();
                        String errorMessage = "Gagal mendapat data user profile. Kesalahan JSON.";
                        Toast.makeText(requireContext(), errorMessage, Toast.LENGTH_SHORT).show();
                        Log.e("Get Profile", errorMessage);
                    }
                },
                error -> {
                    Log.e("Get Profile", "Error: " + error.toString());
                    String errorMessage = "Gagal mendapat data user profile. Kesalahan jaringan.";
                    Toast.makeText(requireContext(), errorMessage, Toast.LENGTH_SHORT).show();
                }
        );

        Volley.newRequestQueue(requireContext()).add(request);

    }
}