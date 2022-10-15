#!/usr/bin/python

from array import array
import csv

import set_common as s

f = open("../firmware/src/src/basetrackersettings.h","w")
f.write("""\
/*
* This file is part of the Head Tracker distribution (https://github.com/dlktdr/headtracker)
* Copyright (c) 2022 Cliff Blackburn
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, version 3.
*
* This program is distributed in the hope that it will be useful, but
* WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
* General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program. If not, see <http://www.gnu.org/licenses/>.
*/

/**********************************************
 *
 *  !!! THIS FILE IS AUTOMATICALLY GENERATED, DO NOT EDIT DIRECTLY !!!
 *
 *  Modify /utils/settings.csv and execute buildsettings.py to generate this FW header
 *
 ***********************************************/

#pragma once

#include <stdint.h>
#include <string.h>
#include <math.h>

#include "arduinojsonwrp.h"

extern unsigned int encode_base64(unsigned char input[], unsigned int input_length,
                           unsigned char output[]);

class BaseTrackerSettings {
public:
""")

# Read the settings
s.readSettings()

# Write the constants to the file
for row in s.const:
  f.write("  static constexpr "  + s.typeToC(row[s.coltype]) + " " + row[s.colname] + " = " + row[s.coldefault] + ";\n")

# Write the Constructor
f.write("\n  BaseTrackerSettings() {\n")
for row in s.settingsarrays:
  start = row[s.colname].find("[")
  end = row[s.colname].find("]")
  arraylength = row[s.colname][start+1:end]
  name = row[s.colname][:start].lower()

  # Fill arrays with the default values
  if "char" in row[s.coltype]:
    f.write("    strcpy(" + name + ",\"" + row[s.coldefault] + "\");\n")
  else:
    f.write("    for(int i = 0; i < " + arraylength + "; i++) {\n")
    f.write("      " + name + "[i] = " + row[s.coldefault] + ";\n")
    f.write("    }\n")

for row in s.dataarrays:
  start = row[s.colname].find("[")
  end = row[s.colname].find("]")
  arraylength = row[s.colname][start+1:end]
  name = row[s.colname][:start].lower()
  f.write("    memset(" + name + ",0,sizeof(" + s.typeToC(row[s.coltype]) + ") * " + arraylength + ");\n")

f.write("\n    // Call Virtual Events after initialization\n")
events = set()
for row in s.settings:
  events.add(row[s.colfwonevnt])
for row in events:
  if row != "":
    f.write("    " + row + "();\n");
f.write("  }\n\n")

# Make Virtual Events
f.write("  // Virtual Events\n")

for row in events:
  if row != "":
    f.write("  virtual void " + row + "() {};\n")


# Write the get + set functions
f.write("\n")

for row in s.settings:
  if row[s.coltype].lower().strip() == "bool":
    txt = """\
  // {desc}
  inline const {dtype}& get{cname}() {{return {name};}}
  void set{cname}({dtype} val={deflt}) {{ {name} = val; }}\n
""".format(cname = row[s.colname], name = row[s.colname].lower(), dtype = s.typeToC(row[s.coltype]), deflt = row[s.coldefault].lower(), minv = row[s.colmin], maxv = row[s.colmax], desc = row[s.coldesc])
  else:
    txt = """\
  // {desc}
  inline const {dtype}& get{cname}() {{return {name};}}
  bool set{cname}({dtype} val={deflt}) {{
    if(val >= {minv} && val <= {maxv}) {{
      {name} = val;
      return true;
    }}
    return false;
  }}\n\n""".format(cname = row[s.colname], name = row[s.colname].lower(), dtype = s.typeToC(row[s.coltype]), deflt = row[s.coldefault], minv = row[s.colmin], maxv = row[s.colmax], desc = row[s.coldesc])
  f.write(txt)

# Get & Set for the Settings Arrays
for row in s.settingsarrays:
  start = row[s.colname].find("[")
  end = row[s.colname].find("]")
  arraylength = row[s.colname][start+1:end]
  if row[s.coltype].lower().strip() != "char":
    txt = """\
  // {desc}
  void get{cname}({dtype} dest[{len}]) {{memcpy(dest, {name}, sizeof({dtype}) * {len});}}
  bool set{cname}(const {dtype} val[{len}]) {{
    bool changed = false;
    for(int i=0; i < {len}; i++) {{
      if({name}[i] >= {minv} && {name}[i] <= {maxv}) {{
        {name}[i] = val[i];
        changed = true;
      }}
    }}
    return changed;
  }}\n\n""".format(cname = row[s.colname][:start], name = row[s.colname][:start].lower(), dtype = s.typeToC(row[s.coltype].strip()), deflt = row[s.coldefault], minv = row[s.colmin], maxv = row[s.colmax], desc = row[s.coldesc], len = arraylength )
  else:
    txt = """\
  // {desc}
  void get{cname}({dtype}* dest) {{strcpy(dest, {name});}}
  void set{cname}(const char *val) {{
    strncpy({name}, val, {len}+1);
    {name}[{len}] = '\\0';
  }}\n\n""".format(cname = row[s.colname][:start], name = row[s.colname][:start].lower(), dtype = s.typeToC(row[s.coltype].strip()), deflt = row[s.coldefault], minv = row[s.colmin], maxv = row[s.colmax], desc = row[s.coldesc], len = arraylength )

  f.write(txt)

