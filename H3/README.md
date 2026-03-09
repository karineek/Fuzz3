# Fuzzing H3 Uber System

## Installing the Project
Source code from https://github.com/uber/h3.

First, install the prerequisites:
```
sudo apt update
sudo apt install -y cmake make gcc libtool
```

To install it:
```
git clone https://github.com/uber/h3.git
cd h3/
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j"$(nproc)"
sudo make install
```

With the expected output:
```
...
Consolidate compiler generated dependencies of target benchmarkPolygonToCells
[ 99%] Built target benchmarkPolygonToCells
Consolidate compiler generated dependencies of target benchmarkPolygonToCellsExperimental
[100%] Built target benchmarkPolygonToCellsExperimental
Consolidate compiler generated dependencies of target benchmarkPolygon
[100%] Built target benchmarkPolygon
Install the project...
-- Install configuration: "Release"
-- Installing: /usr/local/bin/h3
-- Installing: /usr/local/bin/latLngToCell
-- Installing: /usr/local/bin/h3ToComponents
-- Installing: /usr/local/bin/cellToLatLng
-- Installing: /usr/local/bin/cellToLocalIj
-- Installing: /usr/local/bin/localIjToCell
-- Installing: /usr/local/bin/cellToBoundary
-- Installing: /usr/local/bin/gridDiskUnsafe
-- Installing: /usr/local/bin/gridDisk
-- Installing: /usr/local/bin/cellToBoundaryHier
-- Installing: /usr/local/bin/cellToLatLngHier
-- Installing: /usr/local/bin/h3ToHier
-- Installing: /usr/local/lib/libh3.a
-- Installing: /usr/local/include/h3/h3api.h
-- Installing: /usr/local/lib/cmake/h3/h3Config.cmake
-- Installing: /usr/local/lib/cmake/h3/h3ConfigVersion.cmake
-- Installing: /usr/local/lib/cmake/h3/h3Targets.cmake
-- Installing: /usr/local/lib/cmake/h3/h3Targets-release.cmake
```

## Executing the Code:
