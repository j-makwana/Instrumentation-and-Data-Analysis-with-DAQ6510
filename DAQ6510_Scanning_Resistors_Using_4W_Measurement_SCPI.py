"""***********************************************************
*** Copyright Tektronix, Inc.                           ***
*** See www.tek.com/sample-license for licensing terms. ***
***********************************************************"""
import socket
import struct
import math
import time
import datetime
import pandas as pd
from collections import defaultdict

echo_cmd = 1


"""*********************************************************************************
	Function: instrument_connect(my_socket, ip_address string, my_port int) 
	
	Purpose: Open an instance of an instrument object for remote communication
		 over LAN/Ethernet.

	Parameters:
                my_socket - Instance of a socket object.
                
		ip_address (string) - The TCP/IP address string associated with the
                                      target instrument. 
		my_port (int) - The instrument connection port. 

	Returns:
		my_socket - Updated instance of a socket object that includes
                            attributes of a valid connection. 

	Revisions:
		2019-07-30    JJB    Initial revision.
*********************************************************************************"""
def instrument_connect(my_socket, my_address, my_port, timeout, do_reset, do_id_query):
    my_socket.connect((my_address, my_port)) # input to connect must be a tuple
    my_socket.settimeout(timeout)
    if do_reset == 1:
        instrument_write(my_socket, "*RST")
    if do_id_query == 1:
        tmp_id = instrument_query(my_socket, "*IDN?", 100)
        print(tmp_id)
    return my_socket


"""*********************************************************************************
	Function: instrument_disconnect(my_socket)
	
	Purpose: Break the LAN/Ethernet connection between the controlling computer
			 and the target instrument.

	Parameters:
		my_socket - The TCP instrument connection object used for sending
							  and receiving data.

	Returns:
		None

	Revisions:
		2019-07-30    JJB    Initial revision.
*********************************************************************************"""
def instrument_disconnect(my_socket):
    my_socket.close()
    return


"""*********************************************************************************
	Function: instrument_write(my_socket, my_command)
	
	Purpose: This function issues control commands to the target instrument.

	Parameters:
		my_socket - The TCP instrument connection object used for sending
			    and receiving data.
		my_command (string) - The command issued to the instrument to make it 
				      perform some action or service. 
	Returns:
		None

	Revisions:
		2019-07-30    JJB    Initial revision.
*********************************************************************************"""
def instrument_write(my_socket, my_command):
    if echo_cmd == 1:
        print(my_command)
    cmd = "{0}\n".format(my_command)
    my_socket.send(cmd.encode())
    return


"""*********************************************************************************
	Function: instrument_read(my_socket, receive_size)
	
	Purpose: This function asks the connected instrument to reply with some
                 previously requested information, typically queued up from a call
                 to instrument_write().

	Parameters:
		my_socket - The TCP instrument connection object used for sending
			    and receiving data.
		receive_size (int) - Size of the data/string to be returned to
                                     the caller. 

	Returns:
		reply_string (string) - The requested information returned from the 
					target instrument.

	Revisions:
		2019-07-30    JJB    Initial revision.
*********************************************************************************"""
def instrument_read(my_socket, receive_size):
    return my_socket.recv(receive_size).decode()


"""*********************************************************************************
	Function: instrument_query(my_socket, my_command, receive_size)
	
	Purpose: This function issues control commands to the target instrument with
                 the expectation that data will be returned. For this function
                 instance, the returned data is (typically) in string format. 

	Parameters:
		my_socket - The TCP instrument connection object used for sending
			    and receiving data.
		my_command (string) - The command issued to the instrument to make it 
				      perform some action or service.
		receive_size (int) - The approximate number of bytes of data the caller
                                     expects to be returned in the response from the
                                     instrument. 
	Returns:
		reply_string (string) - The requested information returned from the 
					target instrument. Obtained by way of a caller
					to instrument_read().

	Revisions:
		2019-07-30    JJB    Initial revision.
*********************************************************************************"""
def instrument_query(my_socket, my_command, receive_size):
    instrument_write(my_socket, my_command)
    time.sleep(0.1)
    return instrument_read(my_socket, receive_size)


