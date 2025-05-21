package com.solver;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

public class SolverRequest {
    private String method;
    private int order;
    private String userEquation;
    private String formattedEquation;
    private double initialX;
    private double[] initialY;
    private double reachPoint;
    private double stepSize;

    public String getMethod() { return method; }
    public void setMethod(String method) { this.method = method; }

    public int getOrder() { return order; }
    public void setOrder(int order) { this.order = order; }

    public String getUserEquation() { return userEquation; }
    public void setUserEquation(String userEquation) { this.userEquation = userEquation; }

    public String getFormattedEquation() { return formattedEquation; }
    public void setFormattedEquation(String formattedEquation) { this.formattedEquation = formattedEquation; }

    public double getInitialX() { return initialX; }
    public void setInitialX(double initialX) { this.initialX = initialX; }

    public double[] getInitialY() { return initialY; }
    public void setInitialY(double[] initialY) { this.initialY = initialY; }

    public double getReachPoint() { return reachPoint; }
    public void setReachPoint(double reachPoint) { this.reachPoint = reachPoint; }

    public double getStepSize() { return stepSize; }
    public void setStepSize(double stepSize) { this.stepSize = stepSize; }

    public String toJson() {
        ObjectMapper objectMapper = new ObjectMapper();
        try {
            return objectMapper.writeValueAsString(this);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Error converting SolverRequest to JSON", e);
        }
    }
}