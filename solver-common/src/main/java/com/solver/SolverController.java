package com.solver;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;

import java.util.concurrent.CompletableFuture;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/solver")
public class SolverController {
    private static final Logger logger = LoggerFactory.getLogger(SolverController.class);

    private final Main main;
    private final DBService dbService;

    public SolverController(Main main, DBService dbService) {
        this.main = main;
        this.dbService = dbService;
    }

    @PostMapping("/users/{userId}")
    public CompletableFuture<ResponseEntity<String>> setUserSettingsById(
            @PathVariable("userId") Integer userId,
            @RequestParam("language") String language,
            @RequestParam("rounding") String rounding,
            @RequestParam("method") String method) {
        logger.debug("Setting user settings for userId: {}", userId);
        return dbService.setUserSettingsById(userId, language, rounding, method)
                .thenApply(optionalResult -> optionalResult
                    .map(ResponseEntity::ok)
                    .orElseThrow(() -> new SolverException("Failed to update settings for userId: " + userId)));
    }

    @PostMapping("/solve")
    public CompletableFuture<ResponseEntity<SolutionResponse>> solve(@RequestBody SolverRequest request) {
        logger.debug("Received solve request: {}", request.toJson());
        return CompletableFuture.supplyAsync(() -> {
            int applicationId = -1;
            try {
                applicationId = dbService.createApplication(
                    request.toJson(),
                    "new"
                ).join();

                logger.debug("Created application with id: {}", applicationId);
                dbService.updateApplicationStatus(applicationId, "in_progress").join();

                main.setMethod(request.getMethod());
                main.setOrder(request.getOrder());
                main.setUserEquation(request.getUserEquation());
                main.setEquation(request.getFormattedEquation());
                main.setInitialX(request.getInitialX());
                main.setInitialY(request.getInitialY());
                main.setReachPoint(request.getReachPoint());
                main.setStepSize(request.getStepSize());

                double[] solution = main.getSolution();
                List<Double> xValues = main.getXValues();
                List<double[]> yValues = main.getYValues();

                SolutionResponse response = new SolutionResponse(solution, xValues, yValues);
                dbService.saveResults(applicationId, response.toJson()).join();
                dbService.updateApplicationStatus(applicationId, "completed").join();

                logger.debug("Successfully solved problem for application id: {}", applicationId);
                return ResponseEntity.ok(response);
            } catch (Exception e) {
                logger.error("Error solving problem for application id: {}", applicationId, e);
                if (applicationId != -1) {
                    try {
                        dbService.updateApplicationStatus(applicationId, "error").join();
                    } catch (Exception sqlException) {
                        logger.error("Failed to update application status to error", sqlException);
                    }
                }
                throw new SolverException("Error solving the problem", e);
            }
        });
    }

    @PostMapping("/solve/{userId}")
    public CompletableFuture<ResponseEntity<Integer>> solveWithUserId(
            @PathVariable("userId") Integer userId,
            @RequestBody SolverRequest request) {
        logger.debug("Received solve request with userId: {}", userId);
        return CompletableFuture.supplyAsync(() -> {
            final int applicationId;
            try {
                applicationId = dbService.createApplicationWithUserId(
                    request.toJson(),
                    "new", 
                    userId
                ).join();

                logger.debug("Created application with id: {} for userId: {}", applicationId, userId);

                CompletableFuture.runAsync(() -> {
                    try {
                        dbService.updateApplicationStatus(applicationId, "in_progress").join();

                        main.setMethod(request.getMethod());
                        main.setOrder(request.getOrder());
                        main.setUserEquation(request.getUserEquation());
                        main.setEquation(request.getFormattedEquation());
                        main.setInitialX(request.getInitialX());
                        main.setInitialY(request.getInitialY());
                        main.setReachPoint(request.getReachPoint());
                        main.setStepSize(request.getStepSize());

                        double[] solution = main.getSolution();
                        List<Double> xValues = main.getXValues();
                        List<double[]> yValues = main.getYValues();

                        SolutionResponse response = new SolutionResponse(solution, xValues, yValues);
                        dbService.saveResults(applicationId, response.toJson()).join();
                        dbService.updateApplicationStatus(applicationId, "completed").join();

                        logger.debug("Successfully solved problem for application id: {}", applicationId);
                    } catch (Exception e) {
                        logger.error("Error solving problem for application id: {}", applicationId, e);
                        try {
                            dbService.updateApplicationStatus(applicationId, "error").join();
                        } catch (Exception sqlException) {
                            logger.error("Failed to update application status to error", sqlException);
                        }
                    }
                });

                return ResponseEntity.ok(applicationId);
            } catch (Exception e) {
                logger.error("Error creating application for userId: {}", userId, e);
                throw new SolverException("Error creating application", e);
            }
        });
    }

