<p>OK, this is serious!</p>
<p>The Nparcel B2C Comms facility currently has ${count} messages in the queue at ${date}.  Is this what you are expecting?  Just to make sure, I have disabled the Nparcel comms facility, <b>npcommsd</b>.</p>
<p>You are receiving this messages because the configuration has been set to send an error email if the threshold of ${error_threshold} has been breached <i><b>(and because the Nparcel comms facility has now been turned off)</b></i>.</p>
<p>The threshold can be altered by setting the <b>comms_queue_error</b> option under the <b>comms</b> section within the <b>nparcel.conf</b> file.</p>
<p>Oh, once you find out what's going on don't forget to start the <b>npcommsd</b> process again.</p>
