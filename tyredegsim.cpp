#include <iostream>
#include "time.h"
#include <sqlite3.h>
using namespace std;
#include <cmath> 
#include <iomanip>

int Loopingcount(double track_temp) {
    double Laptime, firstLaptime, totalStintTime = 0;
    int totalLaps;
    double baseLaptime = 120.0; 

    // Base: Assuming 18 laps at 30°C. 
    // Sens: Lapses 1 lap of life for every 4 degrees extra.
    double lifeLimit = 18.0 - ((track_temp - 30.0) / 4.0);
    if (lifeLimit < 8) lifeLimit = 8; // Safety net to avoid crashing my pow function :(

    // 2. THE BRIEFING (Must be here to see it before input)
    cout << "\n--- TRACK DATA ---" << std::endl;
    cout << "Track Temp: " << track_temp << "C" << std::endl;
    cout << "Estimated Tyre Life: " << lifeLimit << " Laps" << std::endl;
    cout << "----------------------------" << std::endl;

    cout << "Enter laps for this stint: ";
    cin >> totalLaps;
    cout << "Enter base laptime (e.g., 120): ";
    cin >> baseLaptime;

for (int i = 1; i <= totalLaps; i++) {
    // 1. PHYSICS ENGINE
    // The "Cliff": Penalty stays tiny until i reaches lifeLimit, then explodes.
    double thermalCliff = std::pow((double)i / lifeLimit, 12);
    
    // The "Fuel Gain": Car gets 0.07s faster every lap as it gets lighter.
    double fuelGain = i * 0.07; 

    // The "Warm-up Penalty": Cold tires on Lap 1/2.
    double warmUpPenalty = 0.0;
    if (i == 1) {
        warmUpPenalty = 1.1; 
    } else if (i == 2) {
        warmUpPenalty = 0.2; 
    }

    // 2. THE CALCULATION (The Tug-of-War)
    Laptime = baseLaptime + warmUpPenalty - fuelGain + thermalCliff;

    // 3. TELEMETRY OUTPUT (Solves "Understanding the logic")
    if (i == 1) firstLaptime = Laptime;

    std::cout << "Lap " << setw(2) << i << ": ";
    timeFormat(Laptime);
    
    // Show the hidden math so you can see why the time changed
    cout << " [Fuel: -" << std::fixed << setprecision(2) << fuelGain 
              << "s | Cliff: +" << thermalCliff << "s]";

    // 3-SECOND WARNING SYSTEM 
    if (Laptime > (firstLaptime + 3.0)) { // Changed to 3.0 to match your comment
        std::cout << " [!!! PIT NOW !!!]";
    }
    
    std::cout << std::endl;
    totalStintTime += Laptime;
}
    return 0;
}

int main()
{
    sqlite3* db;
    sqlite3_stmt* stmt;
    double track_temp = 25.0; // Default fallback

    // 1. PULL DATA FROM THE BRIDGE FIRST
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

    // 2. RUN SIMULATION WITH THE LIVE DATA
    Loopingcount(track_temp);

    return 0;
}