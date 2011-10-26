#!/usr/bin/python
#
# Copyright (c) 2011 Ivan Vladimirov Ivanov (ivan.vladimirov.ivanov@gmail.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.


"""
This module implements the virtual machine for the Hack platform described in
chapter 7 and chapter 8 of the book "The Elements of Computing Systems:
Building a Modern Computer from First Principles"
(http://www1.idc.ac.il/tecs/).
"""


__author__ = "Ivan Vladimirov Ivanov (ivan.vladimirov.ivanov@gmail.com)"


import os
import re
import sys


# The following classes model the hack virtual machine commands.


class AddCommand(object): pass


class SubCommand(object): pass


class NegCommand(object): pass


class EqCommand(object): pass


class GtCommand(object): pass


class LtCommand(object): pass


class AndCommand(object): pass


class OrCommand(object): pass


class NotCommand(object): pass


class PushCommand(object):
  def __init__(self, segment, index):
    self.segment = segment
    self.index = index


class PopCommand(object):
  def __init__(self, segment, index):
    self.segment = segment
    self.index = index


class LabelCommand(object):
  def __init__(self, label_name):
    self.label_name = label_name


class GotoCommand(object):
  def __init__(self, label_name):
    self.label_name = label_name


class IfGotoCommand(object):
  def __init__(self, label_name):
    self.label_name = label_name


class FunctionCommand(object):
  def __init__(self, function_name, local_variables):
    self.function_name = function_name
    self.local_variables = local_variables


class CallCommand(object):
  def __init__(self, function_name, arguments):
    self.function_name = function_name
    self.arguments = arguments


class ReturnCommand(object): pass


class EmptyCommand(object): pass


class ErrorCommand(object):
  def __init__(self, line):
    self.line = line


class VMError(Exception):
  def __init__(self, message):
    self.message = message


