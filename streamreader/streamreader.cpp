#include <string>
#include <map>
#include <math.h>
#include <unistd.h> // For sleep()

#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python/dict.hpp>
#include <boost/python/tuple.hpp>
#include "boost/tuple/tuple.hpp"

#include "Client.h"

#define FRONT "front"
#define BACK "back"

using namespace std;
using namespace ViconDataStreamSDK::CPP;
using namespace boost::python;

static Client *client_ptr;

bool streamreader_connect(const char* host) {

  // Make a new client
  client_ptr = new Client();

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

  if (!client_ptr->IsConnected().Connected) {
    return false;
  }

  client_ptr->SetStreamMode(StreamMode::ServerPush);
  client_ptr->EnableMarkerData();
  client_ptr->SetAxisMapping(Direction::Forward, 
                           Direction::Left, 
                           Direction::Up);
  return true;
}

dict streamreader_get_frame() {
  // "car_name" => (x,y,theta,t)
  // t = frame_number
  dict cars;

  while(client_ptr->GetFrame().Result != Result::Success) {
    sleep(1);
  }
  // timing information
  unsigned int frame_number = client_ptr->GetFrameNumber().FrameNumber;
  // Output_GetTimecode frame_time = client_ptr->GetTimecode(); // has .Hours, .Minutes, .Seconds, .Frames

  // Count the number of subjects
  unsigned int car_count = client_ptr->GetSubjectCount().SubjectCount;
  for(unsigned int car_index = 0; car_index < car_count; ++car_index) {
    string car_name = client_ptr->GetSubjectName(car_index).SubjectName;

    // Count the number of markers
    unsigned int marker_count = client_ptr->GetMarkerCount(car_name).MarkerCount;
    map<string, boost::tuples::tuple<float, float> > car_markers;
    for(unsigned int marker_index = 0; marker_index < marker_count; ++marker_index) {
      // Get the marker name
      string marker_name = client_ptr->GetMarkerName(car_name, marker_index).MarkerName;

      // Get the global marker translation
      Output_GetMarkerGlobalTranslation location = client_ptr->GetMarkerGlobalTranslation(car_name, marker_name);

      car_markers[marker_name] = boost::make_tuple(location.Translation[0], location.Translation[1]);
    }

    boost::tuples::tuple<float,float> front = car_markers[FRONT];
    boost::tuples::tuple<float,float> back = car_markers[BACK];
    float v_x = boost::get<0>(front) - boost::get<0>(back);
    float v_y = boost::get<1>(front) - boost::get<1>(back);
    float theta = atan(v_y/v_x);
    cars[car_name] = make_tuple(boost::get<0>(back), boost::get<1>(back), theta, frame_number);
  }

  return cars;
}

BOOST_PYTHON_MODULE(streamreader)
{
    def("connect", streamreader_connect);
    def("get_frame", streamreader_get_frame);
}
