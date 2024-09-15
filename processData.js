// Centered moving average function
function centeredMovingAverage(values, windowSize) {
    var result = [];
    var halfWindow = Math.floor(windowSize / 2);

    for (var i = 0; i < values.length; i++) {
        var start = Math.max(0, i - halfWindow);
        var end = Math.min(values.length - 1, i + halfWindow);
        var count = end - start + 1;
        var sum = 0;
        for (var j = start; j <= end; j++) {
            sum += values[j];
        }
        result.push(sum / count);
    }
    return result;
}

// Mean calculation function
function mean(values) {
    var sum = values.reduce(function(a, b) { return a + b; }, 0);
    return sum / values.length;
}

// Standard deviation function
function standardDeviation(values, meanValue) {
    var squareDiffs = values.map(function(value) {
        var diff = value - meanValue;
        return diff * diff;
    });
    var avgSquareDiff = mean(squareDiffs);
    return Math.sqrt(avgSquareDiff);
}

// Modified findPeaks function
function findPeaks(values, prominence) {
    var peaks = [];
    for (var i = 1; i < values.length - 1; i++) {
        if (values[i] > values[i - 1] && values[i] > values[i + 1]) {
            var leftMin = values[i - 1];
            for (var j = i - 1; j >= 0; j--) {
                if (values[j] <= leftMin) {
                    leftMin = values[j];
                } else {
                    break;
                }
            }

            var rightMin = values[i + 1];
            for (var j = i + 1; j < values.length; j++) {
                if (values[j] <= rightMin) {
                    rightMin = values[j];
                } else {
                    break;
                }
            }

            var peakProminence = values[i] - Math.max(leftMin, rightMin);
            if (peakProminence >= prominence) {
                peaks.push({
                    index: i,
                    value: values[i],
                    prominence: peakProminence
                });
            }
        }
    }
    return peaks;
}

// Cross-correlation function
function computeCrossCorrelation(valuesA, valuesB, indexA, indexB, windowSize) {
    var startA = Math.max(0, indexA - Math.floor(windowSize / 2));
    var endA = Math.min(valuesA.length, indexA + Math.floor(windowSize / 2));

    var startB = Math.max(0, indexB - Math.floor(windowSize / 2));
    var endB = Math.min(valuesB.length, indexB + Math.floor(windowSize / 2));

    var windowA = valuesA.slice(startA, endA);
    var windowB = valuesB.slice(startB, endB);

    var length = Math.max(windowA.length, windowB.length);
    while (windowA.length < length) windowA.push(0);
    while (windowB.length < length) windowB.push(0);

    var meanA = mean(windowA);
    var meanB = mean(windowB);

    var numerator = 0;
    var denomA = 0;
    var denomB = 0;

    for (var i = 0; i < length; i++) {
        var diffA = windowA[i] - meanA;
        var diffB = windowB[i] - meanB;
        numerator += diffA * diffB;
        denomA += diffA * diffA;
        denomB += diffB * diffB;
    }

    var denominator = Math.sqrt(denomA * denomB);

    if (denominator == 0) {
        return 0;
    } else {
        return numerator / denominator;
    }
}

// Group peaks function
function groupPeaks(processedSignals, correlation_threshold, correlation_window, min_channels) {
    var signalPeaks = {};

    for (var signalName in processedSignals) {
        var signal = processedSignals[signalName];
        var peaks = signal.peaks;

        signalPeaks[signalName] = peaks.map(function(peak) {
            return peak.index;
        });
    }

    var groups = [];
    var signalsList = Object.keys(signalPeaks);
    var numSignals = signalsList.length;

    for (var i = 0; i < numSignals; i++) {
        var signalA = signalsList[i];
        var peaksA = signalPeaks[signalA];
        var signalDataA = processedSignals[signalA];

        for (var pa = 0; pa < peaksA.length; pa++) {
            var indexA = peaksA[pa];
            var group = {};
            group[signalA] = indexA;

            for (var j = i + 1; j < numSignals; j++) {
                var signalB = signalsList[j];
                var peaksB = signalPeaks[signalB];
                var signalDataB = processedSignals[signalB];

                for (var pb = 0; pb < peaksB.length; pb++) {
                    var indexB = peaksB[pb];

                    if (Math.abs(indexA - indexB) <= correlation_window) {
                        var corr = computeCrossCorrelation(signalDataA.smoothedValues, signalDataB.smoothedValues, indexA, indexB, correlation_window);

                        if (corr >= correlation_threshold) {
                            group[signalB] = indexB;
                        }
                    }
                }
            }

            if (Object.keys(group).length >= min_channels) {
                groups.push(group);
            }
        }
    }

    return groups;
}

