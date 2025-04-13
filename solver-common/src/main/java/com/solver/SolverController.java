package com.solver;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.concurrent.CompletableFuture;

@RestController
@RequestMapping("/api/solver")
public class SolverController {

    @Autowired
    private Main main;

    @Autowired
    private DBService dbService;

    @PostMapping("/user-settings/{userId}")
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
                Integer userId = request.getUserId();

                applicationId = dbService.createApplication(
                    userId,
                    request.toJson(),
                    "new"
                ).join();

                dbService.updateApplicationStatus(applicationId, "in_progress");

                main.setMethod(request.getMethod());
                main.setOrder(request.getOrder());
                main.setEquation(request.getEquation());
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

    @GetMapping("/user-settings/{userId}")
    public CompletableFuture<String> getUserSettingsById(@PathVariable("userId") Integer userId) {
        return dbService.getUserSettingsById(userId)
                .thenApply(optionalSettings -> optionalSettings.orElseThrow(() -> 
                    new RuntimeException("User settings not found for userId: " + userId)));
    }

    @GetMapping("/application/{applicationId}")
    public CompletableFuture<String> getApplicationById(@PathVariable("applicationId") int applicationId) {
        return dbService.getApplicationById(applicationId)
                .thenApply(optionalApplication -> optionalApplication.orElseThrow(() -> 
                    new RuntimeException("Application not found for applicationId: " + applicationId)));
    }

    @GetMapping("/solution/{applicationId}")
    public CompletableFuture<double[]> getSolutionByApplicationId(@PathVariable("applicationId") int applicationId) {
        return dbService.getSolutionByApplicationId(applicationId)
                .thenApply(optionalSolution -> optionalSolution.orElseThrow(() -> 
                    new RuntimeException("Solution not found for applicationId: " + applicationId)));
    }

    @GetMapping("/x-values/{applicationId}")
    public CompletableFuture<List<Double>> getXValuesByApplicationId(@PathVariable("applicationId") int applicationId) {
        return dbService.getXValuesByApplicationId(applicationId)
                .thenApply(optionalXValues -> optionalXValues.orElseThrow(() -> 
                    new RuntimeException("xValues not found for applicationId: " + applicationId)));
    }

    @GetMapping("/y-values/{applicationId}")
    public CompletableFuture<List<double[]>> getYValuesByApplicationId(@PathVariable("applicationId") int applicationId) {
        return dbService.getYValuesByApplicationId(applicationId)
                .thenApply(optionalYValues -> optionalYValues.orElseThrow(() -> 
                    new RuntimeException("yValues not found for applicationId: " + applicationId)));
    }
}