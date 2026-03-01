#include <iostream>
#include <sqlite3.h>
#include <cmath> 
#include <iomanip>
#include <string>

using namespace std;

void timeFormat(double totalSeconds) {
    int minutes = static_cast<int>(totalSeconds) / 60;
    double seconds = totalSeconds - (minutes * 60);
    cout << minutes << ":" << (seconds < 10 ? "0" : "") << fixed << setprecision(3) << seconds;
}

int Loopingcount(double track_temp, double baseLaptime, double lifeLimit) {
    sqlite3* db;
    char* errMsg = 0;
    sqlite3_open("f1_sim.db", &db);
    
    sqlite3_exec(db, "CREATE TABLE IF NOT EXISTS simulation_results (lap INTEGER, lap_time REAL);", 0, 0, &errMsg);
    sqlite3_exec(db, "DELETE FROM simulation_results;", 0, 0, &errMsg);

    double surfaceWear = 0.032; 
    double fuelEffect = 0.038;  
    
    cout << "\n--- F1 STRATEGY SIMULATION: PHYSICS 3.5 ---" << endl;

    for (int i = 1; i <= (int)lifeLimit; i++) {
        double thermalCliff = std::pow((double)i / (lifeLimit * 0.98), 4);
        double wearLinear = i * surfaceWear; 
        double fuelGain = i * fuelEffect; 
        
        // Calibration nudge for perfect overlap
        double Laptime = (baseLaptime + 0.6) - fuelGain + wearLinear + thermalCliff;

        string sql = "INSERT INTO simulation_results (lap, lap_time) VALUES (" + to_string(i) + ", " + to_string(Laptime) + ");";
        sqlite3_exec(db, sql.c_str(), 0, 0, &errMsg);

        cout << "Lap " << setfill('0') << setw(2) << i << ": ";
        timeFormat(Laptime);
        cout << endl;
    }

    sqlite3_close(db);
    return 0;
}

int main() {
    sqlite3* db;
    sqlite3_stmt* stmt;
    double track_temp = 25.0, base_time = 90.0, stint_len = 20.0;

    if (sqlite3_open("f1_sim.db", &db) == SQLITE_OK) {
        sqlite3_prepare_v2(db, "SELECT track_temp FROM race_weather LIMIT 1;", -1, &stmt, NULL);
        if (sqlite3_step(stmt) == SQLITE_ROW) track_temp = sqlite3_column_double(stmt, 0);
        sqlite3_finalize(stmt);

        sqlite3_prepare_v2(db, "SELECT base_time, stint_len FROM race_rules LIMIT 1;", -1, &stmt, NULL);
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            base_time = sqlite3_column_double(stmt, 0);
            stint_len = sqlite3_column_double(stmt, 1);
        }
        sqlite3_finalize(stmt);
        sqlite3_close(db);
    }
    Loopingcount(track_temp, base_time, stint_len);
    return 0;
}