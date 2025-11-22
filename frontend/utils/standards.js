
// IS 456:2000 Table 5 - Minimum Cement Content, Maximum Water-Cement Ratio and Minimum Grade of Concrete
// for Different Exposures with Normal Weight Aggregates of 20 mm Nominal Maximum Size

export const CONCRETE_EXPOSURE_LIMITS = {
    'Mild': {
        minCementContent: 300,
        maxWaterCementRatio: 0.55,
        minGrade: 20,
        description: 'Concrete surfaces protected against weather or aggressive conditions, except those situated in coastal area.'
    },
    'Moderate': {
        minCementContent: 300,
        maxWaterCementRatio: 0.50,
        minGrade: 25,
        description: 'Concrete surfaces sheltered from severe rain or freezing whilst wet; concrete exposed to condensation and rain; concrete continuously under water; concrete in contact or buried under non-aggressive soil/ground water; concrete surfaces sheltered from saturated salt air in coastal area.'
    },
    'Severe': {
        minCementContent: 320,
        maxWaterCementRatio: 0.45,
        minGrade: 30,
        description: 'Concrete surfaces exposed to severe rain, alternate wetting and drying or occasional freezing whilst wet or severe condensation; concrete completely immersed in sea water; concrete exposed to coastal environment.'
    },
    'Very Severe': {
        minCementContent: 340,
        maxWaterCementRatio: 0.45,
        minGrade: 35,
        description: 'Concrete surfaces exposed to sea water spray, corrosive fumes or severe freezing conditions whilst wet.'
    },
    'Extreme': {
        minCementContent: 360,
        maxWaterCementRatio: 0.40,
        minGrade: 40,
        description: 'Surface of members in tidal zone; members in direct contact with liquid/solid aggressive chemicals.'
    }
};

// IS 456:2000 Clause 15.2.2 - Frequency of Sampling
export const getRequiredSamples = (quantity) => {
    if (quantity <= 5) return 1;
    if (quantity <= 15) return 2;
    if (quantity <= 30) return 3;
    if (quantity <= 50) return 4;

    // 4 plus one additional sample for each additional 50 m3 or part thereof
    const additionalQuantity = quantity - 50;
    const additionalSamples = Math.ceil(additionalQuantity / 50);
    return 4 + additionalSamples;
};

export const getGradeValue = (gradeString) => {
    // Extracts the number from strings like "M25", "M 25", "M-25"
    const match = gradeString?.match(/M\s*-?\s*(\d+)/i);
    return match ? parseInt(match[1], 10) : 0;
};
