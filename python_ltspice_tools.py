#!/usr/bin/python
# Python Code used for testing spice circuits in LTSpice by rewriting the netlist file with new
# parameters, running the netlist in LTSpice, and interpreting the output
import re
import os

def remove_path_from_name(full_filename):
    """removes the path info from a given full filename"""
    base_filename = full_filename.split("/")[-1]
    return(base_filename)


class parameter_statement_class:
    """a container class for carrying around parameter statement info"""
    def __init__(self,variable,value,line_number=None):
        self.variable = variable
        self.value = value
        self.line_number = line_number
    def __repr__(self):
        return("{}={}".format(self.variable,self.value))
    def __str__(self):
        return("{}={}".format(self.variable,self.value))



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

def find_given_param_statement(variable,line):
    """finds the parameter statement for a given line and vairable"""
    regex_string = "{} *= *\S+".format(variable)
    param_regex = re.compile(regex_string,re.IGNORECASE)
    param_find = param_regex.findall(line)
    if param_find != []:
        return(param_find[0])
    else:
        print("error finding parameter {}".format(variable))

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
            new_netlist.lines = new_netlist.change_single_param(variable,value)
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

original_filename = "/home/kevin/.wine/drive_c/Program Files/LTC/LTspiceIV/Photoresistor_Array/Photoresistor_Array.net"
original_netlist = netlist_class(original_filename)
change_params = {"R00":"1k","R01":"5k"}
new_netlist = original_netlist.change_parameters(change_params)
new_netlist.run_netlist()