class HackParser(object):
  """This class is responsible for all parsing logic.

  Parsing means converting a string representation of a program line into an
  instance of one of the command types, an EmptyCommand or and ErrorCommand.
  """

  _SEGMENT_NAMES = [
      "argument",
      "local",
      "static",
      "constant",
      "this",
      "that",
      "pointer",
      "temp"
  ]

  # specifies the order in which commands will attempt to be parsed.
  _COMMAND_PARSE_ORDER = [
      AddCommand,
      SubCommand,
      NegCommand,
      EqCommand,
      GtCommand,
      LtCommand,
      AndCommand,
      OrCommand,
      NotCommand,
      PushCommand,
      PopCommand,
      LabelCommand,
      GotoCommand,
      IfGotoCommand,
      FunctionCommand,
      CallCommand,
      ReturnCommand,
      EmptyCommand,
      ErrorCommand
  ]

  _RE_LABEL = re.compile(r"[a-zA-Z_\.:][a-zA-Z0-9_\.:]*")

  _RE_NUMBER = re.compile(r"\d+")

  @staticmethod
  def ParseCommand(line):
    """Parses a program line.

    Args:
      line: A string with the line to be parsed.

    Returns:
      An instance of one of the command types or an instance ErrorCommand.
    """
    line = HackParser._TrimProgramLine(line)
    for command in HackParser._COMMAND_PARSE_ORDER:
      result = getattr(HackParser, "Parse" + command.__name__)(line)
      if result:
        return result

  @staticmethod
  def ParseAddCommand(line):
    return HackParser._ParseSimpleCommand(line, "add", AddCommand)

  @staticmethod
  def ParseSubCommand(line):
    return HackParser._ParseSimpleCommand(line, "sub", SubCommand)

  @staticmethod
  def ParseNegCommand(line):
    return HackParser._ParseSimpleCommand(line, "neg", NegCommand)

  @staticmethod
  def ParseEqCommand(line):
    return HackParser._ParseSimpleCommand(line, "eq", EqCommand)

  @staticmethod
  def ParseGtCommand(line):
    return HackParser._ParseSimpleCommand(line, "gt", GtCommand)

  @staticmethod
  def ParseLtCommand(line):
    return HackParser._ParseSimpleCommand(line, "lt", LtCommand)

  @staticmethod
  def ParseAndCommand(line):
    return HackParser._ParseSimpleCommand(line, "and", AndCommand)

  @staticmethod
  def ParseOrCommand(line):
    return HackParser._ParseSimpleCommand(line, "or", OrCommand)

  @staticmethod
  def ParseNotCommand(line):
    return HackParser._ParseSimpleCommand(line, "not", NotCommand)

  @staticmethod
  def ParsePushCommand(line):
    parts = line.split()
    if (len(parts) == 3 and parts[0] == "push"
        and parts[1] in HackParser._SEGMENT_NAMES
        and parts[2].isdigit()):
      return PushCommand(parts[1], int(parts[2]))
    else:
      return False

  @staticmethod
  def ParsePopCommand(line):
    parts = line.split()
    if (len(parts) == 3 and parts[0] == "pop"
        and parts[1] in HackParser._SEGMENT_NAMES
        and parts[1] != "constant" and parts[2].isdigit()):
      return PopCommand(parts[1], int(parts[2]))
    else:
      return False

  @staticmethod
  def ParseLabelCommand(line):
    return HackParser._ParseGenericLabelCommand(line, "label", LabelCommand)

  @staticmethod
  def ParseGotoCommand(line):
    return HackParser._ParseGenericLabelCommand(line, "goto", GotoCommand)

  @staticmethod
  def ParseIfGotoCommand(line):
    return HackParser._ParseGenericLabelCommand(line, "if-goto", IfGotoCommand)

  @staticmethod
  def ParseFunctionCommand(line):
    return HackParser._ParseGenericFunctionCommand(line, "function", FunctionCommand)

  @staticmethod
  def ParseCallCommand(line):
    return HackParser._ParseGenericFunctionCommand(line, "call", CallCommand)

  @staticmethod
  def ParseReturnCommand(line):
    if line == "return":
      return ReturnCommand()
    else:
      return False

  @staticmethod
  def ParseEmptyCommand(line):
    return HackParser._ParseSimpleCommand(line, "", EmptyCommand)

  @staticmethod
  def ParseErrorCommand(line):
    return ErrorCommand(line)

  @staticmethod
  def _TrimProgramLine(line):
    try:
      return line[:line.index("//")].strip()
    except ValueError:
      return line.strip()

  @staticmethod
  def _ParseSimpleCommand(line, command_name, constructor):
    if line == command_name:
      return constructor()
    else:
      return False

  @staticmethod
  def _ParseGenericLabelCommand(line, command_name, constructor):
    parts = line.split()
    if (len(parts) == 2 and parts[0] == command_name
        and re.match(HackParser._RE_LABEL, parts[1])):
      return constructor(parts[1])
    else:
      return False

  @staticmethod
  def _ParseGenericFunctionCommand(line, command_name, constructor):
    parts = line.split()
    if len(parts) != 3: return False
    if (len(parts) == 3 and parts[0] == command_name
        and re.match(HackParser._RE_LABEL, parts[1])
        and re.match(HackParser._RE_NUMBER, parts[2])):
      return constructor(parts[1], int(parts[2]))
    else:
      return False


