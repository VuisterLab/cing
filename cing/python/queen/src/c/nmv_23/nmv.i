 /* example.i */
%module nmv
%{
/* Put header files here (optional) */
%}

extern void  initialize_matrix();
extern void  clear_matrix();
extern void  free_memory();
extern int   xplor_read(char *filename);
extern int   eflag;
extern float uncertainty(int iatom, int jatom);
extern float atom_uncertainty(int iatom);
extern float total_uncertainty();
extern float lower_bound(int iatom, int jatom);
extern float upper_bound(int iatom, int jatom);
