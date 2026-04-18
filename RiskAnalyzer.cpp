/*
 * RiskAnalyzer.cpp
 * ================
 * Risk analysis engine called by medical_gui.py via subprocess.
 *
 * Input  (stdin): symptom_count  probability
 * Output (stdout): risk|severity|recommendation|case_type|score
 * Errors (stderr): human-readable message (non-zero exit code)
 *
 * Improvements over original:
 *   - Input validation with meaningful error messages to stderr
 *   - Boundary clamping for edge-case inputs
 *   - Consistent pipe-delimited output format
 *   - Non-zero exit code on error (detected by Python caller)
 *   - Comments throughout
 */

#include <iostream>
#include <string>
#include <sstream>
#include <cmath>

class RiskAnalyzer
{
private:
    int    symptomCount;
    double probability;
    int    riskScore;

public:
    // ── Constructor ───────────────────────────────────────────────────────────
    RiskAnalyzer(int count, double prob)
        : symptomCount(count),
          probability(std::max(0.0, std::min(100.0, prob))),   // clamp 0-100
          riskScore(0)
    {
        if (symptomCount < 0) symptomCount = 0;
        riskScore = calculateScore();
    }

    // ── Score = weighted sum of symptom count and probability ─────────────────
    int calculateScore() const
    {
        int score = (symptomCount * 5) + static_cast<int>(probability / 2.0);
        return std::min(score, 100);   // cap at 100
    }

    // ── Risk level based on score ─────────────────────────────────────────────
    std::string calculateRiskLevel() const
    {
        if (riskScore < 30) return "Low";
        if (riskScore < 60) return "Medium";
        return "High";
    }

    // ── Severity based on probability ─────────────────────────────────────────
    std::string calculateSeverity() const
    {
        if (probability < 40.0) return "Mild";
        if (probability < 70.0) return "Moderate";
        return "Severe";
    }

    // ── Recommendation based on risk level ────────────────────────────────────
    std::string getRecommendation() const
    {
        const std::string level = calculateRiskLevel();
        if (level == "Low")    return "Home care and rest recommended";
        if (level == "Medium") return "Schedule a doctor visit soon";
        return "Seek emergency medical attention immediately";
    }

    // ── Case classification ───────────────────────────────────────────────────
    std::string classifyCase() const
    {
        if (riskScore >= 80) return "Critical";
        if (riskScore >= 50) return "Serious";
        return "Stable";
    }

    // ── Print pipe-delimited result to stdout ─────────────────────────────────
    void printReport() const
    {
        std::cout
            << calculateRiskLevel()    << "|"
            << calculateSeverity()     << "|"
            << getRecommendation()     << "|"
            << classifyCase()          << "|"
            << riskScore;
        // No trailing newline — Python strips stdout anyway
    }
};


// ── Entry point ───────────────────────────────────────────────────────────────
int main()
{
    int    symptomCount = 0;
    double probability  = 0.0;

    // Read two values from stdin (sent by Python subprocess)
    if (!(std::cin >> symptomCount >> probability))
    {
        std::cerr << "ERROR: Could not read symptomCount and probability from stdin." << std::endl;
        return 1;   // non-zero → Python raises RuntimeError
    }

    if (symptomCount < 0 || probability < 0.0 || probability > 100.0)
    {
        std::cerr << "ERROR: Invalid input values."
                  << " symptomCount=" << symptomCount
                  << " probability="  << probability << std::endl;
        return 1;
    }

    RiskAnalyzer analyzer(symptomCount, probability);
    analyzer.printReport();

    return 0;   // success
}
