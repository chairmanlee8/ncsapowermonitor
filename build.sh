if [ ! -d "build" ]; then
    mkdir build
fi

rm -rf build/*
g++ -c source/powermon.cpp -o build/powermon.o
ar rvs build/powermon.a build/powermon.o
g++ source/test_powermon.cpp build/powermon.a -o build/test_powermon
chmod +x build/test_powermon
g++ source/monitor.cpp build/powermon.a -o build/monitor
chmod +x build/monitor
g++ source/test_monitor.cpp -o build/test_monitor
chmod +x build/test_monitor
cp source/sample_conf.conf build/sample_conf.conf