# Set Functions for the Data Items
for row in s.data:
  txt = """\
  // {desc}
  void setData{cname}({dtype} val) {{ {name} = val; }}\n
""".format(cname = row[s.colname], name = row[s.colname].lower(), dtype = s.typeToC(row[s.coltype].strip()), deflt = row[s.coldefault], minv = row[s.colmin], maxv = row[s.colmax], desc = row[s.coldesc])
  f.write(txt)

# Get & Set for the Data Arrays
for row in s.dataarrays:
  start = row[s.colname].find("[")
  end = row[s.colname].find("]")
  arraylength = row[s.colname][start+1:end]
  if row[s.coltype].lower().strip() != "char":
    txt = """\
  // {desc}
  void setData{cname}(const {dtype} val[{len}]) {{
    memcpy({name}, val, {len});
  }}\n\n""".format(cname = row[s.colname][:start], name = row[s.colname][:start].lower(), dtype = s.typeToC(row[s.coltype].strip()), deflt = row[s.coldefault], minv = row[s.colmin], maxv = row[s.colmax], desc = row[s.coldesc], len = arraylength )
  else:
    txt = """\
  // {desc}
  void setData{cname}(const char *val) {{
    strncpy({name}, val, {len}+1);
    {name}[{len}] = '\\0';
  }}\n\n""".format(cname = row[s.colname][:start], name = row[s.colname][:start].lower(), dtype = s.typeToC(row[s.coltype].strip()), deflt = row[s.coldefault], minv = row[s.colmin], maxv = row[s.colmax], desc = row[s.coldesc], len = arraylength )

  f.write(txt)

# Write all JSON Settings
f.write("  void setJSONSettings(DynamicJsonDocument &json) {\n")
for row in s.settings:
  f.write("    json[\"" + row[s.colname].lower() + "\"] = " + row[s.colname].lower() + ";\n");
f.write("  }\n")

# Read JSON Settings
f.write("\n  void loadJSONSettings(DynamicJsonDocument &json) {\n    JsonVariant v;\n")
for row in events: # On change call required
  if row != "":
    f.write("    bool ch" + row.lower() + " = false;\n");
for row in s.settings:
  f.write("    v = json[\"" + row[s.colname].lower() + "\"]; if(!v.isNull()) {set" + row[s.colname] + "(v);");
  if row[s.colfwonevnt] == "":
    f.write("}\n")
  else:
    f.write(" ch" + row[s.colfwonevnt].lower() + " = true;}\n")
for row in events: # Do the on Change call
  if row != "":
    f.write("    if(ch" + row.lower() + ")\n      " + row + "();\n");
f.write("  }\n")

# All JSON data Items
f.write("\n  void setJSONDataList(DynamicJsonDocument &json)\n  {\n")
f.write("    JsonArray array = json.createNestedArray();\n")
for row in s.data:
  f.write("    array.add(\""+ row[s.colname].lower() + "\");\n")
for row in s.dataarrays:
  start = row[s.colname].find("[")
  f.write("    array.add(\""+ row[s.colname][:start].lower() + "\");\n")
f.write("  }\n")

# Choose what items to send
f.write("""\n\
  // Sets if a data item should be included while in data to GUI
  void setDataItemSend(const char *var, bool enabled)
  {
""")
id = 0
for row in s.data:
  _else = ""
  if id > 0:
    _else = "else "
  id += 1
  txt = """\
    {_else}if (strcmp(var, \"{name}\") == 0) {{
      enabled == true ? senddatavars |= 1 << {id} : senddatavars &= ~(1 << {id});
      return;
    }}
""".format(_else = _else, name = row[s.colname].lower(), id = id)
  f.write(txt)
id = 0
for row in s.dataarrays:
  start = row[s.colname].find("[")
  id += 1
  txt = """\
    else if (strcmp(var, \"{name}\") == 0) {{
      enabled == true ? senddataarray |= 1 << {id} : senddataarray &= ~(1 << {id});
      return;
    }}
""".format(name = row[s.colname].lower()[:start], id = id)
  f.write(txt)
f.write("  }\n")

