if [ ! -d "build" ]; then
    mkdir build
fi

rm -rf build/*
g++ -c source/powermon.cpp -o build/powermon.o
ar rvs build/powermon.a build/powermon.o
