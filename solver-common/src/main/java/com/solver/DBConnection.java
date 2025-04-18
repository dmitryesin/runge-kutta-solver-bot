package com.solver;

import io.github.cdimascio.dotenv.Dotenv;
import java.sql.*;

public class DBConnection {
    private static final Dotenv dotenv = Dotenv.load();

    private static final String URL = String.format(
        "jdbc:%s://%s:%s/%s",
        dotenv.get("DB_CONNECTION"),
        dotenv.get("DB_HOST"),
        dotenv.get("DB_PORT"),
        dotenv.get("DB_DATABASE")
    );
    private static final String USER = dotenv.get("DB_USERNAME");
    private static final String PASSWORD = dotenv.get("DB_PASSWORD");

    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL, USER, PASSWORD);
    }
}