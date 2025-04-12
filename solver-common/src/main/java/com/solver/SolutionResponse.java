package com.solver;

import java.util.List;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

public class SolutionResponse {
    private double[] solution;
    private List<Double> xValues;
    private List<double[]> yValues;

    public SolutionResponse() {}

    @JsonCreator
    public SolutionResponse(
            @JsonProperty("solution") double[] solution,
            @JsonProperty("xValues") List<Double> xValues,
            @JsonProperty("yValues") List<double[]> yValues) {
        this.solution = solution;
        this.xValues = xValues;
        this.yValues = yValues;
    }

    public double[] getSolution() { return solution; }
    public void setSolution(double[] solution) { this.solution = solution; }

    public List<Double> getXValues() { return xValues; }
    public void setXValues(List<Double> xValues) { this.xValues = xValues; }

    public List<double[]> getYValues() { return yValues; }
    public void setYValues(List<double[]> yValues) { this.yValues = yValues; }

    public String toJson() {
        ObjectMapper objectMapper = new ObjectMapper();
        try {
            return objectMapper.writeValueAsString(this);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Error converting SolutionResponse to JSON", e);
        }
    }
}