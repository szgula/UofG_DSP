## Assignment 2, Digital Signal processing: FIR filters

The task of this assignment is to filter an ECG with FIR filters and to detect the R peaks. In contrast the FFT assignment here we write filter code which can be used for realtime processing. This means that the FIR filter needs to be implemented with the help of delay lines and the impulse response is truncated.

### 1. ECG filtering

Download the ECG according to the last digit of your matric number.

1. Create a Python FIR filter class which implements an FIR filter which has a method of the form value dofilter(value) where both the value argument and return value are scalars and not vectors (!) so that it can be used in a realtime system. The constructor of the class takes the coefficients as its input:

     class FIR_filter:
     def __ init __ (self,_coefficients):

     #. your code here

     def dofilter(self,v):

     #. your code here

     return result


     Implement the FIR filter in an efficient way for example by using a ring buffer or by smart application of the Python slicing operations. Minimise the amount of data being      shifted and explain how / why you have done it. Put the lter class in a separate file for example r-lter.py so that it turns into a module which can be imported by the   main program.

2. Add a unit test to the module fir-filter.py from 1 which tests if the FIR filter works properly. For example the delay line and the proper multiplication of the coefficients.
The unit test should be called if one starts the module with python fir-filter.py.
Add the unit test by calling a function called unittest if run as a main program:

if __name__ == "__main__":

unittest()


We included a unit test function in the fir-filter.py module to ensure the proper functionality of the code.

#
 Unit test code explanation   
#

When it runs directly, the fir-filter.py module will execute the unit test function because its __name__ is a string with value __main__. 
However, when other program imports the fir-filter.py module, its __name__ is its module name ('fir-filter'); therefore, the filtering functions will be available,
but it will not execute the unit test function.


Download a short ECG from moodle according to the last digits of your matric number. Filter this ECG with the above FIR lter class by removing the 50Hz interference and the DC. Decide which cutoff frequencies are needed and provide explanations by referring to the spectra and/or fundamental frequencies. Calculate the FIR lter co-ecients numerically ( = using python's IFFT command). Simulate realtime processing by feeding the ECG sample by sample into your FIR lter class. Make sure that the ECG looks intact and that it is not distorted (PQRST intact). Provide appropriate plots.


### 2 ECG heartrate detection

The task is to detect the momentary heart rate r(t) over a longer period of time. For example, after exercise you should see a slow decay of the heart rate to the baseline of perhaps 60 beats per minute. It is not the average heart rate but the frequency derived from the times between adjacent heartbeats.
1. Create a matched filter by using one QRST complex from an ECG and detect the R-peaks. Remember that for matched filters DC free
signals are important. Here, the pre-filtering of the ECGs can be done differently to the filtering above to reduce as much DC as possible and any interference.
