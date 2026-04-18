/*
Risk Analyzer System
--------------------

This program calculates:

1) Risk Level
2) Severity Level
3) Risk Score
4) Medical Recommendation
5) Case Classification

Used by:
medical_gui.py
*/

#include <iostream>
#include <string>

using namespace std;

class RiskAnalyzer
{

private:

    int symptomCount;

    double probability;

    int riskScore;

public:

    // Constructor

    RiskAnalyzer(
        int count,
        double prob
    )
    {
        symptomCount = count;

        probability = prob;

        riskScore = calculateScore();
    }

    // =========================
    // Calculate Risk Score
    // =========================

    int calculateScore()
    {

        int score = 0;

        score += symptomCount * 5;

        score += probability / 2;

        return score;
    }

    // =========================
    // Risk Level
    // =========================

    string calculateRiskLevel()
    {

        if (riskScore < 30)

            return "Low";

        else if (riskScore < 60)

            return "Medium";

        else

            return "High";
    }

    // =========================
    // Severity Level
    // =========================

    string calculateSeverity()
    {

        if (probability < 40)

            return "Mild";

        else if (probability < 70)

            return "Moderate";

        else

            return "Severe";
    }

    // =========================
    // Recommendation
    // =========================

    string getRecommendation()
    {

        string risk = calculateRiskLevel();

        if (risk == "Low")

            return "Home care";

        if (risk == "Medium")

            return "Visit doctor";

        return "Emergency";
    }

    // =========================
    // Case Classification
    // =========================

    string classifyCase()
    {

        if (riskScore >= 80)

            return "Critical";

        if (riskScore >= 50)

            return "Serious";

        return "Stable";
    }

    // =========================
    // Print Report
    // =========================

    void printReport()
    {

        cout

        << calculateRiskLevel()

        << "|"

        << calculateSeverity()

        << "|"

        << getRecommendation()

        << "|"

        << classifyCase()

        << "|"

        << riskScore;
    }
};

// =========================
// Main Function
// =========================

int main()
{

    int symptomCount;

    double probability;

    cin >> symptomCount;

    cin >> probability;

    RiskAnalyzer analyzer(

        symptomCount,

        probability

    );

    analyzer.printReport();

    return 0;
}