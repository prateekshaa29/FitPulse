/**
 * Interactive BMI Calculator logic
 */

document.addEventListener('DOMContentLoaded', () => {
    const heightInput = document.getElementById('bmiHeightInput');
    const heightSlider = document.getElementById('bmiHeightSlider');
    const weightInput = document.getElementById('bmiWeightInput');
    const weightSlider = document.getElementById('bmiWeightSlider');

    const bmiValueEl = document.getElementById('bmiDisplayValue');
    const bmiCategoryEl = document.getElementById('bmiDisplayCategory');
    const bmiAdviceEl = document.getElementById('bmiDisplayAdvice');
    const bmiIndicatorEl = document.getElementById('bmiIndicator');
    const minHealthyEl = document.getElementById('minHealthyWeight');
    const maxHealthyEl = document.getElementById('maxHealthyWeight');

    if (!heightInput || !weightInput) return;

    function calculateBMI(heightCm, weightKg) {
        if (heightCm <= 0 || weightKg <= 0) return null;
        const heightM = heightCm / 100.0;
        const bmi = (weightKg / (heightM * heightM));
        
        let category = 'Normal weight';
        let colorClass = 'bg-success';
        let advice = 'You are within a healthy weight range. Keep maintaining your active fitness routines!';
        
        if (bmi < 18.5) {
            category = 'Underweight';
            colorClass = 'bg-info text-dark';
            advice = 'Your BMI indicates you are underweight. Consider speaking with our nutritionist to build a healthy calorie-dense meal plan.';
        } else if (bmi >= 18.5 && bmi < 25.0) {
            category = 'Normal weight';
            colorClass = 'bg-success';
            advice = 'Excellent work! Your BMI is in the ideal healthy zone. Maintain your balanced diet and workout frequency.';
        } else if (bmi >= 25.0 && bmi < 30.0) {
            category = 'Overweight';
            colorClass = 'bg-warning text-dark';
            advice = 'Your BMI is in the overweight range. Regular cardio sessions and balanced calorie tracking can help you reach a healthy baseline.';
        } else {
            category = 'Obesity';
            colorClass = 'bg-danger';
            advice = 'Your BMI falls into the obesity category. A structured fitness routine and nutritional consultation are strongly recommended.';
        }

        const minHealthy = (18.5 * heightM * heightM).toFixed(1);
        const maxHealthy = (24.9 * heightM * heightM).toFixed(1);

        // Map BMI (15 to 40) to percentage (0% to 100%) for gauge indicator
        let percentage = ((bmi - 15) / (40 - 15)) * 100;
        if (percentage < 0) percentage = 0;
        if (percentage > 100) percentage = 100;

        return {
            bmi: bmi.toFixed(1),
            category: category,
            colorClass: colorClass,
            advice: advice,
            percentage: percentage,
            minHealthy: minHealthy,
            maxHealthy: maxHealthy
        };
    }

    function updateUI() {
        const h = parseFloat(heightInput.value) || 0;
        const w = parseFloat(weightInput.value) || 0;

        const res = calculateBMI(h, w);
        if (!res) return;

        if (bmiValueEl) bmiValueEl.textContent = res.bmi;
        if (bmiCategoryEl) {
            bmiCategoryEl.textContent = res.category;
            bmiCategoryEl.className = `badge ${res.colorClass} fs-6 px-3 py-2`;
        }
        if (bmiAdviceEl) bmiAdviceEl.textContent = res.advice;
        if (bmiIndicatorEl) bmiIndicatorEl.style.left = `${res.percentage}%`;
        if (minHealthyEl) minHealthyEl.textContent = `${res.minHealthy} kg`;
        if (maxHealthyEl) maxHealthyEl.textContent = `${res.maxHealthy} kg`;
    }

    // Input-Slider two-way bindings
    heightInput.addEventListener('input', () => {
        if (heightSlider) heightSlider.value = heightInput.value;
        updateUI();
    });

    if (heightSlider) {
        heightSlider.addEventListener('input', () => {
            heightInput.value = heightSlider.value;
            updateUI();
        });
    }

    weightInput.addEventListener('input', () => {
        if (weightSlider) weightSlider.value = weightInput.value;
        updateUI();
    });

    if (weightSlider) {
        weightSlider.addEventListener('input', () => {
            weightInput.value = weightSlider.value;
            updateUI();
        });
    }

    // Initial run
    updateUI();
});
