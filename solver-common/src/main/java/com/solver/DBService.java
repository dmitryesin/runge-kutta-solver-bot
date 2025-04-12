package com.solver;

import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.sql.*;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;

@Service
public class DBService {

    @Async
    public CompletableFuture<Integer> createApplication(Integer userId, String parameters, String status) {
        return CompletableFuture.supplyAsync(() -> {
            String query = "INSERT INTO applications (user_id, parameters, status) VALUES (?, ?::jsonb, ?) RETURNING id";
            try (Connection conn = DBConnection.getConnection();
                 PreparedStatement stmt = conn.prepareStatement(query)) {
                if (userId != null) {
                    stmt.setInt(1, userId);
                } else {
                    stmt.setNull(1, java.sql.Types.INTEGER);
                }
                stmt.setString(2, parameters);
                stmt.setString(3, status);
                ResultSet rs = stmt.executeQuery();
                if (rs.next()) {
                    return rs.getInt(1);
                } else {
                    throw new SQLException("Failed to create application");
                }
            } catch (SQLException e) {
                throw new RuntimeException(e);
            }
        });
    }

    public Optional<String> getApplicationById(int applicationId) throws SQLException {
        String query = "SELECT parameters FROM applications WHERE id = ?";
        try (Connection conn = DBConnection.getConnection();
             PreparedStatement stmt = conn.prepareStatement(query)) {
            stmt.setInt(1, applicationId);
            ResultSet rs = stmt.executeQuery();
            if (rs.next()) {
                return Optional.of(rs.getString("parameters"));
            } else {
                return Optional.empty();
            }
        }
    }

    @Async
    public CompletableFuture<Optional<String>> getResultsByApplicationId(int applicationId) {
        return CompletableFuture.supplyAsync(() -> {
            String query = "SELECT data FROM results WHERE application_id = ?";
            try (Connection conn = DBConnection.getConnection();
                 PreparedStatement stmt = conn.prepareStatement(query)) {
                stmt.setInt(1, applicationId);
                ResultSet rs = stmt.executeQuery();
                if (rs.next()) {
                    return Optional.of(rs.getString("data"));
                } else {
                    return Optional.empty();
                }
            } catch (SQLException e) {
                throw new RuntimeException(e);
            }
        });
    }

    @Async
    public CompletableFuture<Void> updateApplicationStatus(int applicationId, String status) {
        return CompletableFuture.runAsync(() -> {
            String query = "UPDATE applications SET status = ?, last_updated_at = NOW() WHERE id = ?";
            try (Connection conn = DBConnection.getConnection();
                 PreparedStatement stmt = conn.prepareStatement(query)) {
                stmt.setString(1, status);
                stmt.setInt(2, applicationId);
                stmt.executeUpdate();
            } catch (SQLException e) {
                throw new RuntimeException(e);
            }
        });
    }

    @Async
    public CompletableFuture<Void> saveResults(int applicationId, String results) {
        return CompletableFuture.runAsync(() -> {
            String query = "INSERT INTO results (application_id, data) VALUES (?, ?::jsonb)";
            try (Connection conn = DBConnection.getConnection();
                 PreparedStatement stmt = conn.prepareStatement(query)) {
                stmt.setInt(1, applicationId);
                stmt.setString(2, results);
                stmt.executeUpdate();
            } catch (SQLException e) {
                throw new RuntimeException(e);
            }
        });
    }
}