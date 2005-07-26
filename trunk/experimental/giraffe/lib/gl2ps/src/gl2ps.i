%module gl2ps
%{
/* Includes the header in the wrapper code */
#include "gl2ps.h"
%}

/* Parse the header file to generate wrappers */

/* Type mapping for grabbing a FILE * from Python */
%typemap(python,in) FILE * {
  if (!PyFile_Check($input)) {
      PyErr_SetString(PyExc_TypeError, "Need a file!");
      return NULL;
  }
  $1 = PyFile_AsFile($input);
}

/* Grab a 4 element array as a Python 4-tuple */
%typemap(python,in) int[4](int temp[4]) {   /* temp[4] becomes a local variable */
  int i;
  if (PyTuple_Check($input)) {
    if (!PyArg_ParseTuple($input,"iiii",temp,temp+1,temp+2,temp+3)) {
      PyErr_SetString(PyExc_TypeError,"tuple must have 4 elements");
      return NULL;
    }
    $1 = &temp[0];
  } else {
    PyErr_SetString(PyExc_TypeError,"expected a tuple.");
    return NULL;
  }
}

%include "gl2ps.h"
