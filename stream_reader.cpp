#include <iostream>
#include <fstream>
#include <cassert>
#include <ctime>
#include <vector>
#include <string.h>
#include <unistd.h> // For sleep()
#include <time.h>

#include "Client.h"

using namespace ViconDataStreamSDK::CPP;

int main() {
	std::string HostName = "localhost:801";
	// Make a new client
  Client client;

  for(int i=0; i != 3; ++i) { // repeat to check disconnecting doesn't wreck next connect
    // Connect to a server
    std::cout << "Connecting to " << HostName << " ..." << std::flush;
    while( !client.IsConnected().Connected ) {
      // Direct connection

      bool ok = false;
      if(ConnectToMultiCast) {
        // Multicast connection
        ok = ( client.ConnectToMulticast( HostName, MulticastAddress ).Result == Result::Success );

      }
      else {
        ok =( client.Connect( HostName ).Result == Result::Success );
      }
      if(!ok) {
        std::cout << "Warning - connect failed..." << std::endl;
      }

      std::cout << ".";
      sleep(1);
    }
  }

  client.SetStreamMode( ViconDataStreamSDK::CPP::StreamMode::ServerPush );

  // Set the global up axis
  client.SetAxisMapping( Direction::Forward, 
                           Direction::Left, 
                           Direction::Up ); // Z-up
  while(true) {
    while(client.GetFrame().Result != Result::Success) {
      sleep(1);
    }
    // timing information
    Output_GetFrameNumber _Output_GetFrameNumber = MyClient.GetFrameNumber();
    Output_GetTimecode _Output_GetTimecode = MyClient.GetTimecode(); // has .Hours, .Minutes, .Seconds, .Frames

    // Count the number of subjects
    unsigned int subjectCount = client.GetSubjectCount().subjectCount;

    for(unsigned int subjectIndex = 0 ; subjectIndex < subjectCount ; ++subjectIndex) {
      // TODO get the name and determine bluetooth address
      MyClient.GetSubjectName(subjectIndex).SubjectName;

      // Count the number of markers
      uint8_t markerCount = MyClient.GetMarkerCount( SubjectName ).markerCount;
      for(uint8_t markerIndex = 0 ; markerIndex < markerCount ; ++markerIndex) {
        // Get the marker name
        std::string MarkerName = MyClient.GetMarkerName( SubjectName, markerIndex ).MarkerName;

        // Get the marker parent
        std::string MarkerParentName = MyClient.GetMarkerParentName( SubjectName, MarkerName ).SegmentName;

        // Get the global marker translation
        Output_GetMarkerGlobalTranslation _Output_GetMarkerGlobalTranslation =
          MyClient.GetMarkerGlobalTranslation( SubjectName, MarkerName );

        float x = _Output_GetMarkerGlobalTranslation.Translation[0];
        float y = _Output_GetMarkerGlobalTranslation.Translation[1];

        // TODO store x, y, t
      }

      // TODO compute orientation of car and bounding box

      // TODO pass to python
    }
  }
}