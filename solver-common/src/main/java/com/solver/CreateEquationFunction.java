package com.solver;

import java.util.function.BiFunction;

import net.objecthunter.exp4j.Expression;
import net.objecthunter.exp4j.ExpressionBuilder;

public class CreateEquationFunction {
    public static BiFunction<Double, double[], double[]> create(String equation, int order) {
        if (order == 1) {
            return (x, y) -> {
                try {
                    Expression expressionObj = new ExpressionBuilder(equation)
                            .variables("x", "y")
                            .build()
                            .setVariable("x", x)
                            .setVariable("y", y[0]);
                    double result = expressionObj.evaluate();
                    return new double[]{result};
                } catch (RuntimeException e) {
                    e.printStackTrace();
                    return new double[]{Double.NaN};
                }
            };
        } else if (order == 2) {
            return (x, y) -> {
                try {
                    Expression expressionObj = new ExpressionBuilder(equation)
                            .variables("x", "y", "z")
                            .build()
                            .setVariable("x", x)
                            .setVariable("y", y[0])
                            .setVariable("z", y[1]);
                    double result = expressionObj.evaluate();
                    return new double[]{y[1], result};
                } catch (RuntimeException e) {
                    e.printStackTrace();
                    return new double[]{Double.NaN, Double.NaN};
                }
            };
        }
        return null;
    }
}
