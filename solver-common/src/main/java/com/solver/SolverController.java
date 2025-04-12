package com.solver;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.List;
import java.util.concurrent.CompletableFuture;

@RestController
@RequestMapping("/api/solver")
public class SolverController {

    @Autowired
    private Main main;

    @Autowired
    private DBService dbService;

    @PostMapping("/solve")
    public CompletableFuture<SolutionResponse> solve(@RequestBody SolverRequest request) {
        return CompletableFuture.supplyAsync(() -> {
            int applicationId = -1;
            try {
                applicationId = dbService.createApplication(
                    null,
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

    @GetMapping("/solution/{applicationId}")
    public CompletableFuture<SolutionResponse> getSolutionByApplicationId(@PathVariable("applicationId") int applicationId) {
        return dbService.getResultsByApplicationId(applicationId)
                .thenApply(optionalJson -> optionalJson.map(json -> {
                    try {
                        ObjectMapper objectMapper = new ObjectMapper();
                        return objectMapper.readValue(json, SolutionResponse.class);
                    } catch (Exception e) {
                        throw new RuntimeException("Error parsing solution JSON", e);
                    }
                }).orElseThrow(() -> new RuntimeException("Solution not found for applicationId: " + applicationId)));
    }
}