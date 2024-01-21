package org.lufebe16.util;

public class Smoother {
    private double lastTime = 0.0;
    private double lastDelta = 0.0;
    private double beta = 0.0;
    private double half = 100.0;
    private double range = 0.0;
    private double rangeHalf = 0.0;
    private double rangeMin = 0.0;
    private double rangeMax = 0.0;

    public Smoother(double halfLife)
    {
        half = halfLife;
    }
    public Smoother(double halfLife, double wmin, double wmax)
    {
        half = halfLife;
        range = wmax - wmin;
        rangeHalf = range / 2.0;
        rangeMin = wmin;
        rangeMax = wmax;
    }
    public void updateTime(double curTime)
    {
        if (lastTime > 0.0)
            lastDelta = curTime-lastTime;
            beta = Math.pow(0.5,lastDelta/half);
        lastTime = curTime;
    }
    private double norm(double value)
    {
        while (value < rangeMin) value += range;
        while (value >= rangeMax) value -= range;
        return value;
    }
    public double updateValue(double smoothed, double raw)
    {
        double b = beta;
        if (Double.isNaN(raw)) return smoothed; 
        if (Double.isNaN(smoothed)) b = 0.0;

        if (range != 0.0)
        {
            double s = norm(smoothed);
            double r = norm(raw);
            double d = s - r;
            if (d > rangeHalf)
            {
                d = range - d;
                return norm((range - b*d) + r);
            }
            if (d < -rangeHalf)
            {
                d = -range - d;
                return norm((-range - b*d) + r);
            }
            return norm(b*d + r);
        }
        else
            return b*(smoothed-raw) + raw;
    }
}