    @GetMapping("/users/{userId}")
    public CompletableFuture<ResponseEntity<String>> getUserSettingsById(@PathVariable("userId") Integer userId) {
        logger.debug("Getting user settings for userId: {}", userId);
        return dbService.getUserSettingsById(userId)
                .thenApply(optionalSettings -> optionalSettings
                    .map(ResponseEntity::ok)
                    .orElseThrow(() -> new SolverException("User settings not found for userId: " + userId)));
    }

    @GetMapping("/applications/{applicationId}/status")
    public CompletableFuture<ResponseEntity<String>> getApplicationStatusByApplicationId(@PathVariable("applicationId") int applicationId) {
        logger.debug("Getting application status for id: {}", applicationId);
        return dbService.getApplicationStatusByApplicationId(applicationId)
                .thenApply(optionalStatus -> optionalStatus
                    .map(ResponseEntity::ok)
                    .orElseThrow(() -> new SolverException("Application status not found for applicationId: " + applicationId)));
    }

    @GetMapping("/applications/list/{userId}")
    public CompletableFuture<ResponseEntity<List<Map<String, Object>>>> getApplicationsByUserId(@PathVariable("userId") Integer userId) {
        logger.debug("Getting applications list for userId: {}", userId);
        return dbService.getApplicationsByUserId(userId)
                .thenApply(applications -> {
                    if (applications.isEmpty()) {
                        throw new SolverException("Applications not found for userId: " + userId);
                    }
                    return ResponseEntity.ok(applications);
                });
    }

    @GetMapping("/results/{applicationId}/solution")
    public CompletableFuture<ResponseEntity<double[]>> getSolutionByApplicationId(@PathVariable("applicationId") int applicationId) {
        logger.debug("Getting solution for application id: {}", applicationId);
        return dbService.getSolutionByApplicationId(applicationId)
                .thenApply(optionalSolution -> optionalSolution
                    .map(ResponseEntity::ok)
                    .orElseThrow(() -> new SolverException("Solution not found for applicationId: " + applicationId)));
    }

    @GetMapping("/results/{applicationId}/xvalues")
    public CompletableFuture<ResponseEntity<List<Double>>> getXValuesByApplicationId(@PathVariable("applicationId") int applicationId) {
        logger.debug("Getting x values for application id: {}", applicationId);
        return dbService.getXValuesByApplicationId(applicationId)
                .thenApply(optionalXValues -> optionalXValues
                    .map(ResponseEntity::ok)
                    .orElseThrow(() -> new SolverException("xValues not found for applicationId: " + applicationId)));
    }

    @GetMapping("/results/{applicationId}/yvalues")
    public CompletableFuture<ResponseEntity<List<double[]>>> getYValuesByApplicationId(@PathVariable("applicationId") int applicationId) {
        logger.debug("Getting y values for application id: {}", applicationId);
        return dbService.getYValuesByApplicationId(applicationId)
                .thenApply(optionalYValues -> optionalYValues
                    .map(ResponseEntity::ok)
                    .orElseThrow(() -> new SolverException("yValues not found for applicationId: " + applicationId)));
    }
}