class HackCodeGenerator(object):
  """This class is responsible for generating Hack assembly code.

  The code generation works by transforming a Hack virtual machine command
  instance into a list of hack assembly instructions. This process sometimes
  requires the generation of context dependent assembly labels. To facilitate
  this the code generators require extra inputs: the name of the file in which
  the Hack virtual machine command resides, the name of the enclosing function,
  and the line number of the command. 
  """

  # Mapping from names to the addresses in RAM that represent them.
  _SEGMENT_MAPPING = {
      "sp": 0,
      "temp": 5,
      "pointer": 3,
      "argument": 2,
      "local": 1,
      "this": 3,
      "that": 4,
      "static": 16
  }

  @staticmethod
  def GenerateAsm(command, name, function_name, number):
    """Transforms a VM command into a list of Hack assembly instructions.

    Args:
      command: An instance of one of the command types.
      name: The name of the file in which the command resides.
      function_name: The name of the function in which the command is found.
      number: The line number of the command.

    Returns:
      A list of strings containing the assembly instructions for the command.
    """
    generator = getattr(
        HackCodeGenerator, "GenerateAsm" + command.__class__.__name__)
    return generator(command, name, function_name, number)

  @staticmethod
  def GenerateAsmAddCommand(command, name, function_name, number):
    return HackCodeGenerator._ApplyBinaryTemplate("+")

  @staticmethod
  def GenerateAsmSubCommand(command, name, function_name, number):
    return HackCodeGenerator._ApplyBinaryTemplate("-")

  @staticmethod
  def GenerateAsmNegCommand(command, name, function_name, number):
    return HackCodeGenerator._ApplyUnaryTemplate("-")

  @staticmethod
  def GenerateAsmEqCommand(command, name, function_name, number):
    return HackCodeGenerator._ApplyComparisonTemplate("JEQ", name, number)

  @staticmethod
  def GenerateAsmGtCommand(command, name, function_name, number):
    return HackCodeGenerator._ApplyComparisonTemplate("JLT", name, number)

  @staticmethod
  def GenerateAsmLtCommand(command, name, function_name, number):
    return HackCodeGenerator._ApplyComparisonTemplate("JGT", name, number)

  @staticmethod
  def GenerateAsmAndCommand(command, name, function_name, number):
    return HackCodeGenerator._ApplyBinaryTemplate("&")

  @staticmethod
  def GenerateAsmOrCommand(command, name, function_name, number):
    return HackCodeGenerator._ApplyBinaryTemplate("|")

  @staticmethod
  def GenerateAsmNotCommand(command, name, function_name, number):
    return HackCodeGenerator._ApplyUnaryTemplate("!")

  @staticmethod
  def GenerateAsmPushCommand(command, name, function_name, number):
    if command.segment == "constant":
      return HackCodeGenerator._ApplyPushConstantTemplate(command.index)
    elif command.segment in ("temp", "pointer"):
      return HackCodeGenerator._ApplyPushDirectTemplate(
          HackCodeGenerator._SEGMENT_MAPPING[command.segment] + command.index)
    elif command.segment in ("argument", "local", "this", "that"):
      return HackCodeGenerator._ApplyPushIndirectTemplate(
          HackCodeGenerator._SEGMENT_MAPPING[command.segment], command.index)
    elif command.segment == "static":
      return HackCodeGenerator._ApplyPushDirectTemplate(
          "%s.%d" % (name, command.index))

  @staticmethod
  def GenerateAsmPopCommand(command, name, function_name, number):
    if command.segment in ("temp", "pointer"):
      return HackCodeGenerator._ApplyPopDirectTemplate(
          HackCodeGenerator._SEGMENT_MAPPING[command.segment] + command.index)
    elif command.segment in ("argument", "local", "this", "that"):
      return HackCodeGenerator._ApplyPopIndirectTemplate(
          HackCodeGenerator._SEGMENT_MAPPING[command.segment], command.index)
    elif command.segment == "static":
      return HackCodeGenerator._ApplyPopDirectTemplate(
          "%s.%d" % (name, command.index))

  @staticmethod
  def GenerateAsmLabelCommand(command, name, function_name, number):
    return ["(%s$%s)" % (function_name, command.label_name)]

  @staticmethod
  def GenerateAsmGotoCommand(command, name, function_name, number):
    return [
        "@%s$%s" % (function_name, command.label_name),
        "0;JMP"
    ]

  @staticmethod
  def GenerateAsmIfGotoCommand(command, name, function_name, number):
    return [
        "@SP",
        "M=M-1",
        "A=M",
        "D=M",
        "@%s$%s" % (function_name, command.label_name),
        "D;JNE"
    ]

  @staticmethod
  def GenerateAsmFunctionCommand(command, name, function_name, number):
    return sum([
        HackCodeGenerator._CreateLabel(command.function_name),
        HackCodeGenerator._PushConstant(0) * command.local_variables
    ], [])

  @staticmethod
  def GenerateAsmCallCommand(command, name, function_name, number):
    goto_name = command.function_name
    return_address = "%s$%d$return-address" % (name, number)
    return sum([
        HackCodeGenerator._PushConstant(return_address),
        HackCodeGenerator._PushFromMemory(
            HackCodeGenerator._SEGMENT_MAPPING["local"]),
        HackCodeGenerator._PushFromMemory(
            HackCodeGenerator._SEGMENT_MAPPING["argument"]),
        HackCodeGenerator._PushFromMemory(
            HackCodeGenerator._SEGMENT_MAPPING["this"]),
        HackCodeGenerator._PushFromMemory(
            HackCodeGenerator._SEGMENT_MAPPING["that"]),
        HackCodeGenerator._FromMemoryToD(
            HackCodeGenerator._SEGMENT_MAPPING["sp"]),
        HackCodeGenerator._AddConstantToD(-command.arguments - 5),
        HackCodeGenerator._FromDToMemory(
            HackCodeGenerator._SEGMENT_MAPPING["argument"]),
        HackCodeGenerator._FromMemoryToMemory(
            HackCodeGenerator._SEGMENT_MAPPING["sp"],
            HackCodeGenerator._SEGMENT_MAPPING["local"]),
        HackCodeGenerator._GotoLabel(goto_name),
        HackCodeGenerator._CreateLabel(return_address)
    ], [])

  @staticmethod
  def GenerateAsmReturnCommand(command, name, function_name, number):
    return sum([
        HackCodeGenerator._FromMemoryToMemory(
            HackCodeGenerator._SEGMENT_MAPPING["local"], 13),
        HackCodeGenerator._FromMemoryToD(13),
        HackCodeGenerator._AddConstantToD(-5),
        HackCodeGenerator._FromMemoryDToD(),
        HackCodeGenerator._FromDToMemory(14),
        HackCodeGenerator._PopToD(),
        HackCodeGenerator._FromDToMemoryIndirect(
            HackCodeGenerator._SEGMENT_MAPPING["argument"]),
        HackCodeGenerator._FromMemoryToD(
            HackCodeGenerator._SEGMENT_MAPPING["argument"]),
        HackCodeGenerator._AddConstantToD(1),
        HackCodeGenerator._FromDToMemory(
            HackCodeGenerator._SEGMENT_MAPPING["sp"]),
        HackCodeGenerator._FromMemoryToD(13),
        HackCodeGenerator._AddConstantToD(-1),
        HackCodeGenerator._FromMemoryDToD(),
        HackCodeGenerator._FromDToMemory(
            HackCodeGenerator._SEGMENT_MAPPING["that"]),
         HackCodeGenerator._FromMemoryToD(13),
        HackCodeGenerator._AddConstantToD(-2),
        HackCodeGenerator._FromMemoryDToD(),
        HackCodeGenerator._FromDToMemory(
            HackCodeGenerator._SEGMENT_MAPPING["this"]),
         HackCodeGenerator._FromMemoryToD(13),
        HackCodeGenerator._AddConstantToD(-3),
        HackCodeGenerator._FromMemoryDToD(),
        HackCodeGenerator._FromDToMemory(
            HackCodeGenerator._SEGMENT_MAPPING["argument"]),
         HackCodeGenerator._FromMemoryToD(13),
        HackCodeGenerator._AddConstantToD(-4),
        HackCodeGenerator._FromMemoryDToD(),
        HackCodeGenerator._FromDToMemory(
            HackCodeGenerator._SEGMENT_MAPPING["local"]),
        HackCodeGenerator._GotoLocationFromMemory(14)
    ], [])

  @staticmethod
  def GenerateAsmEmptyCommand(command, name, function_name, number):
    return []

  @staticmethod
  def GenerateBootstrapAsm():
    return sum([
        [
            "@256",
            "D=A",
            "@0",
            "M=D"
        ],
        HackCodeGenerator.GenerateAsmCallCommand(
            CallCommand("Sys.init", 0), "Sys", "", 1000000)
    ], [])

  @staticmethod
  def _ApplyBinaryTemplate(op):
    return [
        "@SP",
        "M=M-1",
        "A=M",
        "D=M",
        "A=A-1",
        "M=D%sM" % (op,) if op != "-" else "M=M-D"
    ]

  @staticmethod
  def _ApplyUnaryTemplate(op):
    return [
        "@SP",
        "A=M",
        "A=A-1",
        "M=%sM" % (op,)
    ]

  @staticmethod
  def _ApplyComparisonTemplate(op, name, number):
    branch_label = "%s$%d$branch" % (name, number)
    end_label = "%s$%d$end" % (name, number)
    return [
        "@SP",
        "M=M-1",
        "A=M",
        "D=M",
        "A=A-1",
        "D=D-M",
        "@%s" % (branch_label,),
        "D;%s" % (op,),
        "@SP",
        "A=M-1",
        "M=0",
        "@%s" % (end_label,),
        "0;JMP",
        "(%s)" % (branch_label,),
        "@SP",
        "A=M-1",
        "M=0",
        "M=!M",
        "(%s)" % (end_label,)
    ]

  @staticmethod
  def _ApplyPushTemplate():
    return [
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1"
    ]

  @staticmethod
  def _ApplyPushConstantTemplate(value):
    return [
        "@%d" % (value,),
        "D=A"
    ] + HackCodeGenerator._ApplyPushTemplate()

  @staticmethod
  def _ApplyPushDirectTemplate(value):
    return [
        "@" + str(value),
        "D=M"
    ] + HackCodeGenerator._ApplyPushTemplate()

  @staticmethod
  def _ApplyPushIndirectTemplate(segment_base, index):
    return [
        "@%d" % (segment_base,),
        "D=M",
        "@%d" % (index,),
        "A=D+A",
        "D=M"
    ] + HackCodeGenerator._ApplyPushTemplate()

  @staticmethod
  def _ApplyPopDirectTemplate(value):
    return [
        "@SP",
        "M=M-1",
        "A=M",
        "D=M",
        "@" + str(value),
        "M=D"
    ]

  @staticmethod
  def _ApplyPopIndirectTemplate(segment_base, index):
    return [
        "@%d" % (segment_base,),
        "D=M",
        "@%d" % (index,),
        "D=D+A",
        "@13",
        "M=D",
        "@SP",
        "M=M-1",
        "A=M",
        "D=M",
        "@13",
        "A=M",
        "M=D"
    ]

  @staticmethod
  def _FromMemoryToD(address):
    return [
        "@" + str(address),
        "D=M"
    ]

  @staticmethod
  def _FromMemoryDToD():
    return [
        "A=D",
        "D=M"
    ]

  @staticmethod
  def _FromDToMemory(address):
    return [
        "@" + str(address),
        "M=D"
    ]

  @staticmethod
  def _FromDToMemoryIndirect(address):
    return [
        "@" + str(address),
        "A=M",
        "M=D"
    ]

  @staticmethod
  def _FromMemoryToMemory(from_address, to_address):
    return sum([
        HackCodeGenerator._FromMemoryToD(from_address),
        HackCodeGenerator._FromDToMemory(to_address)
    ], [])

  @staticmethod
  def _AddConstantToD(constant):
    op = "+"
    if constant < 0:
      op = "-"
      constant = -constant
    
    return [
        "@%d" % (constant,),
        "D=D%sA" % (op,)
    ]

  @staticmethod
  def _PopToD():
    return [
        "@SP",
        "M=M-1",
        "A=M",
        "D=M"
    ]

  @staticmethod
  def _PushConstant(constant):
    return [
        "@" + str(constant),
        "D=A",
        "@SP",
        "M=M+1",
        "A=M-1",
        "M=D"
    ]

  @staticmethod
  def _PushFromMemory(address):
    return sum([
        HackCodeGenerator._FromMemoryToD(address),
        [
            "@SP",
            "M=M+1",
            "A=M-1",
            "M=D"
        ]
    ], [])

  @staticmethod
  def _CreateLabel(label_name):
    return ["(" + str(label_name) + ")"]

  @staticmethod
  def _GotoLabel(label_name):
    return [
        "@" + str(label_name),
        "0;JMP"
    ]

  @staticmethod
  def _GotoLocationFromMemory(address):
    return [
        "@" + str(address),
        "A=M",
        "0;JMP"
    ]


