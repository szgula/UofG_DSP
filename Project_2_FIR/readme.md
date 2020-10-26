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
