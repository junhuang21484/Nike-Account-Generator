# Nike Account Generator

Please note that this project is created for me to learn playwright in python,
and many features might not get implemented or heavily tested. This
project currently on create account but will not verify (phone #) for
you, however this features is looking to be added in the future.


I have another version written in selenium with all the todo list features
supported. I will implement those features into this project once i got time.
(Or I will just create a new one from scratch)


## Setting
Everything in the `setting.json` file right not can be edited and
configured to your own need.

#### Generator Section:
    "min_type_delay": minimum wait time when typing each character (ms),
    "max_type_delay": maximum wait time when typing each character (ms),
    "min_submit_delay": minimum wait time when clicking between buttons (ms),
    "max_submit_delay": maximum wait time whe nclick between buttons (ms)
#### Notification Section:
    To be worked on


## To Do List
* Add phone verification
  * PVA Codes
  * Get sms
* Add proxy support
* Catchall support 
* Notification support 
  * Discord webhook
* Better documentation
* ~~Finish up multi browser process~~