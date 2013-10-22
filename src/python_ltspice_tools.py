#!/usr/bin/python
# Python Code used for testing spice circuits in LTSpice by rewriting the netlist file with new
# parameters, running the netlist in LTSpice, and interpreting the output
import re
import os
import sys

#----------------------------------------Remove Path from Name----------------------------------------#{{{1
def remove_path_from_name(full_filename):
    """removes the path info from a given full filename"""
    base_filename = full_filename.split("/")[-1]
    return(base_filename)
#----------------------------------------END Remove Path from Name----------------------------------------#}}}

#----------------------------------------Parameter Statement Class----------------------------------------#{{{1
class parameter_statement_class:
    """A container class for carrying around parameter statement info"""
    def __init__(self,variable,value,line_number=None):
        self.variable = variable
        self.value = value
        self.line_number = line_number
    def __repr__(self):
        return("{}={}".format(self.variable,self.value))
    def __str__(self):
        return("{}={}".format(self.variable,self.value))
#----------------------------------------END Parameter Statement Class----------------------------------------#}}}

#----------------------------------------Parameter Check----------------------------------------#{{{1
def parameter_check(line):
    """finds the parameter and value for a given line and parameter"""
    regex_string = "\S+ *= *\S+"
    param_regex = re.compile(regex_string,re.IGNORECASE)
    param_find = param_regex.findall(line)
    if param_find != []:
        return_list = []
        for a_param in param_find:
            a_param = a_param.strip("+")
            a_param = a_param.replace(" ","")
            a_param = a_param.split("=")
            variable = a_param[0]
            value = a_param[1]
            parameter_statement = parameter_statement_class(variable,value)
            return_list.append(parameter_statement)
        return(return_list)
    else:
        return(False)
#----------------------------------------END Parameter Check----------------------------------------#}}}

#----------------------------------------Find Given Param Statement----------------------------------------#{{{1
def find_given_param_statement(variable,line):
    """finds the parameter statement for a given line and vairable"""
    regex_string = "{} *= *\S+".format(variable)
    param_regex = re.compile(regex_string,re.IGNORECASE)
    param_find = param_regex.findall(line)
    if param_find != []:
        return(param_find[0])
    else:
        print("error finding parameter {}".format(variable))
#----------------------------------------END Find Given Param Statemen----------------------------------------#}}}

#----------------------------------------Change Parameter Value----------------------------------------#{{{1
def change_parameter_value(a_param,new_value,current_lines):
    """changes the value of the given parameter to the given new value in the current_lines list.
        Returns the new_lines list with the parameter changed"""
    current_line = current_lines[a_param.line_number]
    current_param_statment = find_given_param_statement(a_param.variable,current_line)
    new_param_statement = a_param.variable + "=" + new_value
    new_line = current_line.replace(current_param_statment,new_param_statement)
    new_lines = current_lines
    new_lines[a_param.line_number] = new_line
    return(new_lines)
#----------------------------------------END Change Parameter Value----------------------------------------#}}}

#----------------------------------------Create Local Log File----------------------------------------#{{{1
def create_local_log_file(log_filename,log_lines):
    """creates a local copy of the .log and returns the filename"""
    new_log_filename = log_filename.split("/")[-1]
    file = open(new_log_filename,"w")
    for line in log_lines:
        file.write(line+"\n")
    return(new_log_filename)
#----------------------------------------END Create Local Lof File----------------------------------------#}}}

#----------------------------------------Parameter Exception Class----------------------------------------#{{{1
class ParameterException(Exception):
    """An exception class for when the given parameter is not found in the file"""
    def __init__(self,given_parameter):
        self.given_parameter = given_parameter
    def __repr__(self):
        error_string = "ParameterError: No such parameter in netlist: {}".format(self.given_parameter)
        return(error_string)
    def __str__(self):
        error_string = "ParameterError: No such parameter in netlist: {}".format(self.given_parameter)
        return(error_string)            
#----------------------------------------END Parameter Exception Class----------------------------------------#}}}

