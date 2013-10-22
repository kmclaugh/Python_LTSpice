#!/usr/bin/python
# Python Code used for testing spice circuits in LTSpice by rewriting the netlist file with new
# parameters, running the netlist in LTSpice, and interpreting the output
import re
import os

#----------------------------------------Find Param Equals----------------------------------------#{{{1
def find_param_equals(parameter,line):
    """finds the parameter and value for a given line and parameter"""
    regex_string = "{} *= *\S+".format(parameter)
    param_regex = re.compile(regex_string,re.IGNORECASE)
    param_find = param_regex.findall(line)
    if param_find != []:
        return(param_find[0])
    else:
        return(False)
#----------------------------------------END Find Param Equals----------------------------------------#}}}

#----------------------------------------Original Line Class----------------------------------------#{{{1
class original_line_class:
    """container class for carrying around line and line numbers"""
    def __init__(self,line,line_number):
        self.line = line
        self.number = line_number
    def __repr__(self):
        return(self.line)
    def __str__(self):
        return(self.line)

#----------------------------------------End Original Line Class----------------------------------------#}}}

#----------------------------------------Process File----------------------------------------#{{{1
def process_file(filename):
    """Reads the .net file and picks out the parameters one is interested in"""
    file = open(filename,"r")
    original_file = []
    lines = file.readlines()
    line_count = 0
    param_line = False
    for line in lines:
        line=line[:-2]
        original_line = original_line_class(line,line_count)
        original_file.append(original_line)
        line_count += 1
    return(original_file)
#----------------------------------------END Process File----------------------------------------#}}}

#----------------------------------------Read Parameter Lines----------------------------------------#{{{1
def read_parameter_lines(original_lines_list,parameter_header_name):
    """Picks out the lines with the given parameters """
    parameter_lines = []
    param_line = False
    for original_line in original_lines_list:
        if parameter_header_name in original_line.line:
            if "End" in original_line.line:
                end_param_statement = original_line
                param_line = False
                parameter_lines.append(original_line)
            else:
                start_param_statement = original_line
                param_line = True
        if param_line == True:
            parameter_lines.append(original_line)
    return(parameter_lines)
#----------------------------------------END Process File----------------------------------------#}}}

#----------------------------------------Param Statement Class----------------------------------------#{{{1
class param_statement_class:
    """A class that defines a parameter in a netlist file. For instance:
            R0=1k"""

    def __init__(self,parameter,original_line):
        self.param_statement = parameter
        self.original_line = original_line
        self.find_param_equals()
         
    def find_param_equals(self):
        param_find = self.param_statement.split("=")
        self.param_equals = param_find[1].replace(" ","")

    def replace_param_equals(self,new_param_statement,current_file_list):
        current_line = current_file_list[self.original_line.number]
        new_line = current_line.line.replace(self.param_statement,new_param_statement)
        new_line = original_line_class(new_line,self.original_line.number)
        current_file_list[self.original_line.number] = new_line
        return(current_file_list)
#----------------------------------------END Param Statement Clas----------------------------------------#}}}

#----------------------------------------Switch Param Equals----------------------------------------#{{{1
def switch_param_equals(change_params,original_file_list,parameter_lines):
    """Switches parameter equals in the old file with the new given parameters.
        change parameters are given as list in the format (parameter,new_equals)"""
    current_file_list = original_file_list
    for line in parameter_lines:
        updated_line = line
        for change_param in change_params:
            if change_param[0] in line.line:
                orig_param_equals = find_param_equals(change_param[0],updated_line.line)

                if orig_param_equals != False:
                    param_statement = param_statement_class(orig_param_equals,updated_line)
                    new_param_statement = change_param[0]+"="+str(change_param[1])
                    current_file_list = param_statement.replace_param_equals(new_param_statement,current_file_list)
                    updated_line = current_file_list[param_statement.original_line.number]
    return(current_file_list)
