#include <iostream>
#include "time.h"
#include <sqlite3.h>
#include <cmath> 
#include <iomanip>
#include <string>

using namespace std;

// Updated signature: Now accepts automated base time and life limit from main
int Loopingcount(double track_temp, double baseLaptime, double lifeLimit) {
    double Laptime, firstLaptime, totalStintTime = 0;
    
    // --- DB SETUP: OPEN BRIDGE ---
    sqlite3* db;
    char* errMsg = 0;
    sqlite3_open("f1_sim.db", &db);
    
    // Create the table for the dashboard and wipe old data
    sqlite3_exec(db, "CREATE TABLE IF NOT EXISTS simulation_results (lap INTEGER, lap_time REAL);", 0, 0, &errMsg);
    sqlite3_exec(db, "DELETE FROM simulation_results;", 0, 0, &errMsg);

    // DISPLAY AUTOMATED TRACK DATA
    cout << "\n--- AUTOMATED DATA FETCHED ---" << endl;
    cout << "Track Temp:      " << track_temp << "C" << endl;
    cout << "Anchor Pace:     " << baseLaptime << "s" << endl;
    cout << "Expected Stint:  " << (int)lifeLimit << " Laps" << endl;
    cout << "----------------------------" << endl;

    // Run the loop for the duration of the real stint length
    // 1. ADD THIS CONSTANT ABOVE THE LOOP
double surfaceWear = 0.05; // Each lap adds 50ms of natural wear

for (int i = 1; i <= (int)lifeLimit; i++) {
    // --- PHYSICS 2.0 ---
    
    // We make the cliff start a bit earlier (0.9 multiplier) 
    // and use a lower power (10 instead of 12) for a smoother curve.
    double thermalCliff = std::pow((double)i / (lifeLimit * 0.9), 10);
    
    // This is the "Tilt" - the tires getting slower every lap
    double wearLinear = i * surfaceWear; 
    
    double fuelGain = i * 0.035; 
    double warmUpPenalty = 0.0;
    
    if (i == 1) warmUpPenalty = 1.1; 
    else if (i == 2) warmUpPenalty = 0.2; 

    // NEW FORMULA: Base + Warmup - Lightness + Natural Wear + Final Cliff
    Laptime = baseLaptime + warmUpPenalty - fuelGain + wearLinear + thermalCliff;

    if (i == 1) firstLaptime = Laptime;

    // --- SAVE TO DATABASE ---
    string sql = "INSERT INTO simulation_results (lap, lap_time) VALUES (" + 
                 to_string(i) + ", " + to_string(Laptime) + ");";
    sqlite3_exec(db, sql.c_str(), 0, 0, &errMsg);

    // --- TELEMETRY OUTPUT ---
    cout << "Lap " << setw(2) << i << ": ";
    timeFormat(Laptime);
    cout << " [Fuel: -" << fixed << setprecision(2) << fuelGain 
         << "s | Wear: +" << (wearLinear + thermalCliff) << "s]";

    if (Laptime > (firstLaptime + 1.0)) cout << " [!]";
    
    cout << endl;
    totalStintTime += Laptime;
}

    // --- DB CLEANUP ---
    sqlite3_close(db);
    return 0;
}

int main()
{
    sqlite3* db;
    sqlite3_stmt* stmt;
    
    // Fallback defaults
    double track_temp = 25.0; 
    double base_time = 90.0;
    double stint_len = 20.0;

    if (sqlite3_open("f1_sim.db", &db) == SQLITE_OK) {
        // 1. PULL TRACK TEMPERATURE
        const char* q1 = "SELECT track_temp FROM race_weather ORDER BY id DESC LIMIT 1;";
        if (sqlite3_prepare_v2(db, q1, -1, &stmt, NULL) == SQLITE_OK) {
            if (sqlite3_step(stmt) == SQLITE_ROW) {
                track_temp = sqlite3_column_double(stmt, 0);
            }
        }
        sqlite3_finalize(stmt);

        // 2. PULL AUTOMATED RULES (Base Time and Stint Length)
        // We look for Lando's specific data we saved in fetch_data.py
        const char* q2 = "SELECT base_time, stint_len FROM race_rules WHERE track = 'Abu Dhabi' LIMIT 1;";
        if (sqlite3_prepare_v2(db, q2, -1, &stmt, NULL) == SQLITE_OK) {
            if (sqlite3_step(stmt) == SQLITE_ROW) {
                base_time = sqlite3_column_double(stmt, 0);
                stint_len = sqlite3_column_double(stmt, 1);
            }
        }
        sqlite3_finalize(stmt);
        sqlite3_close(db);
    }

    // Pass all automated variables to the simulator
    Loopingcount(track_temp, base_time, stint_len);

    return 0;
}