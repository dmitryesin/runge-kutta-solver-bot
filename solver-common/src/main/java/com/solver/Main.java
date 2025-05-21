package com.solver;

import org.springframework.stereotype.Component;

import java.util.List;
import java.util.ArrayList;
import java.util.function.BiFunction;

@Component
public class Main {
    private int order;
    private BiFunction<Double, double[], double[]> equationFunction;
    private double initial_x;
    private double[] initial_y;
    private double reach_point;
    private double step_size;
    private String method;

    private List<Double> xValues;
    private List<double[]> yValues;

    public void setMethod(String method) {
        this.method = method;
    }

    public void setOrder(int order) {
        this.order = order;
    }

    public void setUserEquation(String userEquation) {}

    public void setEquation(String equation) {
        this.equationFunction = CreateEquationFunction.create(equation, this.order);
    }

    public void setInitialX(double initial_x) {
        this.initial_x = initial_x;
    }

    public void setInitialY(double... initial_y) {
        this.initial_y = initial_y;
    }

    public void setReachPoint(double reach_point) {
        this.reach_point = reach_point;
    }

    public void setStepSize(double step_size) {
        this.step_size = step_size;
    }

    public double[] getSolution() {
        xValues = new ArrayList<>();
        yValues = new ArrayList<>();

        double x = initial_x;
        double[] y = initial_y.clone();

        while (x < reach_point - 1e-10) {
            double[] result = switch (method) {
                case "euler" -> NumericalMethods.methodEuler(equationFunction, x, y, step_size);
                case "midpoint" -> NumericalMethods.methodMidpoint(equationFunction, x, y, step_size);
                case "heun" -> NumericalMethods.methodHeun(equationFunction, x, y, step_size);
                case "rungeKutta" -> NumericalMethods.methodRungeKutta(equationFunction, x, y, step_size);
                case "dormandPrince" -> NumericalMethods.methodDormandPrince(equationFunction, x, y, step_size);
                default -> throw new IllegalArgumentException("Invalid method value: " + method);
            };
            x = result[0];
            y = new double[result.length - 1];
            System.arraycopy(result, 1, y, 0, result.length - 1);

            xValues.add(x);
            yValues.add(y.clone());
        }

        double[] finalSolution = new double[1 + y.length];
        finalSolution[0] = x;
        System.arraycopy(y, 0, finalSolution, 1, y.length);

        return finalSolution;
    }

    public List<Double> getXValues() { return xValues; }

    public List<double[]> getYValues() { return yValues; }
}