"""*********************************************************************************
	This example application demonstrates how to use the DAQ6510 to accurately measure resistance
        across multiple devices. To obtain the best results, the 4-wire (Kelvin) measurement method and
        offset compensation are used for this test.

        Typical resistance measurements made using the 2-wire method source current through the test
        leads and the device under test (DUT). The voltage is measured, and the resistance is calculated.
        It is difficult to obtain accurate 2-wire resistance measurements when the DUT is lower than 100 Ω.
        Typical lead resistances lie in the range of 1 mΩ to 10 mΩ. When the 2-wire method is applied to lowresistance
        measurements, there is a small but significant voltage drop across the resistance of each
        test lead. The voltage measured by the instrument is not the same as the voltage directly across the
        DUT.

        The 4-wire method is preferred for low-resistance measurements. With this configuration, the test
        current is sourced through the DUT using one set of test leads, while a second set of SENSE leads
        measures the voltage across the DUT. The voltage-sensing leads are connected as close to the
        device under test as possible to avoid including the resistance of the test leads in the measurement.

        Thermoelectric voltages (EMFs) can seriously affect low-resistance measurement accuracy. The
        DAQ6510 can apply the offset-compensated ohms method (OCOMP), which makes one normal
        resistance measurement and one using the lowest current source setting to eliminate EMFs.

        For this example, you will use resistors of different low values across multiple channels of a 7700
        multiplexer module and examine how the 4-wire measurement method provides a more accurate
        reading than the 2-wire method. Fixed measurement ranges are applied in order to optimize scanning
        speed and OCOMP is applied to correct for any EMF effects.
*********************************************************************************"""
ip_address = "169.254.243.145"     # Place your instrument's IP address here.
my_port = 5025

s = socket.socket()                 # Establish a TCP/IP socket object
# Open the socket connection
instrument_connect(s, ip_address, my_port, 20000, 0, 1)

t1 = time.time()                    # Start the timer...

instrument_write(s, "*RST")                                     # Reset the DAQ6510
channel_count = 3
scan_count = 5
buffer_size = channel_count*scan_count

instrument_write(s, "ROUT:SCAN:COUN:SCAN {0}".format(scan_count))   # Set the number of times the scan is repeated
instrument_write(s, 'TRAC:POIN {}, "defbuffer1"'.format(buffer_size))                     # Set buffer size
instrument_write(s, 'SENS:FUNC "RES", (@101:103)')                    # specify the channels here for the 2W function
instrument_write(s, 'RES:RANG:AUTO ON, (@101:103)')                     # Set Auto Range on
instrument_write(s, 'SENS:RES:NPLC 0.1, (@101:103)')                     #Set NLPC value (the higher the better but more time taken then)
instrument_write(s, "ROUT:SCAN:CRE (@101:103)")                                     # specify which channels to scan 
instrument_write(s,"TRAC:CLE")                                      #clear the buffer
instrument_write(s, "INIT")                                         # Initiate the scan



start_index = 1
end_index = channel_count
accumulated_readings = 0
columns1= ['TimeStamp']+ ['Channel_{}'.format(i) for i in range(1,channel_count)]
df= pd.DataFrame(columns=columns1)
data_dict= defaultdict(list)

while accumulated_readings < buffer_size:
    time.sleep(0.5)
    readings_count = int(instrument_query(s, "TRACe:ACTual?", 16).rstrip())
    if readings_count >= end_index:
        tempbuf=instrument_query(s, "TRACe:DATA? {0}, {1}, \"defbuffer1\", READ".format(start_index, end_index), 128)
        now= datetime.datetime.now()
        now2 = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        final_data= tempbuf.strip().split(',')
        data_dict['TimeStamp']= now2[:-4]
        for i, value in enumerate(final_data,1):
            
        	data_dict[f"Channel_{i}"] = value
        
        df_dictionary= pd.DataFrame([data_dict])
        df= pd.concat([df, df_dictionary],ignore_index=True)


        start_index += channel_count
        end_index += channel_count
        accumulated_readings += channel_count

# Close the socket connection
instrument_disconnect(s)
t2 = time.time()


# Notify the user of completion and the data streaming rate achieved. 
print("done")
print("Total Time Elapsed: {0:.3f} s".format(t2-t1))
df.to_csv('Keithley_readings.csv')
print(df)

input("Press Enter to continue...")
exit()
