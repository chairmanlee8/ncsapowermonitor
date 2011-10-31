if [ ! -d "build" ]; then
    mkdir build
fi

rm -rf build/*
g++ -c source/powermon.cpp -lpthread -o build/powermon.o
ar rvs build/powermon.a build/powermon.o
g++ source/test_powermon.cpp build/powermon.a -lpthread -o build/test_powermon
chmod +x build/test_powermon
g++ source/monitor.cpp build/powermon.a -lpthread -o build/monitor
chmod +x build/monitor
g++ source/test_monitor.cpp -o build/test_monitor
chmod +x build/test_monitor
cp source/sample_conf.conf build/sample_conf.conf

mkdir build/powermon_server
cp source/host.py build/powermon_server/
cp source/display_server.py build/powermon_server/
cp source/configuration.py build/powermon_server/
cp source/device.py build/powermon_server/
cp source/timestamp.py build/powermon_server/
cp source/debug_print.py build/powermon_server/
cp -R source/static build/powermon_server/static
cp -R source/templates build/powermon_server/templates
cp source/powermon_server.sh build/powermon_server/
chmod +x build/powermon_server/powermon_server.sh
