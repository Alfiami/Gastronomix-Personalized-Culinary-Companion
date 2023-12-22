package com.example.gastronomix.ui;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.cardview.widget.CardView;

import com.android.volley.Request;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.example.gastronomix.R;
import com.example.gastronomix.data.UserPreference;

import org.json.JSONException;
import org.json.JSONObject;

public class Login extends AppCompatActivity {

    private EditText etEmail;
    private EditText etPassword;

    private SharedPreferences preferences = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        preferences = UserPreference.getPreferences(this);

        etEmail = findViewById(R.id.login_email);
        etPassword = findViewById(R.id.login_password);

        Button btnLogin = findViewById(R.id.btn_login);
        btnLogin.setOnClickListener(view -> loginUser());

        TextView tvGotoRegis = findViewById(R.id.goto_regis);
        tvGotoRegis.setOnClickListener(view -> {
            Intent intent = new Intent(Login.this, Registrasi.class);
            startActivity(intent);
        });


    }

    private void loginUser() {
        String email = etEmail.getText().toString().trim();
        String password = etPassword.getText().toString().trim();

        String loginUrl = "https://gastronomix-api-txbmicprqq-et.a.run.app/login";

        JSONObject requestData = new JSONObject();
        try {
            requestData.put("email", email);
            requestData.put("password", password);
        } catch (JSONException e) {
            e.printStackTrace();
        }

        JsonObjectRequest request = new JsonObjectRequest(
                Request.Method.POST,
                loginUrl,
                requestData,
                response -> {
                    try {
                        if (response.has("message")) {
                            String message = response.getString("message");
                            Toast.makeText(Login.this, message, Toast.LENGTH_SHORT).show();

                            // TODO: Implementasi pindah ke halaman Home_Screen atau lakukan tindakan lain
                            getUserId(email);
                        } else {
                            String errorMessage = "Gagal melakukan login. Tanggapan tidak valid.";
                            Toast.makeText(Login.this, errorMessage, Toast.LENGTH_SHORT).show();
                            Log.e("Login", errorMessage);
                        }
                    } catch (JSONException e) {
                        e.printStackTrace();
                        String errorMessage = "Gagal melakukan login. Kesalahan JSON.";
                        Toast.makeText(Login.this, errorMessage, Toast.LENGTH_SHORT).show();
                        Log.e("Login", errorMessage);
                    }
                },
                error -> {
                    Log.e("Login", "Error: " + error.toString());
                    String errorMessage = "Gagal melakukan login. Kesalahan jaringan.";
                    Toast.makeText(Login.this, errorMessage, Toast.LENGTH_SHORT).show();
                }
        );

        Volley.newRequestQueue(Login.this).add(request);
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

                            startActivity(new Intent(Login.this, Home_Screen.class).putExtra("userId", preferences.getString("userId", "")));
                            finish(); // Tutup halaman login agar tidak bisa kembali

                        } else {
                            String errorMessage = "Gagal mendapat data userId. Tanggapan tidak valid.";
                            Toast.makeText(this, errorMessage, Toast.LENGTH_SHORT).show();
                            Log.e("Login", errorMessage);
                        }
                    } catch (JSONException e) {
                        e.printStackTrace();
                        String errorMessage = "Gagal mendapat data userId. Kesalahan JSON.";
                        Toast.makeText(this, errorMessage, Toast.LENGTH_SHORT).show();
                        Log.e("Login", errorMessage);
                    }
                },
                error -> {
                    Log.e("Login", "Error: " + error.toString());
                    String errorMessage = "Gagal mendapat data userId. Kesalahan jaringan.";
                    Toast.makeText(this, errorMessage, Toast.LENGTH_SHORT).show();
                }
        );

        Volley.newRequestQueue(this).add(request);

    }
}
