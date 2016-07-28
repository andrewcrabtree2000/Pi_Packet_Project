#!/usr/bin/env python

import time
from Adafruit_CharLCD import *

# A wrapper around the Adafruit LCD library. This extends the functionality to
# allow for easy and generic input that can be reused.
class LCD_Input_Wrapper(Adafruit_CharLCDPlate):

   # Before enums were introduced in Python, this was one such method of 
   # 'faking' an enum. It takes a list of identifiers, zips it from 0..n-1,
   # where n is the number of identifiers passed in, and uses the type 
   # function to generate a new class with the aforementioned identifiers as
   # class variables.
   def enums(*sequential):
      enums = dict(zip(sequential, range(len(sequential))))
      return type('Enum', (), enums)

   Input_Type = enums('Char', 'Int', 'Hex')

   Value_Types = ( (Input_Type.Int, 'i', '0123456789'),
                   (Input_Type.Hex, 'h', '0123456789abcdef') )

   def get_value_tuple(self, key):
      for i in self.Value_Types:
         if key in i:
            return i
      return None

   class Input_Char(object):
      value = ' '
      value_type = ''

   def _inc_or_dec(self, value, value_type, delta):
      values_array = self.get_value_tuple(value_type)[2]
      index = (values_array.index(value) + delta) % len(values_array)
      return values_array[index]

   def increment(self, value):
      return self._inc_or_dec(value.value, value.value_type, 1)

   def decrement(self, value):
      return self._inc_or_dec(value.value, value.value_type, -1)

   def parse_identifier(self, input_format):
      char_type = self.Input_Char()
      advances = 0
      try:
         char_type.value_type = self.get_value_tuple(input_format[1])[0]
         char_type.value = '0'
      except (TypeError):
         print 'Cannot parse format; unknown identifier after "%"'
         char_type.value_type = self.Input_Type.Char
         char_type.value = input_format[0]
      return (2, char_type)

   def parse_char(self, input_format):
      char_type = self.Input_Char()
      advances = 0
      if input_format[0] == '%':
         advances, char_type = self.parse_identifier(input_format)
      else:
         char_type.value_type = self.Input_Type.Char
         char_type.value = input_format[0]
         advances = 1
      return (advances, char_type)
   
   def _find_input(self, list_chars, index, delta):
      for i in list_chars[(index+delta) % len(list_chars)::delta]:
         if i.value_type != self.Input_Type.Char:
            return list_chars.index(i)
      return self._find_input(list_chars, len(list_chars), delta)
   
   def find_previous_input(self, list_chars, index):
      return self._find_input(list_chars, index, -1)
   
   def find_next_input(self, list_chars, index):
      return self._find_input(list_chars, index, 1)
  
   def get_input_list(self, list_vals):
      index = 0;
      self.blink(False)
      self.clear()
      self.message(list_vals[index])
      while True:
         time.sleep(0.15)
         if self.is_pressed(UP):
            index = ((index + 1) % len(list_vals))
         elif self.is_pressed(DOWN):
            index = ((index - 1) % len(list_vals))
         elif self.is_pressed(SELECT):
            break
         else:
            continue
         self.clear()
         self.message(list_vals[index])
      return list_vals[index] 

   def get_input_format(self, lcd_format, default=''):
      list_chars = []
      i = 0
      while i < len(lcd_format):
         advance, char = self.parse_char(lcd_format[i:i+2])
         i += advance
         list_chars.append(char)

      if default != '':
         i = 0
         cur_default = 0
         while i < len(list_chars):
            cur_value_type = list_chars[i].value_type
            try:
               index = [val[0] for val in self.Value_Types].index(cur_value_type)
               if default[cur_default] in self.Value_Types[index][2]:
                  list_chars[i].value = default[cur_default]
                  i += 1
               cur_default += 1
            except (ValueError):
               i += 1

      index = self.find_next_input(list_chars, -1)
      if index == -1:
         print 'Enter a format, dummy'
         return ''
   
      index_newline = -1
      for i in xrange(len(list_chars)):
         if list_chars[i].value == '\n':
            index_newline = i
            break
   
      self.clear()
      self.message(''.join([x.value for x in list_chars]))
   
      self.blink(True)

      row = 0

      # TODO: Make this a function
      cursor_index = index
      if index_newline != -1 and index >= index_newline:
         cursor_index -= index_newline + 1
         row = 1
      elif index_newline != -1:
         row = 0
      self.set_cursor(cursor_index, row)

      while True:
         time.sleep(0.15)
         if self.is_pressed(UP):
            list_chars[index].value = self.increment(list_chars[index])
         elif self.is_pressed(DOWN):
            list_chars[index].value = self.decrement(list_chars[index])
         elif self.is_pressed(LEFT):
            index = self.find_previous_input(list_chars, index)
         elif self.is_pressed(RIGHT):
            index = self.find_next_input(list_chars, index)
         elif self.is_pressed(SELECT):
            break
         else:
            continue
         self.clear()
         self.message(''.join([x.value for x in list_chars]))
         cursor_index = index
         if index_newline != -1 and index >= index_newline:
            cursor_index -= index_newline + 1
            row = 1
         elif index_newline != -1:
            row = 0
         self.set_cursor(cursor_index, row)
      return ''.join([x.value for x in list_chars])