#ifndef  CSPLINE_H

void  splie2( float x1a[], float x2a[], float **ya, int m, int n, float **y2a);
void  splin2( float x1a[], float x2a[], float **ya, float **y2a, int m, int n, 
              float x1, float x2, float *y);
float quickSpline(float x[], float y[], const int n,float xpt,int wrap);
float quickSpline2(float xs1[],float xs2[],float x1,float x2,float p[19][19]);
float quickSpline3(float xs1[],float xs2[],float x1,float x2,float **p);

#define   CSPLINE_H

#endif
