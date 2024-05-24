package com.solver;

import py4j.GatewayServer;

import java.util.List;
import java.util.ArrayList;
import java.util.function.BiFunction;

public class Main {

    private int order;
    private BiFunction<Double, double[], double[]> equationFunction;
    private double initial_x;
    private double[] initial_y;
    private double reach_point;
    private double step_size;

    private List<Double> xValues;
    private List<double[]> yValues;

    public void setOrder(int order) {
        this.order = order;
    }

    public void setEquation(String equation) {
        this.equationFunction = CreateEquationFunction.create(equation, this.order);
    }

    public void setInitialX(double initial_x) {
        this.initial_x = initial_x;
    }

    public void setInitialY(double initial_y) {
        this.initial_y = new double[]{initial_y};
    }

    public void setInitialY(double initial_y1, double initial_y2) {
        this.initial_y = new double[]{initial_y1, initial_y2};
    }

    public void setReachPoint(double reach_point) {
        this.reach_point = reach_point;
    }

    public void setStepSize(double step_size) {
        this.step_size = step_size;
    }

    public double[] getSolution() {
        List<Double> xValues = new ArrayList<>();
        List<double[]> yValues = new ArrayList<>();

        double x = initial_x;
        double[] y = initial_y.clone();

        xValues.clear();
        yValues.clear();
        while (x < reach_point - 1e-10) {
            double[] result = MethodRungeKutta.method(equationFunction, x, y, step_size);
            x = result[0];
            y = new double[result.length - 1];
            System.arraycopy(result, 1, y, 0, result.length - 1);

            xValues.add(x);
            yValues.add(y);
        }
        this.xValues = xValues;
        this.yValues = yValues;

        if (order == 1) {
            return new double[]{x, y[y.length - 1]};
        } else if (order == 2) {
            return new double[]{x, y[0], y[y.length - 1]};
        }
        return null;
    }

    public List<Double> getXValues() { return xValues; }

    public List<double[]> getYValues() { return yValues; }

    public static void main(String[] args) {
        Main main = new Main();
        
        GatewayServer server = new GatewayServer(main);
        
        server.start();
    }
}