// Linear interpolation function
function linearInterpolate(x, x0, y0, x1, y1) {
    return y0 + ((y1 - y0) * (x - x0)) / (x1 - x0);
}

// Resample function
function resampleData(times, values, resampleTimes) {
    var resampledValues = [];
    var index = 0;

    for (var i = 0; i < resampleTimes.length; i++) {
        var t = resampleTimes[i];

        // Find the interval [t0, t1] such that t0 <= t <= t1
        while (index < times.length - 1 && times[index + 1] < t) {
            index++;
        }

        if (times[index] == t) {
            resampledValues.push(values[index]);
        } else if (times[index] < t && times[index + 1] >= t) {
            var interpolatedValue = linearInterpolate(
                t,
                times[index],
                values[index],
                times[index + 1],
                values[index + 1]
            );
            resampledValues.push(interpolatedValue);
        } else {
            // Extrapolate if outside the known times
            resampledValues.push(values[index]);
        }
    }

    return resampledValues;
}

// Process data function
function processData(data, n_hours, smooth_window, prominence, correlation_threshold, correlation_window, min_channels, enable_filter, short_window, long_window) {
    // Find the maximum timestamp in the data
    var maxTimestamp = 0;
    var minTimestamp = Infinity;
    for (var signalName in data) {
        var signalData = data[signalName];
        for (var timestamp in signalData) {
            var time = parseInt(timestamp); // Timestamps are in milliseconds
            if (time > maxTimestamp) {
                maxTimestamp = time;
            }
            if (time < minTimestamp) {
                minTimestamp = time;
            }
        }
    }

    var latestTime = maxTimestamp;
    var earliestTime = latestTime - n_hours * 3600 * 1000;

    // Generate common time axis at 1-minute intervals
    var resampleInterval = 60 * 1000; // 1 minute in milliseconds
    var resampleTimes = [];
    for (var t = earliestTime; t <= latestTime; t += resampleInterval) {
        resampleTimes.push(t);
    }

    var processedSignals = {};

    for (var signalName in data) {
        var signalData = data[signalName];
        var times = [];
        var values = [];

        for (var timestamp in signalData) {
            var time = parseInt(timestamp); // Timestamps are in milliseconds
            var value = signalData[timestamp];

            if (time >= earliestTime && time <= latestTime) {
                times.push(time);
                values.push(value);
            }
        }

        // Sort times and values
        var combined = times.map(function(e, i) {
            return { time: e, value: values[i] };
        });
        combined.sort(function(a, b) {
            return a.time - b.time;
        });

        times = combined.map(function(e) { return e.time; });
        values = combined.map(function(e) { return e.value; });

        // Resample data at 1-minute intervals using linear interpolation
        var resampledValues = resampleData(times, values, resampleTimes);

        // Apply high-pass filter if enabled
        if (enable_filter) {
            var shortMA = centeredMovingAverage(resampledValues, Math.max(short_window, 1));
            var longMA = centeredMovingAverage(resampledValues, Math.max(long_window, 1));

            var filteredValues = [];
            for (var i = 0; i < resampledValues.length; i++) {
                if (longMA[i] !== 0) {
                    filteredValues.push(shortMA[i] / longMA[i]);
                } else {
                    filteredValues.push(0);
                }
            }
            resampledValues = filteredValues;
        }

        // Normalization
        var meanValue = mean(resampledValues);
        var stdValue = standardDeviation(resampledValues, meanValue);
        var normalizedValues = resampledValues.map(function(v) {
            return ((v - meanValue) / stdValue) + (-50);
        });

        // Apply centered moving average to normalized values
        var smooth_window_samples = Math.max(Math.floor(smooth_window), 1); // Ensure at least window size of 1
        var smoothedValues = centeredMovingAverage(normalizedValues, smooth_window_samples);

        // Find peaks in smoothed normalized values
        var peaks = findPeaks(smoothedValues, prominence);

        processedSignals[signalName] = {
            times: resampleTimes,
            values: smoothedValues, // Use smoothed values for plotting
            smoothedValues: smoothedValues,
            peaks: peaks
        };
    }

    var groups = groupPeaks(processedSignals, correlation_threshold, correlation_window, min_channels);

    return {
        signals: processedSignals,
        groups: groups
    };
}
