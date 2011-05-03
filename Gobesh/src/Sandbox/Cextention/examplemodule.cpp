#include "/Developer/SDKs/MacOSX10.5.sdk/System/Library/Frameworks/Python.framework/Versions/2.5/include/python2.5/Python.h"

/* The module doc string */
PyDoc_STRVAR(example__doc__,
"Example c++ extention");

/* The function doc string */
PyDoc_STRVAR(first_function__doc__,
"The doc string");

/* The wrapper to the underlying C function */
static PyObject *
py_first_function(PyObject *self, PyObject *args)
{
	double x=0, y=0;
	int iterations, max_iterations=1000;
	/* "args" must have two doubles and may have an integer */
	/* If not specified, "max_iterations" remains unchanged; defaults to 1000 */
	/* The ':iterate_point' is for error messages */
	if (!PyArg_ParseTuple(args, "dd|i:first_function", &x, &y, &max_iterations))
		return NULL;
	/* Verify the parameters are correct */
	if (max_iterations < 0) max_iterations = 0;

	/* Call the C function */
	iterations = max_iterations;

	/* Convert from a C integer value to a Python integer instance */
	return PyInt_FromLong((long) iterations);
}

/* A list of all the methods defined by this module. */
/* "iterate_point" is the name seen inside of Python */
/* "py_iterate_point" is the name of the C function handling the Python call */
/* "METH_VARGS" tells Python how to call the handler */
/* The {NULL, NULL} entry indicates the end of the method definitions */
static PyMethodDef example_methods[] = {
	{"first_function",  py_first_function, METH_VARARGS, first_function__doc__},
	{NULL, NULL}      /* sentinel */
};

/* When Python imports a C module named 'X' it loads the module */
/* then looks for a method named "init"+X and calls it.  Hence */
/* for the module "mandelbrot" the initialization function is */
/* "initmandelbrot".  The PyMODINIT_FUNC helps with portability */
/* across operating systems and between C and C++ compilers */
PyMODINIT_FUNC
initexample(void)
{
	/* There have been several InitModule functions over time */
	Py_InitModule3("example", example_methods,
                   example__doc__);
}
