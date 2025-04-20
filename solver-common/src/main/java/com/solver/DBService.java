package com.solver;

import org.springframework.scheduling.annotation.Async;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.JsonProcessingException;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;
import java.util.HashMap;
import java.util.Map;

@Service
public class DBService {

    @Async
    public CompletableFuture<Optional<String>> getUserSettingsById(Integer userId) {
        return CompletableFuture.supplyAsync(() -> {
            String query = """
                SELECT language, rounding, method
                FROM users
                WHERE id = ?
                """;
            try (Connection conn = DBConnection.getConnection();
                 PreparedStatement stmt = conn.prepareStatement(query)) {
                stmt.setInt(1, userId);
                ResultSet rs = stmt.executeQuery();
                if (rs.next()) {
                    String language = rs.getString("language");
                    String rounding = rs.getString("rounding");
                    String method = rs.getString("method");
                    return Optional.of(
                        String.format(
                            "{\"language\": \"%s\", \"rounding\": \"%s\", \"method\": \"%s\"}",
                            language,
                            rounding,
                            method));
                } else {
                    return Optional.empty();
                }
            } catch (SQLException e) {
                throw new RuntimeException(e);
            }
        });
    }

    @Async
    public CompletableFuture<Optional<String>> setUserSettingsById(Integer userId, String language, String rounding, String method) {
        return CompletableFuture.supplyAsync(() -> {
            String query = """
                INSERT INTO users (id, language, rounding, method)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (id) DO UPDATE
                SET language = EXCLUDED.language,
                    rounding = EXCLUDED.rounding,
                    method = EXCLUDED.method
                """;
            try (Connection conn = DBConnection.getConnection();
                 PreparedStatement stmt = conn.prepareStatement(query)) {
                stmt.setInt(1, userId);
                stmt.setString(2, language);
                stmt.setString(3, rounding);
                stmt.setString(4, method);
                int rowsAffected = stmt.executeUpdate();
                return rowsAffected > 0 ? Optional.of("Settings saved successfully") : Optional.empty();
            } catch (SQLException e) {
                throw new RuntimeException(e);
            }
        });
    }