#----------------------------------------Netlist Class----------------------------------------#{{{1
class netlist_class:
    """A container class for carrying around info about a netlist file"""
    def __init__(self,linux_filename):
        self.linux_filename = linux_filename
        
        if ".wine" in linux_filename:
            self.wine_filename = linux_filename.split("LTspiceIV/")[-1]
        self.name = remove_path_from_name(linux_filename)
        self.linux_directory = linux_filename.replace(self.name,"")
        self.wine_directory = self.linux_directory.split("LTspiceIV/")[-1]
        self.read_file()
        
    def __repr__(self):
        return(self.name)
    def __str__(self):
        return(self.name)

    def read_file(self):
        """Read the file's lines into a list, removing the endline characters, and placing it in the lines attribute. 
            Finds parameter statements and places them in parameter attributes"""
        file = open(self.linux_filename,"r")
        lines = file.readlines()
        edited_lines = []
        parameters = {}
        line_counter = 0
        for line in lines:
            edited_line = line[:-2]
            edited_lines.append(edited_line)
            param_check = parameter_check(line)
            if param_check != False:
                for a_param in param_check:
                    a_param.line_number = line_counter
                    parameters[a_param.variable] = a_param
            line_counter += 1
        self.lines = edited_lines
        self.parameters = parameters
        file.close()

    def change_single_param(self,a_variable,a_value):
        """Finds the given vairable in the netlist lines and replaces the current value with the given value.
            Returns the new lines of a new netlist with the value changed.
            Really only for internal use"""
        parameter_statment = self.parameters[a_variable]
        new_lines = change_parameter_value(a_param=parameter_statment,new_value=a_value,current_lines=self.lines)
        return(new_lines)

    def change_parameters(self,variable_value_dictionary,new_filename=None):
        """Changes all the parameters of the netlist lines to the values given in the varaible_value_dictionary.
            Returns a new netlist object. Give the full path to the new linux filename if you don't want to use
            the default new filename."""
        ##Create the new_netlist from the old and rename it's by appending "new" or the given filename
        new_netlist = self
        if new_filename == None:
            new_netlist.name = "{}_new".format(self.name.split(".net")[0])+".net"
            new_netlist.linux_filename = self.linux_directory + new_netlist.name
            new_netlist.wine_filename = self.wine_directory + new_netlist.name
        else:
            new_netlist.linux_filename = new_filename
            if ".wine" in new_filename:
                self.wine_filename = new_filename.split("LTspiceIV/")[-1]
            new_netlist.name = remove_path_from_name(new_filename)
            new_netlist.linux_directory = new_filename.replace(self.name,"")
            new_netlist.wine_directory = new_netlist.linux_directory.split("LTspiceIV/")[-1]
        
        ##Change the parameters and update the new parameter dictionary
        new_parameters = self.parameters
        for variable, value in variable_value_dictionary.iteritems():
            try:
                new_netlist.lines = new_netlist.change_single_param(variable,value)
            except KeyError as keyerror:
                print(ParameterException(keyerror.args[0]))
                sys.exit(0)
            new_parameter_statement = parameter_statement_class(variable,value)
            new_parameter_statement = new_parameters[variable]
            new_parameter_statement.value = value
            new_parameters[variable] = new_parameter_statement
        new_netlist.parameters = new_parameters   

        return(new_netlist)

    def write_file(self):
        """Writes the lines to the netlist file"""
        file = open(self.linux_filename,"w")
        for line in self.lines:
            file.write(line+"\n")
        file.close()

    def run_netlist(self):
        """Runs the given netlist assuming the netlist is in the LTspiveIV directory"""
        self.write_file()
        command = "run_netlist.sh {}".format(self.wine_filename)
        os.system(command)
        
        #Read in log file and check for errors
        print("reading in .log file")
        log_filename = self.linux_filename.replace(".net",".log")
        file = open(log_filename,"r")
        log_lines = file.readlines()
        edited_lines = []
        error = False
        for line in log_lines:
            edited_line = line[:-2]
            edited_lines.append(edited_line)
            if "Error" in line:
                error = True
        log_lines = edited_lines
        local_log_filename = create_local_log_file(log_filename,log_lines)
        if error == True:
            command = "gedit {}&".format(local_log_filename)
            os.system(command)
            sys.exit(0)
        else: #if no errors make raw_values object
            raw_values = raw_values_class(self.linux_filename,log_filename=local_log_filename,log_lines=log_lines)        
            return(raw_values)
