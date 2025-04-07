package com.solver;

import java.util.function.BiFunction;

import net.objecthunter.exp4j.Expression;
import net.objecthunter.exp4j.ExpressionBuilder;

import java.util.Map;
import java.util.HashMap;

public class CreateEquationFunction {
    public static BiFunction<Double, double[], double[]> create(String equation, int order) {
        if (order < 1) {
            throw new IllegalArgumentException("Order must be at least 1");
        }
        
        return (x, y) -> {
            double[] dydt = new double[order];

            System.arraycopy(y, 1, dydt, 0, order - 1);
            
            dydt[order - 1] = evaluateEquation(equation, x, y);
            return dydt;
        };
    }
    
    private static double evaluateEquation(String equation, double x, double[] y) {
        try {
            equation = equation.replaceAll("y\\[(\\d+)]", "y$1");
            
            ExpressionBuilder builder = new ExpressionBuilder(equation).variable("x");
            
            for (int i = 0; i < y.length; i++) {
                builder.variable("y" + i);
            }
            
            Expression expression = builder.build();
            
            Map<String, Double> variables = new HashMap<>();
            variables.put("x", x);
            for (int i = 0; i < y.length; i++) {
                variables.put("y" + i, y[i]);
            }
            
            expression.setVariables(variables);
            return expression.evaluate();
        } catch (Exception e) {
            throw new RuntimeException("Error: " + equation, e);
        }
    }
}