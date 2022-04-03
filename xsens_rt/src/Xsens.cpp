#include "xsensdeviceapi.h"
#include "Xsens.h"

#include <iostream>
#include <list>

using namespace std;
Xsens::Xsens(uint16_t frequency, bool logdata):
logdata(logdata),
frequency(frequency)
{
}

Xsens::~Xsens()
{
	deinit();
}

int Xsens::handleError(string errorString)
{
	control->destruct();
	cout << errorString << endl;
	cout << "Press [ENTER] to continue." << endl;
	return -1;
};

int Xsens::init()
{
	XsVersion version;

	cout << "Creating XsControl object..." << endl;
	control = XsControl::construct();
	assert(control != nullptr);

	xdaVersion(&version);
	cout << "Using XDA version: " << version.toString().toStdString() << endl;

	if (!scanned) {
		if (scanDevice() !=0) return -1;
	}
		if (openPort() != 0) return -1;

	// Get the device object
	device = control->device(mtPort.deviceId());
	assert(device != nullptr);
	cout << "Device: " << device->productCode().toStdString() << ", with ID: " << device->deviceId().toString() << " opened." << endl;

	if (configureDevice() != 0) return -1;

	// Create and attach callback handler to device
	device->addCallbackHandler(&callback);

	cout << "Putting device into measurement mode..." << endl;
	if (!device->gotoMeasurement())
		return handleError("Could not put device into measurement mode. Aborting.");


    return 0;
}

int Xsens::configureDevice() {
	// Put the device into configuration mode before configuring the device
	cout << "Putting device into configuration mode..." << endl;
	if (!device->gotoConfig())
		return handleError("Could not put device into configuration mode. Aborting.");

	cout << "Configuring the device..." << endl;
	XsOutputConfigurationArray configArray;
	//configArray.push_back(XsOutputConfiguration(XDI_PacketCounter, 0));
	//configArray.push_back(XsOutputConfiguration(XDI_SampleTimeFine, 0));

	if (device->deviceId().isImu() || device->deviceId().isVru() || device->deviceId().isAhrs() || device->deviceId().isGnss())
	{
		configArray.push_back(XsOutputConfiguration(XDI_Acceleration, frequency));
		configArray.push_back(XsOutputConfiguration(XDI_RateOfTurn, frequency));
		configArray.push_back(XsOutputConfiguration(XDI_MagneticField, frequency));
	}
	else
	{
		return handleError("Unknown device while configuring. Aborting.");
	}

	if (!device->setOutputConfiguration(configArray))
		return handleError("Could not configure MTi device. Aborting.");

	return 0;
}

int Xsens::openPort() {

	cout << "Opening port..." << endl;
	if (!control->openPort(mtPort.portName().toStdString(), mtPort.baudrate()))
		return handleError("Could not open port. Aborting.");

	return 0;
}

int Xsens::scanDevice() {
	cout << "Scanning for devices..." << endl;
	XsPortInfoArray portInfoArray = XsScanner::scanPorts();

	// Find an MTi device
	for (auto const &portInfo : portInfoArray)
	{
		if (portInfo.deviceId().isMti() || portInfo.deviceId().isMtig())
		{
			mtPort = portInfo;
			break;
		}
	}

	if (mtPort.empty())
		return handleError("No MTi device found. Aborting.");

	cout << "Found a device with ID: " << mtPort.deviceId().toString().toStdString() << " @ port: " << mtPort.portName().toStdString() << ", baudrate: " << mtPort.baudrate() << endl;
	scanned = true;
	return 0;
}

int Xsens::log() {
	cout << "Creating a log file..." << endl;
	string logFileName = "logfile.mtb";
	if (device->createLogFile(logFileName) != XRV_OK)
		return handleError("Failed to create a log file. Aborting.");
	else
		cout << "Created a log file: " << logFileName.c_str() << endl;
	cout << "Starting recording..." << endl;
	if (!device->startRecording())
		return handleError("Failed to start recording. Aborting.");

	return 0;
}

int Xsens::deinit() {
	if (logdata) {
		cout << "Stopping recording..." << endl;
		if (!device->stopRecording())
			return handleError("Failed to stop recording. Aborting.");

		cout << "Closing log file..." << endl;
		if (!device->closeLogFile())
			return handleError("Failed to close log file. Aborting.");
	}

	cout << "Closing port..." << endl;
	control->closePort(mtPort.portName().toStdString());

	cout << "Freeing XsControl object..." << endl;
	control->destruct();

	cout << "Successful exit." << endl;

	cout << "Press [ENTER] to continue." << endl;
	cin.get();
	return 0;
}

bool Xsens::data_availible() {
	return callback.packetAvailable();
}

bool Xsens::recieve(SensData *d) {
	// Retrieve a packet
	XsDataPacket packet = callback.getNextPacket();

	if (packet.containsCalibratedData())
	{
		XsVector acc = packet.calibratedAcceleration();
		d->acc.X = acc[0];
		d->acc.Y = acc[1];
		d->acc.Z = acc[2];

		XsVector gyr = packet.calibratedGyroscopeData();
		d->gyr.X = gyr[0];
		d->gyr.Y = gyr[1];
		d->gyr.Z = gyr[2];

		XsVector mag = packet.calibratedMagneticField();
		d->mag.X = mag[0];
		d->mag.Y = mag[1];
		d->mag.Z = mag[2];
		return true;
	} else {
		return false;
	}
}