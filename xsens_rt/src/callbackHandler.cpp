#include "callbackHandler.h"
#include "xsensdeviceapi.h"

bool CallbackHandler::packetAvailable() const
{
	xsens::Lock locky(&m_mutex);
	return m_numberOfPacketsInBuffer > 0;
}

XsDataPacket CallbackHandler::getNextPacket()
{
	assert(packetAvailable());
	xsens::Lock locky(&m_mutex);
	XsDataPacket oldestPacket(m_packetBuffer.front());
	m_packetBuffer.pop_front();
	--m_numberOfPacketsInBuffer;
	return oldestPacket;
}


void CallbackHandler::onLiveDataAvailable(XsDevice*, const XsDataPacket* packet)
{
	xsens::Lock locky(&m_mutex);
	assert(packet != nullptr);
	while (m_numberOfPacketsInBuffer >= m_maxNumberOfPacketsInBuffer)
		(void)getNextPacket();

	m_packetBuffer.push_back(*packet);
	++m_numberOfPacketsInBuffer;
	assert(m_numberOfPacketsInBuffer <= m_maxNumberOfPacketsInBuffer);
}