#----------------------------------------END Switch Param Equals----------------------------------------#}}}

#----------------------------------------Write New Net File----------------------------------------#{{{1
def write_new_net_file(current_file_list,original_filename):
    """Writes the new .net file so it is ready to run. Returns the new linux filename and wine filename"""
    new_filename_linux = original_filename[:-4]+"_new"+".net"
    file = open(new_filename_linux,"w")
    for line in current_file_list:
        file.write(line.line+"\n")
    file.close()
    new_filename_wine = new_filename_linux.split("LTspiceIV/")[-1]
    return(new_filename_linux,new_filename_wine)
#----------------------------------------END Write New Net File----------------------------------------#}}}

#----------------------------------------Run Netlist----------------------------------------#{{{1
def run_netlist(net_filename):
    """Runs the given netlist assuming the netlist is in the LTspiveIV directory"""
    command = "run_netlist.sh {}".format(net_filename)
    os.system(command)
#----------------------------------------END Run Netlist----------------------------------------#}}}

#----------------------------------------Variable Value Class----------------------------------------#{{{1
class variable_value_class:
    """Container class for variable-value pairs"""
    def __init__(self,variable,variable_number,variable_type,value=None,file_line=None):
        self.variable = variable
        self.value = value
        self.variable_number = variable_number
        self.variable_type = variable_type
        self.find_unit()
        self.file_line = file_line
    def __repr__(self):
        return_string = "{} = {} {}".format(self.variable,self.value,self.unit)
        return(return_string)
    def __str__(self):
        return_string = "{} = {} {}".format(self.variable,self.value,self.unit)
        return(return_string)
    def find_unit(self):
        """pulls the unit, ie V, A, Ohm, out of the variable type"""
        if "voltage" in self.variable_type:
            self.unit = "V"
        elif "current" in self.variable_type:
            self.unit = "A"
#----------------------------------------END Variable Value Class----------------------------------------#}}}

#----------------------------------------Pull Vairable----------------------------------------#{{{1
def pull_variable(line):
    """Pulls the variable, variable number, and variable type out of the line. Returns a vairable_value_class obj"""
    elements = line.split("\t")
    elements = elements[1:]

    #variable number
    variable_number = int(elements[0])
    #variable name
    variable = elements[1].split("(")
    variable = variable[1].replace(")","")
    #variable type
    variable_type = elements[2]
    variable_value_pair = variable_value_class(variable=variable,variable_number=variable_number,variable_type=variable_type)
    return(variable_value_pair)
#----------------------------------------END Pull Vairable----------------------------------------#}}}

#----------------------------------------Pull Value----------------------------------------#{{{1
def pull_value(line):
    """pulls the float value out of a given value line and returns a float obj"""
    float_regex = re.compile("-*\d.\d+e[-+]\d+")
    string_value = float_regex.findall(line)[0]
    float_value = float(string_value)
    return(float_value)
#----------------------------------------END Pull Value----------------------------------------#}}}

#----------------------------------------Read Variables----------------------------------------#{{{1
def read_variables(raw_filename):
    "Read the raw file and collects vairables and values. Returns a list of variable_value_class objects"""

    file = open(raw_filename,"r")
    raw_file_lines = file.readlines()
    file.close()
    start_variables = False
    start_values = False
    line_count = 0
    value_count = 0
    variable_values = []
    for line in raw_file_lines:
        line=line[:-2]
        if "Variables:" in line:
            if "No. Variables" not in line:
                start_variables = True

        elif "Values:" in line:
            start_variables = False
            start_values = True

        elif start_variables == True:
            variable_value_pair = pull_variable(line)
            variable_value_pair.file_line = line_count
            variable_values.append(variable_value_pair)

        elif start_values == True:
            value = pull_value(line)
            variable_values[value_count].value = value
            value_count += 1
    return(variable_values)
#----------------------------------------END Read Variables----------------------------------------#}}}


