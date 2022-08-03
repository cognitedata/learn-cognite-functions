# Cognite Functions Hands-On Exercise

For the hands-on exercise, we will be looking at developing a Cognite Function that evaluates the performance of a heat exchanger over time. A heat exchanger is a process unit that can be used to transfer heat from on medium to another. Think of the radiator in your house as a heat exchanger that can be used to heat your room by passing hot water through a series of pipes to warm the surrounding air. When a heat exchanger has been in operation for a while, its performance decreases for a variety of reasons - such as, fouling, scaling, corrosion etc. It’s important to monitor the heat transfer efficiency of the heat exchanger, in order to obtain the desired output.

The heat exchanger that we will be looking at is the discharge cooler in the Open Industrial Dataset. You can learn more about the data set here (https://openindustrialdata.com/) but essentially it represents the first of four stages for compression of natural gas on the Valhall PH platform. The discharge cooler is used to cool down the effluent of the compressed gas coming out of the compressor. We'll monitor the thermal resistance of a heat exchanger. This is important for the maintenance and cleaning of the HE. If the thermal resistance goes down, it’s not performing at the optimal level so we need to start cleaning and/or maintenance.

The hands-on exercise is divided into 5 parts. The first 3 parts are mandatory for the completion of the course while the last 2 are there for anyone who wants to dig deeper into advanced functionality.

1. Retrieving data from CDF with the SDK and calculating the thermal resistance of a heat exchanger. 
2. Implementing this calculation as a Cognite Function that runs on a schedule using the Python SDK. 
3. Implementing this calculation as a Cognite Function using only the Fusion UI. 
4. (Advanced) Learning how to use GitHub Actions to automatically deploy a Cognite Function in GitHub.
5. (Advanced) Forecasting the thermal resistance using a machine learning algorithm

Each part is performed in a separate notebook, we encourage you to go through the notebooks and run the code yourself. Happy coding!