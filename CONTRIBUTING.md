# Contributing to hotsos

Hotsos comprises a set of plugins that analyse application-specific data. While
all plugins and library code are currently written in Python, they are not
necessarily constrained to this as long as their output meets the standard
requirements (see plugins section). It is nevertheless recommended to write
plugins in Python so as to be able to leverage the (core) library code and unit
test facilities.

As a matter if principle, the aim should always be that plugin implementations
contains the least possible code and anything that could be shared should go
into the core library code (see core section).

## Key Components:

### defs

In order reduce/remove the need to carry metadata such as search definitions in
code, they are instead stored in yaml. Currently we have the following yaml
definitions:

* bugs - Defines search criteria used to identify bugs in log files. Includes
         information such as search expression and output message. These
         searches do not require accompanying code and are run automatically
         per plugin.

* events - Defines search criteria used to identify events in log files.

* config_checks - Defines criteria for indentifying invalid configuration.
 
* package\_bug\_checks - Defines criteria for identifying whether installed
                         packages contain known bugs.

* plugins - This is the high level Python plugin driver.


### core

This is the home for shared code and comprises mainly of plugin library code as
well as code required to operate hotsos.

### plugins

This is where plugins are implemented. A plugin comprises of a high level
eponymous directory containing any number of plugin "parts" which are a way of
breaking down the structure of the plugin using meaningfully named files.


### tests

python mock based unit tests
