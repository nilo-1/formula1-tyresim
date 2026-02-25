#include <iostream>
#include "time.h"
#include <sqlite3.h>
#include <cmath> 
#include <iomanip>
#include <string> // Added for to_string

using namespace std;

int Loopingcount(double track_temp) {
    double Laptime, firstLaptime, totalStintTime = 0;
    int totalLaps;
    double baseLaptime = 120.0; 

    // --- DB SETUP: OPEN BRIDGE ---
    sqlite3* db;
    char* errMsg = 0;
    sqlite3_open("f1_sim.db", &db);
    // Create the table for the dashboard and wipe old data
    sqlite3_exec(db, "CREATE TABLE IF NOT EXISTS simulation_results (lap INTEGER, lap_time REAL);", 0, 0, &errMsg);
    sqlite3_exec(db, "DELETE FROM simulation_results;", 0, 0, &errMsg);

    double lifeLimit = 18.0 - ((track_temp - 30.0) / 4.0);
    if (lifeLimit < 8) lifeLimit = 8; 

    cout << "\n--- TRACK DATA ---" << endl;
    cout << "Track Temp: " << track_temp << "C" << endl;
    cout << "Estimated Tyre Life: " << lifeLimit << " Laps" << endl;
    cout << "----------------------------" << endl;

    cout << "Enter laps for this stint: ";
    cin >> totalLaps;
    cout << "Enter base laptime (e.g., 120): ";
    cin >> baseLaptime;

    for (int i = 1; i <= totalLaps; i++) {
        // --- YOUR PHYSICS (UNTOUCHED) ---
        double thermalCliff = std::pow((double)i / lifeLimit, 12);
        double fuelGain = i * 0.035; 
        double warmUpPenalty = 0.0;
        if (i == 1) warmUpPenalty = 1.1; 
        else if (i == 2) warmUpPenalty = 0.2; 

        Laptime = baseLaptime + warmUpPenalty - fuelGain + thermalCliff;

        if (i == 1) firstLaptime = Laptime;

        // --- SAVE TO DATABASE FOR DASHBOARD ---
        string sql = "INSERT INTO simulation_results (lap, lap_time) VALUES (" + 
                     to_string(i) + ", " + to_string(Laptime) + ");";
        sqlite3_exec(db, sql.c_str(), 0, 0, &errMsg);

        // --- TELEMETRY OUTPUT ---
        cout << "Lap " << setw(2) << i << ": ";
        timeFormat(Laptime);
        cout << " [Fuel: -" << fixed << setprecision(2) << fuelGain 
             << "s | Cliff: +" << thermalCliff << "s]";

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
    double track_temp = 25.0; 

    if (sqlite3_open("f1_sim.db", &db) == SQLITE_OK) {
        const char* query = "SELECT track_temp FROM race_weather ORDER BY id DESC LIMIT 1;";
        
        if (sqlite3_prepare_v2(db, query, -1, &stmt, NULL) == SQLITE_OK) {
            if (sqlite3_step(stmt) == SQLITE_ROW) {
                track_temp = sqlite3_column_double(stmt, 0);
            }
        }
        sqlite3_finalize(stmt);
        sqlite3_close(db);
    }

    Loopingcount(track_temp);

    return 0;
}