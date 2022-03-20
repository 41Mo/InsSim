#include <fstream>
#include <sstream>
#include <iostream>
#include <iomanip>
#include <vector>

#include "analysis_api.h"

std::vector<std::vector<std::string>> parse_csv(std::string fn) {
    std::string filename{fn};
    std::ifstream input{filename};

    std::vector<std::vector<std::string>> csvRows;

    if (!input.is_open()) {
      std::cerr << "Couldn't read file: " << filename << "\n";
      return csvRows;
    }


    for (std::string line; std::getline(input, line);) {
      std::istringstream ss(std::move(line));
      std::vector<std::string> row;
      if (!csvRows.empty()) {
         // We expect each row to be as big as the first row
        row.reserve(csvRows.front().size());
      }
      // std::getline can split on other characters, here we use ','
      for (std::string value; std::getline(ss, value, ';');) {
        row.push_back(std::move(value));
      }
      csvRows.push_back(std::move(row));
    }

    return csvRows;
}

void print_value(float v) {
    std::cout << std::setw(15) << v;
}
void test_print(vec_body acc, vec_body gyr) {
    print_value(acc.X);
    print_value(acc.Y);
    print_value(acc.Z);
    print_value(gyr.X);
    print_value(gyr.Y);
    print_value(gyr.Z);
    std::cout << "\n";
}

float precise_float(std::string s) {
    // dirty hack
    std::ostringstream out;
    out << std::setprecision(7) << std::stof(s);
    float percise = std::stof(out.str());
    return percise;
}

int main(int argc, char const *argv[])
{
    auto csv = parse_csv("../../csv_data/Sensors_and_orientation.csv");
    uint64_t size = csv.size();
    vec_body *acc = new vec_body[size];
    vec_body *gyr = new vec_body[size];

    // starting from 1 to skip header
    int header = 1;
    for (uint64_t i = header; i<size; i++) {
        auto row = csv.at(i);
        acc[i].X = precise_float(row.at(2));
        acc[i].Y = precise_float(row.at(3));
        acc[i].Z = precise_float(row.at(4));
        gyr[i].X = precise_float(row.at(5));
        gyr[i].Y = precise_float(row.at(6));
        gyr[i].Z = precise_float(row.at(7));
        //test_print(acc[i], gyr[i]);
    }
    SENSORS sens{acc, gyr, size};

    Analysis_api api{sens, 0, 0, 0 ,0 ,0, 1, size};
    api.loop();
    return 0;
}