f.write("""\n\
  void sendArray(DynamicJsonDocument &json,
                 uint8_t bit,
                 const uint32_t counter,
                 int divisor,
                 const char *name,
                 void *item,
                 void *lastitem,
                 int size)
  {
    bool sendit = false;
    char b64array[200];
    if (senddataarray & (1 << bit)) {
      if (divisor < 0) {
        if (memcmp(lastitem, item, size) != 0)
          sendit = true;
        else if (divisor != -1 && counter % abs(divisor) == 0)
          sendit = true;
      } else {
        if (counter % divisor == 0)
          sendit = true;
      }
      if (sendit) {
        encode_base64((unsigned char *)item, size, (unsigned char *)b64array);
        json[name] = b64array;
        memcpy(lastitem, item, size);
      }
    }
  }
  """)

# Transmit Data items back to the gui
f.write("\n  void setJSONData(DynamicJsonDocument &json)\n  {\n")
f.write("""\
    // Sends only requested data items
    // Updates only as often as specified, 1 = every cycle
    // Base64 only done on arrays as it ends up on avg more bytes to
    //   do everything

    static uint32_t counter = 0;

""")
id = 0
for row in s.data:
  id += 1
  try:
    round = int(row[s.colround])
    round = pow(10, round)
  except ValueError:
    round = 1000

  if row[s.coltype].lower().strip() == "float":
    valtxt = "roundf(((float)" + row[s.colname].lower() + " * {round})) / {round}".format(round = round)
  else:
    valtxt = row[s.colname].lower()

  txt = """\
    if (senddatavars & (1 << {id}) && (counter % {div}) == 0)
      json["{vname}"] = {value};
""".format(vname = row[s.colname].lower(), value=valtxt, div= row[s.coldivisor], id=id)
  f.write(txt)

f.write("\n")

id = 0
for row in s.dataarrays:
  id += 1
  start = row[s.colname].find("[")
  end = row[s.colname].find("]")
  arraylength = row[s.colname][start+1:end]
  name = row[s.colname].lower()[:start]
  name6 = "6" + name + s.typeToJson(row[s.coltype].strip())
  ctype = s.typeToC(row[s.coltype].strip())
  f.write("    sendArray(json," + str(id) + ",counter," + row[s.coldivisor] + ",\"" + name6 + "\",(void*)" + name + ",(void*)last" + row[s.colname].lower()[:start]  + ", sizeof(" + ctype + ") * " + arraylength + ");\n")
f.write("""\

    // Used for reduced data divisor
    counter++;
  }\n\n""")


# Stop All Data Function
f.write("""\
  void stopAllData()
  {
    senddatavars = 0;
    senddataarray = 0;
  }
""")

# Variables
f.write("\nprotected:\n")

f.write("""\
  // Bit map of data to send to GUI, max 64 items
  uint64_t senddatavars;
  uint64_t senddataarray;
""")

f.write("\n  // Settings\n")
for row in s.settings:
  if "bool" in row[s.coltype]:
    dflt = row[s.coldefault].lower().strip()
  else:
    dflt = row[s.coldefault].strip()
  f.write("  " + s.typeToC(row[s.coltype]) + " " + row[s.colname].lower().strip())
  if row[s.coldefault] == "":
    f.write (";")
  else:
    f.write (" = " + dflt + ";")

  f.write(" // " + row[s.coldesc] + "\n")

f.write("\n  // Setting Arrays\n")
for row in s.settingsarrays:
  start = row[s.colname].find("[")
  end = row[s.colname].find("]")
  arlen = row[s.colname][start+1:end]
  if row[s.coltype].lower().strip() == "char":
    try:
      arlen = int(arraylength)
      arlen += 1 # Increment Storage Space For Null
      arlen = str(arlen)
    except ValueError:
      arlen = arraylength
  f.write("  " + s.typeToC(row[s.coltype]) + " " + row[s.colname][:start].lower() + "[" + arlen + "]; // " + row[s.coldesc] + "\n")

f.write("\n  // Real Time Data\n")
for row in s.data:
  f.write("  " + s.typeToC(row[s.coltype]) + " " + row[s.colname].lower() + " = 0; // " + row[s.coldesc] + "\n")

f.write("\n  // Real Time Data Arrays\n")
for row in s.dataarrays:
  start = row[s.colname].find("[")
  end = row[s.colname].find("]")
  arlen = row[s.colname][start+1:end]
  if row[s.coltype].lower().strip() == "char":
    try:
      arlen = int(arraylength)
      arlen += 1
      arlen = str(arlen)
    except ValueError:
      arlen = arraylength
  f.write("  " + s.typeToC(row[s.coltype]) + " " + row[s.colname][:start].lower() + "[" + arlen + "]; // " + row[s.coldesc] + "\n")
  f.write("  " + s.typeToC(row[s.coltype]) + " last" + row[s.colname][:start].lower() + "[" + arlen + "]; // " + row[s.coldesc] + "\n")

# Close Class
f.write("};\n")

f.close()

print("Gernerated Firmware Settings Base Class")