#ifndef callbackHandler_h__
#define callbackHandler_h__
#include "xsensdeviceapi.h"
#include "xscommon/xsens_mutex.h"
#include <list>

class CallbackHandler : public XsCallback
{
public:
	CallbackHandler(size_t maxBufferSize = 5)
		: m_maxNumberOfPacketsInBuffer(maxBufferSize)
		, m_numberOfPacketsInBuffer(0)
	{
	}

	virtual ~CallbackHandler() throw()
	{
	}

	bool packetAvailable() const;

	XsDataPacket getNextPacket();

protected:
virtual void onLiveDataAvailable(XsDevice*, const XsDataPacket* packet);

private:
	mutable xsens::Mutex m_mutex;
	size_t m_maxNumberOfPacketsInBuffer;
	size_t m_numberOfPacketsInBuffer;
	std::list<XsDataPacket> m_packetBuffer;

};

#endif