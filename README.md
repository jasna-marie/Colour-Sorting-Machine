# Colour-Sorting-Machine
In this repository all necessary information for programming an automatic colour sorting machine can be found.
The prototype was created as part of the module "Industrielle Produktion und Industrie 4.0" at the Aachen University of Applied Sciences. 

The idea of programming a prototype of an automatic colour sorting machine developed from the problem that manual sorting is time-consuming, cost-intensive and error-prone. An automated sorting process should save time and costs and improve quality and hygiene.

The prototype was built using the following components: 
1 x TCS34725 colour sensor, 1 x HX711 24-bit analogue-to-digital converter, 4 x half-bridge load cells, 2 x servomotors, 2 x ESP8266

![circuit-diagramm](https://user-images.githubusercontent.com/107826888/174525890-bb2a7cb5-ae74-4883-9383-92389b0246ce.png)

The prototype shall fulfil the following functionality: The machine detects the colour of the objects via the TCS34725. The first servo motor moves to the correct position after detection. The second servo motor opens the barrier. The object then slides into the correct small load carrier. A scale with four half-bridge load cells which are connected to the HX711, is placed under a small load carrier. If an object is assigned to the small load carrier with the scale, the weight is recorded. A ThinkSpeak dashboard is used to visualise real-time data. After each measurement, the data is sent to ThinkSpeak.To analyse the quality of the colour sensor, the measured values are sent to Amazon Web Services and evaluated via a Jupyter notebook.
