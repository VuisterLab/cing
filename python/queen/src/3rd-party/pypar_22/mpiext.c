/************************************************************************/
/* PyPAR - Parallel Python using MPI                 	                */
/* Copyright (C) 2001, 2002, 2003 Ole M. Nielsen                        */
/*                                                                      */
/* See enclosed README file for details of installation and use.   	*/
/*                                                                 	*/   
/* This program is free software; you can redistribute it and/or modify */
/* it under the terms of the GNU General Public License as published by */
/* the Free Software Foundation; either version 2 of the License, or    */
/* (at your option) any later version.                                  */
/*                                                                      */     
/* This program is distributed in the hope that it will be useful,      */
/* but WITHOUT ANY WARRANTY; without even the implied warranty of       */
/* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        */
/* GNU General Public License (http://www.gnu.org/copyleft/gpl.html)    */
/* for more details.                                                    */
/*                                                                      */
/* You should have received a copy of the GNU General Public License    */
/* along with this program; if not, write to the Free Software          */
/*  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*/
/*                                                                      */
/*                                                                 	*/
/* Contact addresses: Ole.Nielsen@anu.edu.au, gp.ciceri@acm.org         */
/*                                                                 	*/
/* version (see __version__ in pypar.py)                                */
/************************************************************************/


#include "Python.h"
#include "mpi.h"
#include "Numeric/arrayobject.h"

// to handle MPI constants export (shamelessly stolen from _cursesmodule.c)
#define SetDictInt(string,ch) \
        PyDict_SetItemString(ModDict, string, PyInt_FromLong((long) (ch)));

// Remap struct MPI_op to int (easier to handle by python)
#define MAX 1
#define MIN 2
#define SUM 3
#define PROD 4
#define LAND 5
#define BAND 6
#define LOR 7
#define BOR 8
#define LXOR 9
#define BXOR 10
#define MAXLOC 11
#define MINLOC 12
//#define REPLACE 13 // Not available on all MPI systems

MPI_Datatype type_map(PyArrayObject *x) {  

  //
  // TYPE    py_type  mpi_type  bytes  symbol
  // ---------------------------------------- 
  // INT       4        6         4      'i'
  // LONG      5        8         8      'l'
  // FLOAT     6       10         4      'f'  
  // DOUBLE    7       11         8      'd'
  
  
  int py_type;
  MPI_Datatype mpi_type;
  
  if (x -> nd != 1) {
    PyErr_SetString(PyExc_ValueError, "Array must be 1 dimensional");
    return (MPI_Datatype) 0;
  }      
      
  py_type = x -> descr -> type_num;     
  if (py_type == PyArray_DOUBLE) 
    mpi_type = MPI_DOUBLE;
  else if (py_type == PyArray_LONG)   
    mpi_type = MPI_LONG;  
  else if (py_type == PyArray_FLOAT) 
    mpi_type = MPI_FLOAT;
  else if (py_type == PyArray_INT) 
    mpi_type = MPI_INT;
  else {
    PyErr_SetString(PyExc_ValueError, "Array must be of type int or float");
    return 0;
  }      

  //printf("Types %d %d\n", py_type, mpi_type);
  
  return mpi_type;
}    

MPI_Op op_map(int py_op) {  
  
  MPI_Op mpi_op;
  
  if (py_op == MAX) 
    mpi_op = MPI_MAX;
  else if (py_op == MIN)   
    mpi_op = MPI_MIN;  
  else if (py_op == SUM)   
    mpi_op = MPI_SUM;  
  else if (py_op == PROD)   
    mpi_op = MPI_PROD;  
  else if (py_op == LAND)   
    mpi_op = MPI_LAND;  
  else if (py_op == BAND)   
    mpi_op = MPI_BAND;  
  else if (py_op == LOR)   
    mpi_op = MPI_LOR;  
  else if (py_op == BOR)   
    mpi_op = MPI_BOR;  
  else if (py_op == LXOR)   
    mpi_op = MPI_LXOR;  
  else if (py_op == BXOR)   
    mpi_op = MPI_BXOR;  
  else if (py_op == MAXLOC)
    mpi_op = MPI_MAXLOC;
  else if (py_op == MINLOC)   
    mpi_op = MPI_MINLOC;  
  //else if (py_op == REPLACE)   
  //  mpi_op = MPI_REPLACE;  
  else {
    PyErr_SetString(PyExc_ValueError, "Operation unknown");
    return 0;
  }      

  //printf("Op: %d.\n", py_op);
  
  return mpi_op;
}  


