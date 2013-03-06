#ifndef DISPLAY_H

#ifndef CS_H
#include "cs.h"
#endif

typedef struct DISPLAY_DATA
{
  int     length;
  int     properties;
  int     nucleus;
  int     fill;
  int     *num;
  char    *res;
  char    **label;
  float   **cs;
} DISPLAY_DATA;

DISPLAY_DATA  *CreateDisplayData( int len, int prop, int nuc );
void           display_selected_nucleus( DISPLAY_DATA *d );
void           FreeDisplayData( DISPLAY_DATA *d );
void           InitializeDisplayData( DISPLAY_DATA *d, CSHIFT *cs, char *label );
void           FillDisplayData( DISPLAY_DATA *d, CSHIFT *cs, char *label, int t );
void           FillDisplayDataHB( DISPLAY_DATA *d, CSHIFT *cs );
void           FillDisplayDataCYS( DISPLAY_DATA *d, CSHIFT *orig, CSHIFT *ss );
void           FillDisplayDataPRO( DISPLAY_DATA *d, RES *pro );
void           FillDisplayDataNN( DISPLAY_DATA *d );
void FillDisplayDataOPT( DISPLAY_DATA *d, CSHIFT *cs , CSHIFT *oldcs);

#define LABEL_SIZE  8
#define DISPLAY_H

#endif
