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
Test cases for the hack_vm module.
"""


__author__ = "Ivan Vladimirov Ivanov (ivan.vladimirov.ivanov@gmail.com)"


import unittest

import hack_vm

class TestHackVM(unittest.TestCase):

  def testParseCommand(self):
    for command in [
        "add",
        "sub",
        "neg",
        "eq",
        "gt",
        "lt",
        "and"]:
      result = hack_vm.HackParser.ParseCommand("add")
      self.assertTrue(result != False)

    result1 = hack_vm.HackParser.ParseCommand("push constant 13")
    self.assertTrue(result1 != False)
    self.assertTrue(result1.segment == "constant")
    self.assertTrue(result1.index == 13)

    result2 = hack_vm.HackParser.ParseCommand("pop local 42")
    self.assertTrue(result2 != False)
    self.assertTrue(result2.segment == "local")
    self.assertTrue(result2.index == 42)

    result3 = hack_vm.HackParser.ParseCommand("   pop  foo 2  //I like pie!")
    self.assertTrue(result3 != False)
    self.assertTrue(result3.__class__.__name__ == "ErrorCommand")

  def testParseProgram(self):
    self.assertRaises(
        hack_vm.VMError, hack_vm.ParseProgram, ["foo"], "foo")

  def testGenerateAsmBinary(self):
    result1 = hack_vm.HackCodeGenerator.GenerateAsm(
        hack_vm.AddCommand(), "foo", "bar", 1)
    self.assertTrue("M=D+M" in result1)

    result2 = hack_vm.HackCodeGenerator.GenerateAsm(
        hack_vm.SubCommand(), "foo", "bar", 2)
    self.assertTrue("M=M-D" in result2)

    result3 = hack_vm.HackCodeGenerator.GenerateAsm(
        hack_vm.AndCommand(), "foo", "bar", 3)
    self.assertTrue("M=D&M" in result3)

    result4 = hack_vm.HackCodeGenerator.GenerateAsm(
        hack_vm.OrCommand(), "foo", "bar", 4)
    self.assertTrue("M=D|M" in result4)

  def testGenerateAsmUnary(self):
    result1 = hack_vm.HackCodeGenerator.GenerateAsm(
        hack_vm.NegCommand(), "foo", "bar", 1)
    self.assertTrue("M=-M" in result1)

    result2 = hack_vm.HackCodeGenerator.GenerateAsm(
        hack_vm.NotCommand(), "foo", "bar", 2)
    self.assertTrue("M=!M" in result2)

  def testGenerateAsmComparison(self):
    result1 = hack_vm.HackCodeGenerator.GenerateAsm(
        hack_vm.EqCommand(), "foo", "bar", 1)
    self.assertTrue("@foo$1$branch" in result1)
    self.assertTrue("@foo$1$end" in result1)
    self.assertTrue("(foo$1$branch)" in result1)
    self.assertTrue("(foo$1$end)" in result1)
    self.assertTrue("D;JEQ")
    
    result2 = hack_vm.HackCodeGenerator.GenerateAsm(
        hack_vm.GtCommand(), "foo", "bar", 2)
    self.assertTrue("@foo$2$branch" in result2)
    self.assertTrue("@foo$2$end" in result2)
    self.assertTrue("(foo$2$branch)" in result2)
    self.assertTrue("(foo$2$end)" in result2)
    self.assertTrue("D;JLT")

    result3 = hack_vm.HackCodeGenerator.GenerateAsm(
        hack_vm.LtCommand(), "foo", "bar", 3)
    self.assertTrue("@foo$3$branch" in result3)
    self.assertTrue("@foo$3$end" in result3)
    self.assertTrue("(foo$3$branch)" in result3)
    self.assertTrue("(foo$3$end)" in result3)
    self.assertTrue("D;JGT")

  def testGenerateAsmPush(self):
    result1 = hack_vm.HackCodeGenerator.GenerateAsm(
        hack_vm.PushCommand("constant", 42), "foo", "bar", 1)
    self.assertTrue("@42" in result1)

    result2 = hack_vm.HackCodeGenerator.GenerateAsm(
        hack_vm.PushCommand("temp", 2), "foo", "bar", 2)
    self.assertTrue("@7" in result2)

    result3 = hack_vm.HackCodeGenerator.GenerateAsm(
        hack_vm.PushCommand("local", 42), "foo", "bar", 3)
    self.assertTrue("@1" in result3)
    self.assertTrue("@42" in result3)

    result4 = hack_vm.HackCodeGenerator.GenerateAsm(
        hack_vm.PushCommand("static", 42), "foo", "bar", 4)
    self.assertTrue("@foo.42" in result4)

  def testGenerateAsmPop(self):
    result1 = hack_vm.HackCodeGenerator.GenerateAsm(
        hack_vm.PopCommand("pointer", 42), "foo", "bar", 1)
    self.assertTrue("@45" in result1)

    result2 = hack_vm.HackCodeGenerator.GenerateAsm(
        hack_vm.PopCommand("argument", 42), "foo", "bar", 2)
    self.assertTrue("@2" in result2)
    self.assertTrue("@42" in result2)

    result3 = hack_vm.HackCodeGenerator.GenerateAsm(
        hack_vm.PopCommand("static", 42), "foo", "bar", 3)
    self.assertTrue("@foo.42" in result3)


if __name__ == "__main__":
  unittest.main()