def ParseProgram(program_lines, program_name):
  """Transforms the lines of a VM program to a list of parsed commands.

  Args:
    program_line: A list of strings with the VM program.
    program_name: the name of the file containing the program.

  Returns:
    A list of parsed commands.

  Raises:
    VMError: If parsing results in an ErrorCommand.
  """
  program_commands = map(HackParser.ParseCommand, program_lines)
  
  errors = []
  for line_number in range(len(program_commands)):
    command = program_commands[line_number]
    if command.__class__.__name__ == "ErrorCommand":
      errors.append(
          "%s.%d: %s" % (program_name, line_number + 1, command.line))

  if len(errors) > 0:
    raise VMError("Error: " + os.linesep.join(errors))
  else:
    return program_commands


def IdentifyParentFunctions(program_commands):
  """Returns a list of enclosing functions for the program_commands.

  Args:
    program_commands: A list of command type instances.

  Returns:
    A list of strings with one element for each element of program_commands.
    This element is the name of the enclosing function for the command.
  """
  parent_functions = []
  current_function = "DEFAULT_FUNCTION"
  for command in program_commands:
    if command.__class__.__name__ == "FunctionCommand":
      current_function = command.function_name
    parent_functions.append(current_function)
  return parent_functions


def DecorateCommands(program_commands, program_name):
  """Decorates a list of program commands.

  Args:
    program_commands: A list of command type instances.
    program_name: The name of the file containing the commands.

  Returns:
    A list of (command, program_name, enclosing_function, line_number) tuples.
  """
  return zip(
      program_commands,
      [program_name] * len(program_commands),
      IdentifyParentFunctions(program_commands),
      range(len(program_commands)))


