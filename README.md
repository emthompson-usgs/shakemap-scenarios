shakemap-scenarios
==================

Overview
--------

Running a scenario is very different than running real events for a few reasons:
* There isn't any data to be concerned about
* The date/time doesn't really matter unless required for a specific
  exercise
* Scenarios are organized in COMCAT by scenario catalogs, and each catalog
  needs to have an associated "catalog page" on the earthquake website that
  describes how the scenarios are created

In the future, all of this will be run within Python in ShakeMap 4.0. However,
this code was created to address some issues that could not be handled in the
current version of ShakeMap, such as the use of multiple GMPEs, and the
inclusion of new GMPEs that are not available in ShakeMap 3.5. However, the code
in this repository only handles the generation of the ground motion grids. The
generation of products (e.g., maps, shapefiles, etc.) and transferring of the
products to COMCAT is still handled with ShakeMap 3.5, but there are some helper
functions in here to facilitate the interaction of the different codes.

Installation and Dependencies
-----------------------------
Run the `install.sh` script in this repository.


Workflow
--------

### Paths

You need to configure some paths in a conf file. Create a file in the user home
directory named `scenarios.conf` with the following contents:
```ini
[scenarios]
shakehome = /home/user/shake
pdlbin = /home/user/ProductClient/ProductClient.jar
pdlkey = /home/user/ProductClient/key
pdlconf = /home/user/ProductClient/scenarioconfig.ini
catalog = test
vs30file = /home/user/data/global_vs30.grd
```

### Prepare event directory in ShakeMap 4

Edit event.xml and *_fault.txt. Notes:
    * Fault file should be in "new" format (lon, lat, depth)
    * Be sure event id ends with "_se"

Setup event-specific model.conf file
    * Check GMPEs
    * Check extent and resolution

Run ShakeMap 4 to generate ground motions
```
shake <event id> assemble model mapping
```
Note: the `mapping` coremod is optional but it is useful to review the results
before proceeding.


### Prepare ShakeMap 3 input directory

`shake4to3 <event id>`

### Run ShakeMap 3

```
from scenarios.utils import run_one_old_shakemap
log = run_one_old_shakemap(<event id>)
```


### Transfer

**IMPORTANT:** Be sure to double/triple check that the catalog code is correct
in `[SHAKEHOME]/config/transfer.conf`, which is specified in __two__ places. For
catalog code `BSSC2014`, this is what the pertinent section of the conf file
should look like:
```
pdl_java : /usr/bin/java
pdl_client : /home/<user>/ProductClient/ProductClient.jar
pdl_source : us
pdl_type : shakemap
pdl_scenariotype : shakemap-scenario
pdl_code : bssc2014<EVENT>
pdl_eventsource : bssc2014
pdl_eventsourcecode : <EVENT>
pdl_privatekey : /home/<user>/ProductClient/comcat_atlaskey
pdl_config: /home/<user>/ProductClient/scenarioconfig.ini
```
_If you mess this up, it creates havoc in COMCAT because of the complex nature
of association, the lack of our ability to manually un-associate, and that we
cannot really delete anything. It is extremely difficult to fix._

Unlike for older scenarios, we now have to also send an origin. Here is a script
that sends origins for all of the events in the data directory:
```python
import os
from scenarios.utils import send_origin
from configobj import ConfigObj
from impactutils.io.cmd import get_command_output
config = ConfigObj(os.path.join(os.path.expanduser('~'), 'scenarios.conf'))
datadir = os.path.join(config['system']['shakehome'], 'data')
id_str = next(os.walk(datadir))[1]
n = len(id_str)
logs = [None]*n
for i in range(0, n):
    logs[i] = send_origin(id_str[i])

```

To send the associated ShakeMap, we simply construct a call to the ShakeMap 3.5
`transfer` program:
```python
import os
from configobj import ConfigObj
from impactutils.io.cmd import get_command_output
config = ConfigObj(os.path.join(os.path.expanduser('~'), 'scenarios.conf'))
datadir = os.path.join(config['system']['shakehome'], 'data')
shakebin = os.path.join(config['system']['shakehome'], 'bin')
id_str = next(os.walk(datadir))[1]
n = len(id_str)
logs = [None]*n
for i in range(n):
    calltransfer = shakebin + '/transfer -event ' + id_str[i] + ' -pdl -scenario'
    logs[i] = get_command_output(calltransfer)
```

Sometimes it is difficult to know if the transfer has succeeded because of
caching. The logs are meant to help. It can also be helpful to know the caching
rules:

| Event age         | Cache time |
| ----------------- | ---------- |
| 7 days or less    | 1 min      |
| 30 days or less   | 15 min     |
| More than 30 days | 1 day      |
