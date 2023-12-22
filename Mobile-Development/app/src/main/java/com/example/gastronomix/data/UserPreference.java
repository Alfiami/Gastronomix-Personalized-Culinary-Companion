package com.example.gastronomix.data;

import android.content.Context;
import android.content.SharedPreferences;

public class UserPreference {

    private static final String PREFERENCES_NAME = "user";

    public static SharedPreferences getPreferences(Context context) {
        return context.getSharedPreferences(PREFERENCES_NAME, Context.MODE_PRIVATE);
    }

}
