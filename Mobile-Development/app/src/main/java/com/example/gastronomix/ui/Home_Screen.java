package com.example.gastronomix.ui;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.Fragment;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.view.MenuItem;
import android.widget.Toast;

import com.android.volley.Request;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.example.gastronomix.R;

import com.google.android.material.bottomnavigation.BottomNavigationView;

import org.json.JSONException;
import org.json.JSONObject;


public class Home_Screen extends AppCompatActivity implements BottomNavigationView.OnNavigationItemSelectedListener {

    private String userId = "";
    private Bundle bundle = new Bundle();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_home_screen);

        Intent intent = getIntent();
        userId = intent.getStringExtra("userId");

        loadFragment(new Fr_home(), userId);
        BottomNavigationView navigationView = findViewById(R.id.navigation);
        navigationView.setOnNavigationItemSelectedListener(this);

    }

    @Override
    public boolean onNavigationItemSelected(@NonNull MenuItem item) {
        Fragment fragment = null;

        if (item.getItemId() == R.id.fr_home) {
            fragment = new Fr_home();
        } else if (item.getItemId() == R.id.fr_note) {
            fragment = new Fr_note();
        } else if (item.getItemId() == R.id.fr_result) {
            fragment = new Fr_result();
        } else if (item.getItemId() == R.id.fr_account) {
            fragment = new Fr_account();
        }

        return loadFragment(fragment, userId);
    }

    private boolean loadFragment(Fragment fragment, String userId) {
        if (fragment != null) {
            bundle.putString("userId", userId);
            fragment.setArguments(bundle);
            getSupportFragmentManager()
                    .beginTransaction()
                    .replace(R.id.fragment_container, fragment)
                    .commit();
            return true;
        }
        return false;
    }


}