def GenerateAsm(decorated_program_commands):
  """Transforms the command list into a list of assembly instruction lists.

  Args:
    decorated_program_commands: A list of (command, program_name,
        enclosing_function, line_number) tuples.

  Returns:
    A list of lists containing Hack assembly instruction strings.
  """
  return map(
      lambda c: HackCodeGenerator.GenerateAsm(c[0], c[1], c[2], c[3]),
      decorated_program_commands)


def FlattenAsm(asm_chunks):
  """Flattens a list of lists with Hack assembly instructions.

  Args:
    asm_chunks: A list of lists with Hack assembly instruction strings.

  Returns:
    A list of Hack assembly instruction strings.
  """
  return sum(asm_chunks, [])


def AssembleProgram(program_lines, program_name):
  """Transforms the lines of a VM program into a list of assembly instructions.

  Args:
    program_lines: A list of strings representing the lines of a VM program.
    program_name: The name of the file that contains the program.

  Returns:
    A list of Hack assembly instruction strings.
  """
  return FlattenAsm(
      GenerateAsm(
          DecorateCommands(
              ParseProgram(program_lines, program_name),
              program_name)))


def LinkPrograms(programs):
  """Transforms a list of VM programs into a single Hack assembly stream.

  Args:
    programs: A list of Hack VM programs. A Hack VM program is a
        (program_name, program_lines) tuple, with program_name being the
        name of the program and program_lines being a list of strings
        with the programs commands.

  Returns:
    A list of Hack assembly instruction strings.
  """
  return sum(
      map(lambda p: AssembleProgram(p[1], p[0]), programs),
      [])


