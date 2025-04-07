package com.solver;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/solver")
public class SolverController {

    @Autowired
    private Main main;

    @PostMapping("/solve")
    public SolutionResponse solve(@RequestBody SolverRequest request) {
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

        return new SolutionResponse(solution, xValues, yValues);
    }

    @GetMapping("/solution")
    public double[] getSolution() {
        return main.getSolution();
    }

    @GetMapping("/x-values")
    public List<Double> getXValues() {
        return main.getXValues();
    }

    @GetMapping("/y-values")
    public List<double[]> getYValues() {
        return main.getYValues();
    }
}