/*********************************************************/
/* send_string                                           */
/* Send string of characters                             */
/*                                                       */
/*********************************************************/
static PyObject *send_string(PyObject *self, PyObject *args) {
  char *s;
  int destination, tag, length, err;
 
  /* process the parameters */
  if (!PyArg_ParseTuple(args, "s#ii", &s, &length, &destination, &tag))
    return NULL;
  
  /* call the MPI routine */
  err = MPI_Send(s, length, MPI_CHAR, destination, tag, MPI_COMM_WORLD);

  return Py_BuildValue("i", err);
}

/**********************************************************/
/* receive_string                                         */
/* Receive string of characters                           */
/*                                                        */
/**********************************************************/
static PyObject *receive_string(PyObject *self, PyObject *args) {
  char *s;
  int source, tag, length, err, st_length; 
  MPI_Status status;

  /* process the parameters */
  if (!PyArg_ParseTuple(args, "s#ii", &s, &length, &source, &tag))
    return NULL;
    
  /* call the MPI routine */
  err = MPI_Recv(s, length, MPI_CHAR, source, tag, MPI_COMM_WORLD, &status);
   
  MPI_Get_count(&status, MPI_CHAR, &st_length); 
  // status.st_length is not available in all MPI implementations
  //Alternative is: MPI_Get_elements(MPI_Status *, MPI_Datatype, int *);

  return Py_BuildValue("i(iiiii)", err, status.MPI_SOURCE, status.MPI_TAG,
  status.MPI_ERROR, st_length, sizeof(char));  
}

/**********************************************************/
/* bcast_string                                           */
/* Broadcast string of characters                         */
/*                                                        */
/**********************************************************/
static PyObject *bcast_string(PyObject *self, PyObject *args) {
  char *s;
  int source, length, err; 

  /* process the parameters */
  if (!PyArg_ParseTuple(args, "s#i", &s, &length, &source))
    return NULL;
    
  /* call the MPI routine */
  err = MPI_Bcast(s, length, MPI_CHAR, source, MPI_COMM_WORLD);
   
  return Py_BuildValue("i", err);  
}

/**********************************************************/
/* scatter_string                                         */
/* Scatter string of characters                           */
/*                                                        */
/**********************************************************/
static PyObject *scatter_string(PyObject *self, PyObject *args) {
  char *s;
  char *d;
  int source, length, err; 

  /* process the parameters */
  if (!PyArg_ParseTuple(args, "sisi", &s, &length, &d, &source))
    return NULL;
    
  /* call the MPI routine */
  err = MPI_Scatter(s, length, MPI_CHAR, d, length,  MPI_CHAR, source, MPI_COMM_WORLD);
   
  return Py_BuildValue("i", err);  
}

/**********************************************************/
/* gather_string                                         */
/* Gather string of characters                           */
/*                                                        */
/**********************************************************/
static PyObject *gather_string(PyObject *self, PyObject *args) {
  char *s;
  char *d;
  int source, length, err; 

  /* process the parameters */
  if (!PyArg_ParseTuple(args, "sisi", &s, &length, &d, &source))
    return NULL;
    
  /* call the MPI routine */
  err = MPI_Gather(s, length, MPI_CHAR, d, length,  MPI_CHAR, source, MPI_COMM_WORLD);
   
  return Py_BuildValue("i", err);  
}


/**********************************************************/
/* send_array                                             */
/* Send Numeric array of type float, double, int, or long */
/*                                                        */
/**********************************************************/
static PyObject *send_array(PyObject *self, PyObject *args) {
  PyObject *input;
  PyArrayObject *x;
  int destination, tag, err;
  MPI_Datatype mpi_type;
  
  /* process the parameters */
  if (!PyArg_ParseTuple(args, "Oii", &input, &destination, &tag))
    return NULL;
    
  /* Make Numeric array from general sequence type (no cost if already Numeric)*/    
  x = (PyArrayObject *)
    PyArray_ContiguousFromObject(input, PyArray_NOTYPE, 0, 0);
    
  /* Input check and determination of MPI type */          
  mpi_type = type_map(x);
  if (!mpi_type) return NULL;
    
  /* call the MPI routine */
  err = MPI_Send(x->data, x->dimensions[0], mpi_type, destination, tag,\
           MPI_COMM_WORLD);
	   
  Py_DECREF(x); 	   
	   
  return Py_BuildValue("i", err);
}

