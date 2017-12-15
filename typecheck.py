#!/usr/bin/env python3

import inspect
import functools

def optional_typecheck(function):
	"""
    Decorator type-checking *annotated* parameters and return values. Works with python 3.
    
        Some examples: (for excessive examples see the testsuite at the bottom)
    
		>>> import typecheck
		>>> @typecheck.optional_typecheck
		... def foo(bar: int) -> str:
		...     return "{}".format(bar)
		...
		>>> foo('a')
		Traceback (most recent call last):
		  File "<stdin>", line 1, in <module>
		  File "/home/dpiegdon/programming/pytypecheck/typecheck.py", line 56, in wrapper
			raise TypeError("Expected argument '{}' of type {} but got {}.".format(name, annotations[name], type(val)))
		TypeError: Expected argument 'bar' of type <class 'int'> but got <class 'str'>.
		>>> foo(1)
		'1'

		Annotations are optional. Where an annotation is missing,
		no typechecking is done.

    Authors:
        * David R. Piegdon

	License:
		The MIT License (MIT)
		Copyright (c) 2015, 2016, 2017 David R. Piegdon

		Permission is hereby granted, free of charge, to any person obtaining a
		copy of this software and associated documentation files (the
		"Software"), to deal in the Software without restriction, including
		without limitation the rights to use, copy, modify, merge, publish,
		distribute, sublicense, and/or sell copies of the Software, and to
		permit persons to whom the Software is furnished to do so, subject to
		the following conditions:

		The above copyright notice and this permission notice shall be included
		in all copies or substantial portions of the Software.

		THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
		OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
		MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
		IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
		CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
		TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
		SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

	Prior art and inspiration:
        * mypy     - an experimental optional static type checker for Python
		* pylint
        * pyflakes

	ChangeLog:
        2017-12-15 - added docs + testsuite for initial public release
                     after long internal use
    
    """
	annotations = function.__annotations__
	@functools.wraps(function)
	def wrapper(*args, **kwargs):
		# check parameters
		for name, val in inspect.getcallargs(function, *args, **kwargs).items():
			if name in annotations:
				if not isinstance(val, annotations[name]):
					raise TypeError("Expected argument '{}' of type {} but got {}.".format(name, annotations[name], type(val)))
		# call wrapped function
		result = function(*args, **kwargs)
		# check return value
		if "return" in annotations:
			if not isinstance(result, annotations["return"]):
				raise TypeError("Expected return of type {} but got {}.".format(annotations["return"], type(result)))
		# return result from wrapped function
		return result
	return wrapper



def _testsuite():
	### test decorator itself

	# test parameters
	@optional_typecheck
	def foo(x: int) -> str:
		return "{}".format(x)

	if "1" != foo(1):
		raise RuntimeError("bad return value for foo(1)")
	try:
		foo('a')
		raise RuntimeError("accepts str as int")
	except TypeError:
		pass

	# test return value
	@optional_typecheck
	def bar(x: int) -> int:
		return "badreturn"

	try:
		bar(1)
		raise RuntimeError("should always fail (with int)")
	except TypeError:
		pass
	try:
		bar('a')
		raise RuntimeError("should always fail (with str)")
	except TypeError:
		pass

	# test missing annotations
	@optional_typecheck
	def qux(x: int, y, z: int):
		return "{}{}{}".format(x, y, z)

	try:
		qux('a', 1, 2)
		raise RuntimeError("qux accepts str as int")
	except TypeError:
		pass
	a = qux(1, {'a': 2, 'b': [1,2,3], 'c': "qwer"}, 3)
	if "1{'a': 2, 'b': [1, 2, 3], 'c': 'qwer'}3" != a:
		raise RuntimeError("bad output for complex qux")

try:
	_testsuite()
except Exception:
	print("ERROR: typecheck testsuite failed:")
	raise

