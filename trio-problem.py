from time import sleep
import time
import trio

from random import uniform

# Note on documentation: In our group we use Google style docstrings.

class Monochromator():
    """Class simulating simple monochromator interactions."""
    
    def __init__(self, room):
        self.room = room

    async def change_grating(self, grating_number):
        """ Changes the grating according to the grating number.
        
        In this case the grating number can be 1, 2, 3 or for example
        300, 1200, 1800.
        """
        await trio.sleep(2) # Ca. 20 seconds is the time it takes the device in the lab
        print(f"Changed the grating in {self.room} to: {grating_number}")

class CCD():
    """Class simulating simple CCD camera commands."""

    def __init__(self, room):
        self.room = room

    async def measure_spectrum(self, exposure_time):
        """Measure a spectrum for the period of the exposure time.
        
        Args:
            exposure_time (int): Exposure time in seconds.

        """
        await trio.sleep(exposure_time)
        print(f"Successfully measured spectrum. Saved at: {self.room}")

class Powermeter():
    """Class simulating simple powermeter interactions."""

    def __init__(self, room):
        self.room = room

    async def read_out(self):
        """Returns the current value.
        
        Returns:
            The current power in Watt.

        """
        await trio.sleep(0.1)
        print(f"{7.5 + uniform(0,1)} Watt")

async def measurement(object, rating_1, spectrum_1, rating_2, spectrum_2):
    mchr = Monochromator(object)
    ccd_camera = CCD(object)
    pwmeter = Powermeter(object)

    await mchr.change_grating(rating_1)
    await ccd_camera.measure_spectrum(spectrum_1)
    await mchr.change_grating(rating_2)
    await ccd_camera.measure_spectrum(spectrum_2)
    

 
# if __name__ == "__main__": 
    # # Initializing the devices
    # mchr = Monochromator("Alice")
    # ccd_camera = CCD("Alice")
    # pwmeter = Powermeter("Alice")

    # # Example measurement process
    # mchr.change_grating(300)
    # pwmeter.read_out()
    # ccd_camera.measure_spectrum(0.1)
    # pwmeter.read_out()
    # mchr.change_grating(1200)
    # pwmeter.read_out()
    # ccd_camera.measure_spectrum(1)
    # pwmeter.read_out()
    # mchr.change_grating(1800)
    # pwmeter.read_out()
    # ccd_camera.measure_spectrum(5)
    # pwmeter.read_out()

"""
A lot of our measurement tasks involve doing measurements using different
devices at the same time. Often these are also controlled by the same computer.
A lot of the interaction with these devices in Python, is giving them a command
and waiting for it's execution. However in a normal synchronous Python program
the program is blocked while waiting, similar to the Python time.sleep function.

Please take a look at the Python Trio module. You can find the tutorial here:
https://trio.readthedocs.io/en/stable/tutorial.html
You should not need to read the whole document to fulfill the following task,
only the beginning of the tutorial should be necessary. Feel free to read the
excellent tutorial in full, however I do not want to unduly take up your time
for this test.

Task:
Convert the synchronous functions in the example measurement process to an
asynchronous equivalent.

Then implement this sequence of measurements, 

mchr_alice = Monochromator("Alice")
mchr_bob = Monochromator("Bob")
ccd_camera_alice = CCD("Alice")
ccd_camera_bob = CCD("Bob")

mchr_alice.change_grating(300)
ccd_camera_alice.measure_spectrum(0.1)
mchr_alice.change_grating(1800)
ccd_camera_alice.measure_spectrum(5)

mchr_bob.change_grating(1200)
ccd_camera_bob.measure_spectrum(1)
mchr_bob.change_grating(1800)
ccd_camera_bob.measure_spectrum(5)

such that the measurements in Alice are done one after the other but at the same
time, i.e. concurrently, the measurements in Bob are done one after the other.
"""
async def main():
    start_time = time.time()
    print("Starting measurement")
    async with trio.open_nursery() as nursery:
        nursery.start_soon(measurement, "Alice", 300, 0.1, 1800, 5)
        nursery.start_soon(measurement, "Bob", 1200, 1, 1800, 5)
        
        print("Wait until measurement finished")

    print("Time execution: %s seconds" % (time.time() - start_time))
# trio.run(main)
"""
Food for thought:
You don't need to implement it, but please think about: How would you go about
implementing simultaneous powermeter read outs during the longer spectra
measurements with the CCD camera, say about every 0.1 seconds.
For example: 1 CCD camera take 5 second to measure a spectrum, during this time it can read out the powermeter every 0.1 seconds (50 times).
"""

async def powermeter_read_out():
    pwmeter = Powermeter("Alice")
    try:
        while True:
            await pwmeter.read_out()
    except trio.Cancelled:
        print("Powermeter read out canceled because of spectrum measurement finished.")

async def ccd_camera_measure_spectrum(exposure_time):
    ccd_camera = CCD("Alice")
    async with trio.open_nursery() as nursery:
        nursery.start_soon(powermeter_read_out)
        await ccd_camera.measure_spectrum(exposure_time)
        nursery.cancel_scope.cancel()

trio.run(ccd_camera_measure_spectrum, 1)