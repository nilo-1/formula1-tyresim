#include <iostream>
#include <vector>
#include <string>
#include <iomanip>
#include <cmath>
#include <sqlite3.h>
#include "time.h"

// --- PHYSICS RULESETS ---
double mediumRuleset(int lap, double base) {
    double linearDeg = 0.06 * lap;
    if (lap > 22) linearDeg += 0.4; 
    return base + linearDeg;
}

double hardRuleset(int lap, double base) {
    double linearDeg = 0.025 * lap;
    return (base + 0.8) + linearDeg;
}

// --- DATABASE BRIDGE ---
struct RaceRule {
    std::string compound;
    int stint_len;
    double base_time;
};

std::vector<RaceRule> rules;

// Standard SQLite callback to fill our vector
int callback(void* data, int argc, char** argv, char** azColName) {
    RaceRule r;
    r.compound = argv[0] ? argv[0] : "UNKNOWN";
    r.stint_len = argv[1] ? std::stoi(argv[1]) : 0;
    r.base_time = argv[2] ? std::stod(argv[2]) : 0.0;
    rules.push_back(r);
    return 0;
}

int main() {
    sqlite3* db;
    if (sqlite3_open("f1_sim.db", &db)) {
        std::cerr << "Can't open database: " << sqlite3_errmsg(db) << std::endl;
        return 1;
    }

    const char* query = "SELECT compound, stint_len, base_time FROM race_rules WHERE track = 'Abu Dhabi'";
    char* zErrMsg = 0;
    
    if (sqlite3_exec(db, query, callback, 0, &zErrMsg) != SQLITE_OK) {
        std::cerr << "SQL error: " << zErrMsg << std::endl;
        sqlite3_free(zErrMsg);
    }
    sqlite3_close(db);

    std::cout << "--- DAY 4: TYRE COMPOUND SANDBOX (Abu Dhabi 2024) ---" << std::endl;
    
    for (const auto& rule : rules) {
        std::cout << "\nStint: " << rule.compound << " | Base: ";
        timeFormat(rule.base_time); // Calling your function
        std::cout << "\n------------------------------------------" << std::endl;

        for (int i = 1; i <= rule.stint_len; ++i) {
            double rawTime = (rule.compound == "MEDIUM") ? mediumRuleset(i, rule.base_time) : hardRuleset(i, rule.base_time);
            
            std::cout << "Lap " << std::setw(2) << i << ": ";
            timeFormat(rawTime); // Calling your function again
            std::cout << std::endl;
        }
    }
    return 0;
}