/*************************************************************/
/* receive_array                                             */
/* Receive Numeric array of type float, double, int, or long */
/*                                                           */
/*************************************************************/
static PyObject *receive_array(PyObject *self, PyObject *args) {
  PyArrayObject *x;
  int source, tag, err, st_length, size;
  MPI_Datatype mpi_type;
  MPI_Status status;

  /* process the parameters */
  if (!PyArg_ParseTuple(args, "Oii", &x, &source, &tag))
    return NULL;

  /* Input check and determination of MPI type */          
  mpi_type = type_map(x);
  if (!mpi_type) return NULL;  
      
  /* call the MPI routine */
  err =  MPI_Recv(x->data, x->dimensions[0], mpi_type, source, tag, \
         MPI_COMM_WORLD, &status);
	 
  MPI_Get_count(&status, mpi_type, &st_length); 
  // status.st_length is not available in all MPI implementations
  //Alternative is: MPI_Get_elements(MPI_Status *, MPI_Datatype, int *);
	 
      
  if ((mpi_type == MPI_DOUBLE) | (mpi_type == MPI_LONG)) {
    size = 8;
  } else {
    size = 4;
  }
    
  return Py_BuildValue("i(iiiii)", err, status.MPI_SOURCE, status.MPI_TAG,
  status.MPI_ERROR, st_length, size);  
}


/*************************************************************/
/* bcast_array                                               */
/* Broadcast Num.  array of type float, double, int, or long */
/*                                                           */
/*************************************************************/
static PyObject *bcast_array(PyObject *self, PyObject *args) {
  PyArrayObject *x;
  int source, err;
  MPI_Datatype mpi_type;
  //MPI_Status status;

  /* process the parameters */
  if (!PyArg_ParseTuple(args, "Oi", &x, &source))
    return NULL;

  /* Input check and determination of MPI type */          
  mpi_type = type_map(x);
  if (!mpi_type) return NULL;  
      
  /* call the MPI routine */
  err =  MPI_Bcast(x->data, x->dimensions[0], mpi_type, source, \
         MPI_COMM_WORLD);
      
  return Py_BuildValue("i", err);
}

/*************************************************************/
/* scatter_array                                             */
/* Scatter Num.    array of type float, double, int, or long */
/*                                                           */
/*************************************************************/
static PyObject *scatter_array(PyObject *self, PyObject *args) {
  PyArrayObject *x;
  PyArrayObject *d;
  int length, source, err;
  MPI_Datatype mpi_type;
  //MPI_Status status;

  /* process the parameters */
  if (!PyArg_ParseTuple(args, "OiOi", &x, &length, &d, &source))
    return NULL;

  /* Input check and determination of MPI type */          
  mpi_type = type_map(x);
  if (!mpi_type) return NULL;  
      
  /* call the MPI routine */
  err =  MPI_Scatter(x->data, length, mpi_type, d->data, length, mpi_type, source, \
         MPI_COMM_WORLD);
      
  return Py_BuildValue("i", err);
}


/*************************************************************/
/* gather_array                                              */
/* Gather Num.     array of type float, double, int, or long */
/*                                                           */
/*************************************************************/
static PyObject *gather_array(PyObject *self, PyObject *args) {
  PyArrayObject *x;
  PyArrayObject *d;
  int length, source, err;
  MPI_Datatype mpi_type;
  //MPI_Status status;

  /* process the parameters */
  if (!PyArg_ParseTuple(args, "OiOi", &x, &length, &d, &source))
    return NULL;

  /* Input check and determination of MPI type */          
  mpi_type = type_map(x);
  if (!mpi_type) return NULL;  
      
  /* call the MPI routine */
  err =  MPI_Gather(x->data, length, mpi_type, d->data, length, mpi_type, source, \
         MPI_COMM_WORLD);
      
  return Py_BuildValue("i", err);
}



/*************************************************************/
/* reduce_array                                              */
/* Reduce Num.     array of type float, double, int, or long */
/*                                                           */
/*************************************************************/
static PyObject *reduce_array(PyObject *self, PyObject *args) {
  PyArrayObject *x;
  PyArrayObject *d;
  int length, source, op, err;
  MPI_Datatype mpi_type;
  //MPI_Status status;
  MPI_Op mpi_op;

  /* process the parameters */
  if (!PyArg_ParseTuple(args, "OOiii", &x, &d, &length, &op, &source))
    return NULL;
   
  /* Input check and determination of MPI type */          
  mpi_type = type_map(x);
  if (!mpi_type) return NULL;  
  if (mpi_type != type_map(d)) {
    printf ("Input array and buffer must be of the same type\n");
    return Py_BuildValue("i", -666);    
  }
  
  /* Input check and determination of MPI op */ 
  //printf("op: %d\n", op);         
  mpi_op = op_map(op);
  if (!mpi_op) return NULL;  
   
         
  if (op == MAXLOC || op == MINLOC) {
    //not implemented
    return Py_BuildValue("i", -666);
  }
  else {
  /* call the MPI routine */
  err =  MPI_Reduce(x->data, d->data, length, mpi_type, mpi_op, source, \
         MPI_COMM_WORLD);
  }
         
      
  return Py_BuildValue("i", err);
}

/*********************************************************/
/* MPI calls rank, size, finalize, abort                 */
/*                                                       */
/*********************************************************/

static PyObject * rank(PyObject *self, PyObject *args) {
  int myid;

  MPI_Comm_rank(MPI_COMM_WORLD,&myid);
  return Py_BuildValue("i", myid);
}

