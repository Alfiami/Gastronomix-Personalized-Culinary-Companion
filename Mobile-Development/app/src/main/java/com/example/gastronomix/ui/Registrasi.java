package com.example.gastronomix.ui;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.Request;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.example.gastronomix.R;
import com.example.gastronomix.data.UserPreference;
import com.example.gastronomix.databinding.ActivityRegistrasiBinding;

import org.json.JSONException;
import org.json.JSONObject;

public class Registrasi extends AppCompatActivity {
    TextView gotoLogin;
    private SharedPreferences preferences = null;
    private ActivityRegistrasiBinding activityRegistrasiBinding = null;

    private EditText edtNama;
    private EditText edtEmail;
    private EditText edtPassword;
    private EditText edtTinggi;
    private EditText edtAlergi;
    private EditText edtGender;
    private EditText edtBerat;
    private EditText edtTujuan;

    private Button btnRegis;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        activityRegistrasiBinding = ActivityRegistrasiBinding.inflate(getLayoutInflater());
        setContentView(activityRegistrasiBinding.getRoot());

        preferences = UserPreference.getPreferences(this);

        edtNama = activityRegistrasiBinding.edtNama;
        edtEmail = activityRegistrasiBinding.edtEmail;
        edtPassword = activityRegistrasiBinding.edtPassword;
        edtGender = activityRegistrasiBinding.edtGender;
        edtTinggi = activityRegistrasiBinding.edtTinggi;
        edtAlergi = activityRegistrasiBinding.edtAlergi;
        edtBerat = activityRegistrasiBinding.edtBerat;
        edtTujuan = activityRegistrasiBinding.edtTujuan;
        btnRegis = activityRegistrasiBinding.btnRegis;


        gotoLogin = (TextView) findViewById(R.id.goto_login);
        gotoLogin.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent gotologin = new Intent(getApplicationContext(), Login.class);
                startActivity(gotologin);
            }
        });


        btnRegis.setOnClickListener(view -> registration());


    }

    private void registration() {

        String nama = edtNama.getText().toString().trim();
        String email = edtEmail.getText().toString().trim();
        String password = edtPassword.getText().toString().trim();
        String gender = edtGender.getText().toString().trim();
        String tinggi = edtTinggi.getText().toString().trim();
        String alergi = edtAlergi.getText().toString().trim();
        String berat = edtBerat.getText().toString().trim();
        String tujuan = edtTujuan.getText().toString().trim();


        String registerUrl = "https://gastronomix-api-txbmicprqq-et.a.run.app/register";

        JSONObject requestData = new JSONObject();
        try {
            requestData.put("email", email);
            requestData.put("password", password);
            requestData.put("name", nama);
            requestData.put("gender", gender);
            requestData.put("height", tinggi);
            requestData.put("weight", berat);
            requestData.put("allergies", alergi);
            requestData.put("weight_goal", tujuan);
        } catch (JSONException e) {
            e.printStackTrace();
        }

        JsonObjectRequest request = new JsonObjectRequest(
                Request.Method.POST,
                registerUrl,
                requestData,
                response -> {
                    try {
                        if (response.has("message")) {
                            String message = response.getString("message");
                            Toast.makeText(this, message, Toast.LENGTH_SHORT).show();

                            getUserId(email);


                        } else {
                            String errorMessage = "Gagal melakukan registrasi. Tanggapan tidak valid.";
                            Toast.makeText(this, errorMessage, Toast.LENGTH_SHORT).show();
                            Log.e("Regis", errorMessage);
                        }
                    } catch (JSONException e) {
                        e.printStackTrace();
                        String errorMessage = "Gagal melakukan registrasi. Kesalahan JSON.";
                        Toast.makeText(this, errorMessage, Toast.LENGTH_SHORT).show();
                        Log.e("Regis", errorMessage);
                    }
                },
                error -> {
                    Log.e("Regis", "Error: " + error.toString());
                    String errorMessage = "Gagal melakukan registrasi. Kesalahan jaringan.";
                    Toast.makeText(this, errorMessage, Toast.LENGTH_SHORT).show();
                }
        );

        Volley.newRequestQueue(this).add(request);

    }


    private void getUserId(String email) {
        String getUserIdUrl = "https://gastronomix-api-txbmicprqq-et.a.run.app/get_user_id";
        JSONObject requestData = new JSONObject();
        try {
            requestData.put("email", email);
        } catch (JSONException e) {
            e.printStackTrace();
        }

        JsonObjectRequest request = new JsonObjectRequest(
                Request.Method.POST,
                getUserIdUrl,
                requestData,
                response -> {
                    try {
                        if (response.has("user_id")) {
                            // Write a preference
                            SharedPreferences.Editor editor = preferences.edit();
                            editor.putString("userId", response.getString("user_id"));
                            editor.apply();

                            startActivity(new Intent(this, Home_Screen.class).putExtra("userId", preferences.getString("userId", "")));
                            finish(); // Tutup halaman login agar tidak bisa kembali

                        } else {
                            String errorMessage = "Gagal mendapat data userId. Tanggapan tidak valid.";
                            Toast.makeText(this, errorMessage, Toast.LENGTH_SHORT).show();
                            Log.e("Regis", errorMessage);
                        }
                    } catch (JSONException e) {
                        e.printStackTrace();
                        String errorMessage = "Gagal mendapat data userId. Kesalahan JSON.";
                        Toast.makeText(this, errorMessage, Toast.LENGTH_SHORT).show();
                        Log.e("Regis", errorMessage);
                    }
                },
                error -> {
                    Log.e("Regis", "Error: " + error.toString());
                    String errorMessage = "Gagal mendapat data userId. Kesalahan jaringan.";
                    Toast.makeText(this, errorMessage, Toast.LENGTH_SHORT).show();
                }
        );

        Volley.newRequestQueue(this).add(request);

    }
}