#----------------------------------------END Netlist Class----------------------------------------#}}}

#----------------------------------------Variable Value Class----------------------------------------#{{{1
class node_value_class:
    """Container class for node-value pairs"""
    def __init__(self,node,node_number,node_type,value=None):
        self.node = node
        self.value = value
        self.node_number = node_number
        self.node_type = node_type
        self.find_unit()
    def __repr__(self):
        return_string = "{} = {} {}".format(self.node,self.value,self.unit)
        return(return_string)
    def __str__(self):
        return_string = "{} = {} {}".format(self.node,self.value,self.unit)
        return(return_string)
    def find_unit(self):
        """pulls the unit, ie V, A, Ohm, out of the node type"""
        if "voltage" in self.node_type:
            self.unit = "V"
        elif "current" in self.node_type:
            self.unit = "A"
#----------------------------------------END Variable Value Class----------------------------------------#}}}

#----------------------------------------Pull Node----------------------------------------#{{{1
def pull_node(line):
    """Pulls the node, node number, and node type out of the line. Returns a node_value_class obj"""
    elements = line.split("\t")
    elements = elements[1:]

    #node number
    node_number = int(elements[0])
    #node name
    node = elements[1].split("(")
    node = node[1].replace(")","")
    #node type
    node_type = elements[2]
    node_value_pair = node_value_class(node=node,node_number=node_number,node_type=node_type)
    return(node_value_pair)
#----------------------------------------END Pull Vairable----------------------------------------#}}}

#----------------------------------------Pull Value----------------------------------------#{{{1
def pull_value(line):
    """pulls the float value out of a given value line and returns a float obj"""
    float_regex = re.compile("-*\d.\d+e[-+]\d+")
    string_value = float_regex.findall(line)[0]
    float_value = float(string_value)
    return(float_value)
#----------------------------------------END Pull Value----------------------------------------#}}}

#----------------------------------------Raw Values Class----------------------------------------#{{{1
class raw_values_class:
    """Class for a raw file output. Contains a dictionary with all the node names and their values.
        Has methods for reading in a .raw file. Can convert a given .net filename into corresponding .raw"""
    def __init__(self,filename,log_filename,log_lines):
        self.raw_filename = filename.replace(".net",".raw")#convert .net to .raw
        self.log_filename = log_filename
        self.log_lines = log_lines
        self.name = remove_path_from_name(self.raw_filename)
        self.read_in_file()

    def __repr__(self):
        return(self.name)
    def __str__(self):
        return(self.name)

    def read_in_file(self):
        """Reads in the raw collect and collects the node and value info storing them indiciviually in a 
            node value class. Returns a dictionary of node names and corresponding node value classes"""
        file = open(self.raw_filename,"r")
        self.raw_file_lines = file.readlines()
        file.close()
        
        start_nodes = False
        start_values = False
        value_count = 0
        node_values = []
        for line in self.raw_file_lines:
            line=line[:-2]
            if "Variables:" in line:
                if "No. Variables" not in line:
                    start_nodes = True

            elif "Values:" in line:
                start_nodes = False
                start_values = True

            elif start_nodes == True:
                node_value_pair = pull_node(line)
                node_values.append(node_value_pair)

            elif start_values == True:
                value = pull_value(line)
                node_values[value_count].value = value
                value_count += 1
        node_dictionary = {}
        for node_value in node_values:
            node_dictionary[node_value.node] = node_value
        self.node_values = node_dictionary

    def return_node_value(self,name,name_type="node"):
        """Returns the node_value object correspoding to the name given. If name_type option is set to 
            "device" it will return the device current otherwise it defaults to "node" and returns a node voltage"""
        if name_type == "node":
            name = name.lower()
        elif name_type == "device":
            name = name.capitalize()
        else:
            print("Invalid name_type for return_node_value")
            sys.exit(0)
        node_value = self.node_values[name]
        return(node_value)
#----------------------------------------END Raw Values Class----------------------------------------#}}}
        

