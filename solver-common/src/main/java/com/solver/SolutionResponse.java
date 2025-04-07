package com.solver;

import java.util.List;

public class SolutionResponse {
    private double[] solution;
    private List<Double> xValues;
    private List<double[]> yValues;

    public SolutionResponse(double[] solution, List<Double> xValues, List<double[]> yValues) {
        this.solution = solution;
        this.xValues = xValues;
        this.yValues = yValues;
    }

    public double[] getSolution() { return solution; }
    public List<Double> getXValues() { return xValues; }
    public List<double[]> getYValues() { return yValues; }
}