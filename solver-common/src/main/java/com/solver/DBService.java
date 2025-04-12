package com.solver;

import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.JsonProcessingException;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;
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

    // @Async
    // public CompletableFuture<Optional<String>> getApplicationById(int applicationId) {
    //     return CompletableFuture.supplyAsync(() -> {
    //         String query = "SELECT parameters FROM applications WHERE id = ?";
    //         try (Connection conn = DBConnection.getConnection();
    //              PreparedStatement stmt = conn.prepareStatement(query)) {
    //             stmt.setInt(1, applicationId);
    //             ResultSet rs = stmt.executeQuery();
    //             if (rs.next()) {
    //                 return Optional.of(rs.getString("parameters"));
    //             } else {
    //                 return Optional.empty();
    //             }
    //         } catch (SQLException e) {
    //             throw new RuntimeException(e);
    //         }
    //     });
    // }

    // @Async
    // public CompletableFuture<Optional<String>> getResultsByApplicationId(int applicationId) {
    //     return CompletableFuture.supplyAsync(() -> {
    //         String query = "SELECT data->>'solution' AS solution FROM results WHERE application_id = ?";
    //         try (Connection conn = DBConnection.getConnection();
    //              PreparedStatement stmt = conn.prepareStatement(query)) {
    //             stmt.setInt(1, applicationId);
    //             ResultSet rs = stmt.executeQuery();
    //             if (rs.next()) {
    //                 return Optional.of(rs.getString("solution"));
    //             } else {
    //                 return Optional.empty();
    //             }
    //         } catch (SQLException e) {
    //             throw new RuntimeException(e);
    //         }
    //     });
    // }

    @Async
    public CompletableFuture<Optional<List<Double>>> getXValuesByApplicationId(int applicationId) {
        return CompletableFuture.supplyAsync(() -> {
            String query = "SELECT jsonb_array_elements_text(data->'xvalues')::double precision AS x_value FROM results WHERE application_id = ?";
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
            String query = "SELECT jsonb_array_elements(data->'yvalues')::jsonb AS y_value FROM results WHERE application_id = ?";
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
            String query = "SELECT data->>'solution' AS solution FROM results WHERE application_id = ?";
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