def AttachBootstrapCode(program_asm):
  """Attaches a bootstrap header to a list of Hack assembly instructions.

  Args:
    program_asm: A list of Hack assembly strings.

  Returns:
    A list of Hack assembly strings with a bootstrap header.
  """
  return sum([HackCodeGenerator.GenerateBootstrapAsm(), program_asm], [])


def main():
  if len(sys.argv) != 2:
    print "Please enter a file or directory."
    return

  programs = []
  if os.path.isfile(sys.argv[1]):
    if sys.argv[1].endswith(".vm"):
      try:
        with open(sys.argv[1], "r") as program_file:
          program_lines = program_file.readlines()
          programs.append((sys.argv[1][:-3], program_lines))
      except IOError as error:
        print error.message
  elif os.path.isdir(sys.argv[1]):
    for file_name in os.listdir(sys.argv[1]):
      if file_name.endswith(".vm"):
        try:
          with open(file_name, "r") as program_file:
            program_lines = program_file.readlines()
            programs.append((file_name[:-3], program_lines))
        except IOError as error:
          print error.message

  try:
    program_asm = AttachBootstrapCode(LinkPrograms(programs))
    with open("out.asm", "w") as asm_file:
      asm_file.write(os.linesep.join(program_asm))
  except VMError as error:
    print error.message
  except IOError as error:
    print error.message


if __name__ == "__main__":
  main()

