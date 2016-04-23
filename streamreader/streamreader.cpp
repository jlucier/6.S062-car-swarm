#include <iostream>
#include <cassert>
#include <ctime>
#include <vector>
#include <string.h>
#include <unistd.h> // For sleep()
#include <time.h>

#include "Client.h"

using namespace std;
using namespace ViconDataStreamSDK::CPP;

static Client *client_ptr;

void streamreader_connect(const char* host) {

  // Make a new client
  client_ptr = new ViconDataStreamSDK::CPP::Client();

  for(int i=0; i != 3; ++i) { // repeat to check disconnecting doesn't wreck next connect
    // Connect to a server
    while(!client_ptr->IsConnected().Connected) {
      // Direct connection
      bool ok = (client_ptr->Connect(host).Result == Result::Success);

      if(!ok) {
        ; // connection failed, will try again
      }

      sleep(1);
    }
  }

  client_ptr->SetStreamMode(ViconDataStreamSDK::CPP::StreamMode::ServerPush);

  // Set the global up axis
  client_ptr->SetAxisMapping(ViconDataStreamSDK::CPP::Direction::Forward, 
                           ViconDataStreamSDK::CPP::Direction::Left, 
                           ViconDataStreamSDK::CPP::Direction::Up);
}

std::string streamreader_get_frame() {
  while(client_ptr->GetFrame().Result != Result::Success) {
    sleep(1);
  }
  // timing information
  Output_GetFrameNumber frame_number = client_ptr->GetFrameNumber();
  Output_GetTimecode frame_time = client_ptr->GetTimecode(); // has .Hours, .Minutes, .Seconds, .Frames

  std::string name;
  // Count the number of subjects
  unsigned int subjectCount = client_ptr->GetSubjectCount().SubjectCount;
  for(unsigned int subjectIndex = 0; subjectIndex < subjectCount; ++subjectIndex) {
    // TODO get the name and determine bluetooth address
    std::string subject_name = client_ptr->GetSubjectName(subjectIndex).SubjectName;
    name = subject_name;

    // Count the number of markers
    unsigned int markerCount = client_ptr->GetMarkerCount(subject_name).MarkerCount;
    for(unsigned int markerIndex = 0; markerIndex < markerCount; ++markerIndex) {
      // Get the marker name
      std::string marker_name = client_ptr->GetMarkerName(subject_name, markerIndex).MarkerName;

      // Get the marker parent
      std::string marker_parent_name = client_ptr->GetMarkerParentName(subject_name, marker_name).SegmentName;

      // Get the global marker translation
      Output_GetMarkerGlobalTranslation location = client_ptr->GetMarkerGlobalTranslation(subject_name, marker_name);

      float x = location.Translation[0];
      float y = location.Translation[1];

      // TODO store x, y, t
    }

    // TODO compute orientation of car and bounding box
  }

  // TODO return proper values
  return name;
}

#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
using namespace boost::python;

BOOST_PYTHON_MODULE(streamreader)
{
    def("connect", streamreader_connect);
    def("get_frame", streamreader_get_frame);
}
