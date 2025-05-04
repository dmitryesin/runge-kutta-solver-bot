package com.solver;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.concurrent.CompletableFuture;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/solver")
public class SolverController {

    @Autowired
    private Main main;

    @Autowired
    private DBService dbService;

    @PostMapping("/users/{userId}")
    public CompletableFuture<String> setUserSettingsById(
            @PathVariable("userId") Integer userId,
            @RequestParam("language") String language,
            @RequestParam("rounding") String rounding,
            @RequestParam("method") String method) {
        return dbService.setUserSettingsById(userId, language, rounding, method)
                .thenApply(optionalResult -> optionalResult.orElseThrow(() -> 
                    new RuntimeException("Failed to update settings for userId: " + userId)));
    }

    @PostMapping("/solve")
    public CompletableFuture<SolutionResponse> solve(@RequestBody SolverRequest request) {
        return CompletableFuture.supplyAsync(() -> {
            int applicationId = -1;
            try {
                applicationId = dbService.createApplication(
                    request.toJson(),
                    "new"
                ).join();

                dbService.updateApplicationStatus(applicationId, "in_progress");

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

                dbService.saveResults(applicationId, new SolutionResponse(solution, xValues, yValues).toJson());

                dbService.updateApplicationStatus(applicationId, "completed");

                return new SolutionResponse(solution, xValues, yValues);
            } catch (Exception e) {
                if (applicationId != -1) {
                    try {
                        dbService.updateApplicationStatus(applicationId, "error");
                    } catch (Exception sqlException) {
                        sqlException.printStackTrace();
                    }
                }
                throw new RuntimeException("Error solving the problem", e);
            }
        });
    }

    @PostMapping("/solve/{userId}")
    public CompletableFuture<Integer> solveWithUserId(
            @PathVariable("userId") Integer userId,
            @RequestBody SolverRequest request) {
        return CompletableFuture.supplyAsync(() -> {
            final int applicationId;
            try {
                applicationId = dbService.createApplicationWithUserId(
                    request.toJson(),
                    "new", 
                    userId
                ).join();

                CompletableFuture.runAsync(() -> {
                    try {
                        dbService.updateApplicationStatus(applicationId, "in_progress");

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

                        dbService.saveResults(applicationId, new SolutionResponse(solution, xValues, yValues).toJson());
                        dbService.updateApplicationStatus(applicationId, "completed");
                    } catch (Exception e) {
                        try {
                            dbService.updateApplicationStatus(applicationId, "error");
                        } catch (Exception sqlException) {
                            sqlException.printStackTrace();
                        }
                    }
                });

                return applicationId;
            } catch (Exception e) {
                throw new RuntimeException("Error creating application", e);
            }
        });
    }

    @GetMapping("/users/{userId}")
    public CompletableFuture<String> getUserSettingsById(@PathVariable("userId") Integer userId) {
        return dbService.getUserSettingsById(userId)
                .thenApply(optionalSettings -> optionalSettings.orElseThrow(() -> 
                    new RuntimeException("User settings not found for userId: " + userId)));
    }

    @GetMapping("/applications/{applicationId}/status")
    public CompletableFuture<String> getApplicationStatusByApplicationId(@PathVariable("applicationId") int applicationId) {
        return dbService.getApplicationStatusByApplicationId(applicationId)
                .thenApply(optionalStatus -> optionalStatus.orElseThrow(() -> 
                    new RuntimeException("Application status not found for applicationId: " + applicationId)));
    }

    @GetMapping("/applications/list/{userId}")
    public CompletableFuture<List<Map<String, Object>>> getApplicationsByUserId(@PathVariable("userId") Integer userId) {
        return dbService.getApplicationsByUserId(userId)
                .thenApply(applications -> {
                    if (applications.isEmpty()) {
                        throw new RuntimeException("Applications not found for userId: " + userId);
                    }
                    return applications;
                });
    }

    @GetMapping("/results/{applicationId}/solution")
    public CompletableFuture<double[]> getSolutionByApplicationId(@PathVariable("applicationId") int applicationId) {
        return dbService.getSolutionByApplicationId(applicationId)
                .thenApply(optionalSolution -> optionalSolution.orElseThrow(() -> 
                    new RuntimeException("Solution not found for applicationId: " + applicationId)));
    }

    @GetMapping("/results/{applicationId}/xvalues")
    public CompletableFuture<List<Double>> getXValuesByApplicationId(@PathVariable("applicationId") int applicationId) {
        return dbService.getXValuesByApplicationId(applicationId)
                .thenApply(optionalXValues -> optionalXValues.orElseThrow(() -> 
                    new RuntimeException("xValues not found for applicationId: " + applicationId)));
    }

    @GetMapping("/results/{applicationId}/yvalues")
    public CompletableFuture<List<double[]>> getYValuesByApplicationId(@PathVariable("applicationId") int applicationId) {
        return dbService.getYValuesByApplicationId(applicationId)
                .thenApply(optionalYValues -> optionalYValues.orElseThrow(() -> 
                    new RuntimeException("yValues not found for applicationId: " + applicationId)));
    }
}