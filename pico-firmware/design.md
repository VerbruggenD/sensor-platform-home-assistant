# Design doc: home assistent node firmware

## Types of sensors and actuators
- variable sensor can be floating point or integers (multiple)
- binary sensor can be true or false
- switch (home assistent), binary actuator on or off
- light (home assistent), can be on, off and a brightness

For the actuators they need set topics but als get topics.

## Dynamically adding sensors/actuators
The config is read in the config server. This sends the config as a json body to the device over mqtt.

## First implementation of the sensors
There is a sensor interface (base class) that defines the general interfaces of the object. This includes discovery topic, the initialisation of all measurements and also functions to publish the sensor values. In the higher class a specific sensor is implemented, deriving the base class. Here the specific interface of the sensor is done. E.g. for the DHT11, the library is used to initialize, measure and extract the values. this is then automatically published on the correct and unique state topic based on the name, mac address, ...

## First implementation of the actuators
First it is important to support basic actuators like a relay (switch in home assistant). This means it needs to support on and off states. This is published on the set topic. The actuator also needs to publish its state whenever the state changes. This is important if the switch is also controllable with a physical button.

So the actuator config is parsed and if the type is a switch, the switch object is created for that actuator. There is also the possibility to invert the logic in the config. 

The other type is the light. This also has the states on and off but also has a variable value for "brightness" in theory can this be used by almost anything. The value is updated seperately on a different topic. So this object needs a command topic and a brightness command topic and for both also a state topic. This makes the logic of the object very easy. 

## Switch actuator
- discovery topic (publish)
- state topic (publish)
- command topic (subscribe)

On the command topic the state needs to be updated to the state in the payload. The update_actuator function will change the actual actuator. Here the state change trigger is published.

## Light actuator  
- discovery topic (publish)
- state topic (publish)
- brightness state topic (publish)
- command topic (subscribe)
- brightness command topic (subscribe)