static PyObject * size(PyObject *self, PyObject *args) {
  int numprocs; 

  MPI_Comm_size(MPI_COMM_WORLD,&numprocs);
  return Py_BuildValue("i", numprocs);
}
  
static PyObject * Get_processor_name(PyObject *self, PyObject *args) {  
  char processor_name[MPI_MAX_PROCESSOR_NAME];
  int  namelen;

  MPI_Get_processor_name(processor_name,&namelen);
  return Py_BuildValue("s#", processor_name, namelen);
}   

static PyObject * init(PyObject *self, PyObject *args) {  
  PyObject *input;

  int i, error;
  int argc = 0;  
  char **argv;   

  /* process input parameters */
  if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &input))
    return NULL;

  /* Reconstruct C-commandline */     
  /*                           */ 
  argc = PyList_Size(input); //Number of commandline arguments
  argv = (char**) malloc(argc*sizeof(char*)); 
  
  for (i=0; i<argc; i++)  
    argv[i] = PyString_AsString( PyList_GetItem(input, i) );
  
  error = MPI_Init(&argc, &argv); 
  return Py_BuildValue("i", error);  
} 


static PyObject * Initialized(PyObject *self, PyObject *args) {  
  int error, flag;

  error = MPI_Initialized(&flag);
  
  //What should we do with error?
  return Py_BuildValue("i", flag);  
} 

  
static PyObject * Finalize(PyObject *self, PyObject *args) {  
  int error;

  error = MPI_Finalize();
  return Py_BuildValue("i", error);  
} 

static PyObject * Abort(PyObject *self, PyObject *args) {  
  int error, code=0;
  
  error = MPI_Abort(MPI_COMM_WORLD, code);
  return Py_BuildValue("i", error);  
} 

static PyObject * Barrier(PyObject *self, PyObject *args) {  
  int error;
  
  error = MPI_Barrier(MPI_COMM_WORLD);
  return Py_BuildValue("i", error);    
}    

static PyObject * Wtime(PyObject *self, PyObject *args) {     
  double t;
  
  t = MPI_Wtime();
  return Py_BuildValue("d", t);      
}     
 
/**********************************/
/* Method table for python module */
/**********************************/

static struct PyMethodDef MethodTable[] = {
  {"size", size, METH_VARARGS},  
  {"rank", rank, METH_VARARGS},  
  {"Barrier", Barrier, METH_VARARGS},          
  {"Wtime", Wtime, METH_VARARGS},            
  {"Get_processor_name", Get_processor_name, METH_VARARGS},              
  {"init", init, METH_VARARGS},          
  {"Initialized", Initialized, METH_VARARGS},       
  {"Finalize", Finalize, METH_VARARGS},        
  {"Abort", Abort, METH_VARARGS},          
  {"send_string", send_string, METH_VARARGS},
  {"receive_string", receive_string, METH_VARARGS},      
  {"bcast_string", bcast_string, METH_VARARGS},        
  {"scatter_string", scatter_string, METH_VARARGS},        
  {"gather_string", gather_string, METH_VARARGS},        
  {"send_array", send_array, METH_VARARGS},
  {"receive_array", receive_array, METH_VARARGS},    
  {"bcast_array", bcast_array, METH_VARARGS},              
  {"scatter_array", scatter_array, METH_VARARGS},              
  {"gather_array", gather_array, METH_VARARGS},              
  {"reduce_array", reduce_array, METH_VARARGS},              
  {NULL, NULL}
};


/***************************/
/* Module initialisation   */
/***************************/


void initmpiext(void){
  PyObject *m, *ModDict;
  
  m = Py_InitModule("mpiext", MethodTable);
  
  // to handle MPI symbolic constants
  ModDict = PyModule_GetDict(m); 
  SetDictInt("MPI_ANY_TAG", MPI_ANY_TAG);
  SetDictInt("MPI_ANY_SOURCE", MPI_ANY_SOURCE);
  SetDictInt("MAX", MAX);
  SetDictInt("MIN", MIN);
  SetDictInt("SUM", SUM);
  SetDictInt("PROD", PROD);
  SetDictInt("LAND", LAND);
  SetDictInt("BAND", BAND);
  SetDictInt("LOR", LOR);
  SetDictInt("BOR", BOR);
  SetDictInt("LXOR", LXOR);
  SetDictInt("BXOR", BXOR);
  //SetDictInt("MAXLOC", MAXLOC);
  //SetDictInt("MINLOC", MINLOC);
  //SetDictInt("REPLACE", REPLACE);

  
  //SetDictInt("MPI_COMM_WORLD", MPI_COMM_WORLD);  
   
  import_array();     //Necessary for handling of NumPY structures  
}

 
 

