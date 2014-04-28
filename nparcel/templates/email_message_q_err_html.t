<p>OK, this is serious!</p>
<p>The Toll Outlet Portal middleware Comms facility currently has ${count} messages in the queue at ${date}.  Is this what you are expecting?  Just to make sure, I have disabled <b>topcommsd</b>.</p>
<p>You are receiving this messages because the configuration has been set to send an error email if the threshold of ${error_threshold} has been breached <i><b>(and because the Toll Outlet Portal comms facility has now been turned off)</b></i>.</p>
<p>The threshold can be altered by setting the <b>comms_queue_error</b> option under the <b>comms</b> section within the <b>top.conf</b> file.</p>
<p>Oh, once you find out what's going on don't forget to start the <b>topcommsd</b> process again.</p>
