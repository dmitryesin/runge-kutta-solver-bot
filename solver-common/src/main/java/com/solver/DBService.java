package com.solver;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.dao.DataAccessException;
import org.springframework.dao.EmptyResultDataAccessException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.scheduling.annotation.Async;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.concurrent.CompletableFuture;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@Service
public class DBService {

    private final JdbcTemplate jdbcTemplate;

    public DBService(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Async
    @Transactional
    public CompletableFuture<Optional<String>> getUserSettingsById(Integer userId) {
        return CompletableFuture.supplyAsync(() -> {
            String query = """
                SELECT language, rounding, method
                FROM users
                WHERE id = ?
                """;
            
            try {
                return jdbcTemplate.queryForObject(query, (rs, rowNum) -> {
                    String language = rs.getString("language");
                    String rounding = rs.getString("rounding");
                    String method = rs.getString("method");
                    return Optional.of(
                        String.format(
                            "{\"language\": \"%s\", \"rounding\": \"%s\", \"method\": \"%s\"}",
                            language,
                            rounding,
                            method));
                }, userId);
            } catch (EmptyResultDataAccessException e) {
                return Optional.empty();
            } catch (DataAccessException e) {
                throw new RuntimeException(e);
            }
        });
    }

    @Async
    @Transactional
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
            
            try {
                int rowsAffected = jdbcTemplate.update(query, userId, language, rounding, method);
                return rowsAffected > 0 
                    ? Optional.of("Settings saved successfully") 
                    : Optional.empty();
            } catch (DataAccessException e) {
                throw new RuntimeException(e);
            }
        });
    }

    @Async
    @Transactional
    public CompletableFuture<Integer> createApplication(String parameters, String status) {
        return CompletableFuture.supplyAsync(() -> {
            String query = """
                INSERT INTO applications (user_id, parameters, status)
                VALUES (?, ?::jsonb, ?)
                RETURNING id
                """;
            
            try {
                return jdbcTemplate.queryForObject(
                    query,
                    (rs, rowNum) -> rs.getInt("id"),
                    null,
                    parameters,
                    status
                );
            } catch (DataAccessException e) {
                throw new RuntimeException("Failed to create application", e);
            }
        });
    }

    @Async
    @Transactional
    public CompletableFuture<Integer> createApplicationWithUserId(String parameters, String status, Integer userId) {
        return CompletableFuture.supplyAsync(() -> {
            String query = """
                INSERT INTO applications (user_id, parameters, status)
                VALUES (?, ?::jsonb, ?)
                RETURNING id
                """;
            try {
                return jdbcTemplate.queryForObject(
                    query,
                    (rs, rowNum) -> rs.getInt("id"),
                    userId,
                    parameters,
                    status
                );
            } catch (DataAccessException e) {
                throw new RuntimeException("Failed to create application", e);
            }
        });
    }

    @Async
    @Transactional
    public CompletableFuture<List<Map<String, Object>>> getApplicationsByUserId(Integer userId) {
        return CompletableFuture.supplyAsync(() -> {
            String query = """
                SELECT id, parameters, status, created_at, last_updated_at
                FROM applications
                WHERE user_id = ?
                ORDER BY created_at DESC
                """;
            try {
                return jdbcTemplate.query(query, (rs, rowNum) -> {
                    Map<String, Object> application = new HashMap<>();
                    application.put("id", rs.getInt("id"));
                    application.put("parameters", rs.getString("parameters"));
                    application.put("status", rs.getString("status"));
                    application.put("created_at", rs.getString("created_at"));
                    application.put("last_updated_at", rs.getString("last_updated_at"));
                    return application;
                }, userId);
            } catch (DataAccessException e) {
                throw new RuntimeException(e);
            }
        });
    }

    @Async
    @Transactional
    public CompletableFuture<Optional<List<Double>>> getXValuesByApplicationId(int applicationId) {
        return CompletableFuture.supplyAsync(() -> {
            String query = """
                SELECT jsonb_array_elements_text(data->'xvalues')::double precision AS x_value
                FROM results
                WHERE application_id = ?
                """;
            try {
                List<Double> xValues = jdbcTemplate.queryForList(query, Double.class, applicationId);
                return xValues.isEmpty() ? Optional.empty() : Optional.of(xValues);
            } catch (DataAccessException e) {
                throw new RuntimeException(e);
            }
        });
    }

    @Async
    @Transactional
    public CompletableFuture<Optional<List<double[]>>> getYValuesByApplicationId(int applicationId) {
        return CompletableFuture.supplyAsync(() -> {
            String query = """
                SELECT jsonb_array_elements(data->'yvalues')::jsonb AS y_value
                FROM results
                WHERE application_id = ?
                """;
            try {
                List<String> yValuesJson = jdbcTemplate.queryForList(query, String.class, applicationId);
                if (yValuesJson.isEmpty()) {
                    return Optional.empty();
                }
                
                ObjectMapper objectMapper = new ObjectMapper();
                List<double[]> yValues = new ArrayList<>();
                for (String json : yValuesJson) {
                    yValues.add(objectMapper.readValue(json, double[].class));
                }
                return Optional.of(yValues);
            } catch (DataAccessException | JsonProcessingException e) {
                throw new RuntimeException(e);
            }
        });
    }

    @Async
    @Transactional
    public CompletableFuture<Optional<double[]>> getSolutionByApplicationId(int applicationId) {
        return CompletableFuture.supplyAsync(() -> {
            String query = """
                SELECT data->>'solution' AS solution
                FROM results
                WHERE application_id = ?
                """;
            try {
                List<String> solutions = jdbcTemplate.queryForList(query, String.class, applicationId);
                if (solutions.isEmpty()) {
                    return Optional.empty();
                }
                
                ObjectMapper objectMapper = new ObjectMapper();
                return Optional.of(objectMapper.readValue(solutions.getFirst(), double[].class));
            } catch (DataAccessException | JsonProcessingException e) {
                throw new RuntimeException(e);
            }
        });
    }

    @Async
    @Transactional
    public CompletableFuture<Optional<String>> getApplicationStatusByApplicationId(int applicationId) {
        return CompletableFuture.supplyAsync(() -> {
            String query = """
                SELECT status
                FROM applications
                WHERE id = ?
                """;
            try {
                List<String> statuses = jdbcTemplate.queryForList(query, String.class, applicationId);
                return statuses.isEmpty() ? Optional.empty() : Optional.of(statuses.getFirst());
            } catch (DataAccessException e) {
                throw new RuntimeException(e);
            }
        });
    }

    @Async
    @Transactional
    public CompletableFuture<Void> updateApplicationStatus(int applicationId, String status) {
        return CompletableFuture.runAsync(() -> {
            String query = """
                UPDATE applications
                SET status = ?, last_updated_at = NOW()
                WHERE id = ?
                """;
            try {
                jdbcTemplate.update(query, status, applicationId);
            } catch (DataAccessException e) {
                throw new RuntimeException(e);
            }
        });
    }

    @Async
    @Transactional
    public CompletableFuture<Void> saveResults(int applicationId, String results) {
        return CompletableFuture.runAsync(() -> {
            String query = """
                INSERT INTO results (application_id, data)
                VALUES (?, ?::jsonb)
                """;
            try {
                jdbcTemplate.update(query, applicationId, results);
            } catch (DataAccessException e) {
                throw new RuntimeException(e);
            }
        });
    }

    @Async
    @Scheduled(cron = "0 */15 * * * *") // Every 15 minutes
    @Transactional
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
                WHERE id IN (SELECT id FROM to_delete)
                """;
            
            try {
                jdbcTemplate.update(query);
            } catch (DataAccessException e) {
                throw new RuntimeException("Failed to clean old applications", e);
            }
        });
    }
}