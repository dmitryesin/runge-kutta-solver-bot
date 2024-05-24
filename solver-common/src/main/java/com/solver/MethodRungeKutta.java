package com.solver;

import java.util.function.BiFunction;

public class MethodRungeKutta {
    public static double[] method(BiFunction<Double, double[], double[]> f, double x_0, double[] y_0, double h) {
        double[] result;

        double[] k1 = new double[y_0.length];
        double[] k2 = new double[y_0.length];
        double[] k3 = new double[y_0.length];
        double[] k4 = new double[y_0.length];

        double[] y_1 = new double[y_0.length];

        double[] temp = new double[y_0.length];

        k1 = ArrayOperations.multiply(h, f.apply(x_0, y_0));
        temp = ArrayOperations.add(y_0, ArrayOperations.multiply(0.5, k1));
        k2 = ArrayOperations.multiply(h, f.apply(x_0 + h / 2, temp));
        temp = ArrayOperations.add(y_0, ArrayOperations.multiply(0.5, k2));
        k3 = ArrayOperations.multiply(h, f.apply(x_0 + h / 2, temp));
        temp = ArrayOperations.add(y_0, k3);
        k4 = ArrayOperations.multiply(h, f.apply(x_0 + h, temp));

        for (int i = 0; i < y_0.length; i++) {
            y_1[i] = y_0[i] + (k1[i] + 2*k2[i] + 2*k3[i] + k4[i]) / 6;
        }

        if (y_0.length == 1) {
            result = new double[] {x_0 + h, y_1[0]};
        } else {
            result = new double[y_0.length + 1];
            result[0] = x_0 + h;
            for (int i = 1; i < y_0.length + 1; i++) {
                result[i] = y_1[i - 1];
            }
        }

        return result;
    }
}