    @Async
    public CompletableFuture<Integer> createApplication(String parameters, String status) {
        return CompletableFuture.supplyAsync(() -> {
            String query = """
                INSERT INTO applications (user_id, parameters, status)
                VALUES (?, ?::jsonb, ?)
                RETURNING id
                """;
            try (Connection conn = DBConnection.getConnection();
                 PreparedStatement stmt = conn.prepareStatement(query)) {
                stmt.setNull(1, java.sql.Types.INTEGER);
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

    @Async
    public CompletableFuture<Integer> createApplicationWithUserId(String parameters, String status, Integer userId) {
        return CompletableFuture.supplyAsync(() -> {
            String query = """
                INSERT INTO applications (user_id, parameters, status)
                VALUES (?, ?::jsonb, ?)
                RETURNING id
                """;
            try (Connection conn = DBConnection.getConnection();
                 PreparedStatement stmt = conn.prepareStatement(query)) {
                stmt.setInt(1, userId);
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

    @Async
    public CompletableFuture<Optional<String>> getApplicationById(int applicationId) {
        return CompletableFuture.supplyAsync(() -> {
            String query = """
                SELECT parameters
                FROM applications
                WHERE id = ?
                """;
            try (Connection conn = DBConnection.getConnection();
                 PreparedStatement stmt = conn.prepareStatement(query)) {
                stmt.setInt(1, applicationId);
                ResultSet rs = stmt.executeQuery();
                if (rs.next()) {
                    return Optional.of(rs.getString("parameters"));
                } else {
                    return Optional.empty();
                }
            } catch (SQLException e) {
                throw new RuntimeException(e);
            }
        });
    }

    @Async
    public CompletableFuture<List<Map<String, Object>>> getApplicationsByUserId(Integer userId) {
        return CompletableFuture.supplyAsync(() -> {
            String query = """
                SELECT id, parameters, status, created_at, last_updated_at
                FROM applications
                WHERE user_id = ?
                ORDER BY created_at DESC
                """;
            try (Connection conn = DBConnection.getConnection();
                 PreparedStatement stmt = conn.prepareStatement(query)) {
                stmt.setInt(1, userId);
                ResultSet rs = stmt.executeQuery();
                List<Map<String, Object>> applications = new ArrayList<>();
                while (rs.next()) {
                    Map<String, Object> application = new HashMap<>();
                    application.put("id", rs.getInt("id"));
                    application.put("parameters", rs.getString("parameters"));
                    application.put("status", rs.getString("status"));
                    application.put("created_at", rs.getString("created_at"));
                    application.put("last_updated_at", rs.getString("last_updated_at"));
                    applications.add(application);
                }
                return applications;
            } catch (SQLException e) {
                throw new RuntimeException(e);
            }
        });
    }

    @Async
    public CompletableFuture<Optional<List<Double>>> getXValuesByApplicationId(int applicationId) {
        return CompletableFuture.supplyAsync(() -> {
            String query = """
                SELECT jsonb_array_elements_text(data->'xvalues')::double precision AS x_value
                FROM results
                WHERE application_id = ?
                """;
            try (Connection conn = DBConnection.getConnection();
                 PreparedStatement stmt = conn.prepareStatement(query)) {
                stmt.setInt(1, applicationId);
                ResultSet rs = stmt.executeQuery();
                List<Double> xValues = new ArrayList<>();
                while (rs.next()) {
                    xValues.add(rs.getDouble("x_value"));
                }
                return xValues.isEmpty() ? Optional.empty() : Optional.of(xValues);
            } catch (SQLException e) {
                throw new RuntimeException(e);
            }
        });
    }

    @Async
    public CompletableFuture<Optional<List<double[]>>> getYValuesByApplicationId(int applicationId) {
        return CompletableFuture.supplyAsync(() -> {
            String query = """
                SELECT jsonb_array_elements(data->'yvalues')::jsonb AS y_value
                FROM results
                WHERE application_id = ?
                """;
            try (Connection conn = DBConnection.getConnection();
                 PreparedStatement stmt = conn.prepareStatement(query)) {
                stmt.setInt(1, applicationId);
                ResultSet rs = stmt.executeQuery();
                List<double[]> yValues = new ArrayList<>();
                ObjectMapper objectMapper = new ObjectMapper();
                while (rs.next()) {
                    String yValueJson = rs.getString("y_value");
                    yValues.add(objectMapper.readValue(yValueJson, double[].class));
                }
                return yValues.isEmpty() ? Optional.empty() : Optional.of(yValues);
            } catch (SQLException | JsonProcessingException e) {
                throw new RuntimeException(e);
            }
        });
    }

    @Async
    public CompletableFuture<Optional<double[]>> getSolutionByApplicationId(int applicationId) {
        return CompletableFuture.supplyAsync(() -> {
            String query = """
                SELECT data->>'solution' AS solution
                FROM results
                WHERE application_id = ?
                """;
            try (Connection conn = DBConnection.getConnection();
                 PreparedStatement stmt = conn.prepareStatement(query)) {
                stmt.setInt(1, applicationId);
                ResultSet rs = stmt.executeQuery();
                if (rs.next()) {
                    String solutionJson = rs.getString("solution");
                    ObjectMapper objectMapper = new ObjectMapper();
                    return Optional.of(objectMapper.readValue(solutionJson, double[].class));
                } else {
                    return Optional.empty();
                }
            } catch (SQLException | JsonProcessingException e) {
                throw new RuntimeException(e);
            }
        });
    }

    @Async
    public CompletableFuture<Optional<String>> getApplicationStatusByApplicationId(int applicationId) {
        return CompletableFuture.supplyAsync(() -> {
            String query = """
                SELECT status
                FROM applications
                WHERE id = ?
                """;
            try (Connection conn = DBConnection.getConnection();
                 PreparedStatement stmt = conn.prepareStatement(query)) {
                stmt.setInt(1, applicationId);
                ResultSet rs = stmt.executeQuery();
                if (rs.next()) {
                    return Optional.of(rs.getString("status"));
                } else {
                    return Optional.empty();
                }
            } catch (SQLException e) {
                throw new RuntimeException(e);
            }
        });
    }

    @Async
    public CompletableFuture<Optional<String>> getApplicationCreationDateByApplicationId(int applicationId) {
        return CompletableFuture.supplyAsync(() -> {
            String query = """
                SELECT created_at
                FROM applications
                WHERE id = ?
                """;
            try (Connection conn = DBConnection.getConnection();
                PreparedStatement stmt = conn.prepareStatement(query)) {
                stmt.setInt(1, applicationId);
                ResultSet rs = stmt.executeQuery();
                if (rs.next()) {
                    return Optional.of(rs.getString("created_at"));
                } else {
                    return Optional.empty();
                }
            } catch (SQLException e) {
                throw new RuntimeException(e);
            }
        });
    }

    public CompletableFuture<Optional<String>> getApplicationUpdateDateByApplicationId(int applicationId) {
        return CompletableFuture.supplyAsync(() -> {
            String query = """
                SELECT last_updated_at
                FROM applications
                WHERE id = ?
                """;
            try (Connection conn = DBConnection.getConnection();
                PreparedStatement stmt = conn.prepareStatement(query)) {
                stmt.setInt(1, applicationId);
                ResultSet rs = stmt.executeQuery();
                if (rs.next()) {
                    return Optional.of(rs.getString("last_updated_at"));
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
            String query = """
                UPDATE applications
                SET status = ?, last_updated_at = NOW()
                WHERE id = ?
                """;
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
            String query = """
                INSERT INTO results (application_id, data)
                VALUES (?, ?::jsonb)
                """;
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

    @Async
    @Scheduled(cron = "0 0 3 * * *") // Every day at 3:00 AM
    public CompletableFuture<Void> cleanOldApplications() {
        return CompletableFuture.runAsync(() -> {
            String query = """
                WITH ranked_applications AS (
                    SELECT id, user_id, created_at,
                        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS row_num
                    FROM applications
                ),
                to_delete AS (
                    SELECT id
                    FROM ranked_applications
                    WHERE row_num > 5
                    AND created_at < NOW() - INTERVAL '14 days'
                )
                DELETE FROM applications
                WHERE id IN (SELECT id FROM to_delete);
                """;
            try (Connection conn = DBConnection.getConnection();
                 PreparedStatement stmt = conn.prepareStatement(query)) {
                stmt.executeUpdate();
            } catch (SQLException e) {
                throw new RuntimeException(e);
            }
        });
    }
}