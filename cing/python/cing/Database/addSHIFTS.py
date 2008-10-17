from cing.Libs.AwkLike import AwkLikeS
from cing.Libs.NTutils import NTdict
from cing.core.constants import IUPAC
from cing.core.database import NTdb
from cing.core.dictionaries import NTdbGetAtom
from cing.Libs.NTutils import NTmessage

shifts = """
# Statistics Calculated for All Chemical Shifts from Atoms in the 20 Common Amino Acids
#
# The statistics presented in this table were calculated from the full BMRB database.
# This includes paramagnetic proteins, proteins with aromatic prosthetic groups, and
# entries where chemical shifts are reported relative to uncommon chemical shift references.
# The calculated statistics are derived from a total of 1391695 chemical shifts.
#
# In the table, the highlighted residue codes provide a link to a gif image of the amino
# acid with its atom nomenclature.
# Jump to amino acid: Ala  Arg  Asn  Asp  Cys  Gln  Glu  Gly  His  Ile
#
#
#                   Leu  Lys  Met  Phe  Pro  Ser  Thr  Trp  Tyr  Val
#
#
#Last updated: 09-20-2004
#
#Amino   Atom    Atom     Number     Minimum     Maximum    Average    Standard
#Acid    Name    Type    of Shifts    Shift       Shift      Shift     Deviation


ALA     H        H        13574       0.95       12.25       8.19       0.63
ALA     HA       H        11525       1.24        8.62       4.26       0.45
ALA     HB       H        10624      -2.29        3.70       1.37       0.28
ALA     C        C        6555       49.30      185.20     177.77       2.70
ALA     CA       C        9778       42.82       99.00      53.20       2.14
ALA     CB       C        8934        0.00       99.00      19.04       2.58
ALA     N        N        11099      18.28      219.60     123.26       4.61

ARG     H        H        8957        3.64       11.41       8.24       0.61
ARG     HA       H        7625        1.34       12.57       4.29       0.48
ARG     HB2      H        6638       -4.78        4.59       1.80       0.30
ARG     HB3      H        6074       -0.74        3.64       1.78       0.29
ARG     HG2      H        5746       -1.45        4.20       1.58       0.28
ARG     HG3      H        5125       -0.51        5.47       1.56       0.30
ARG     HD2      H        5536       -6.44        4.38       3.12       0.30
ARG     HD3      H        4849       -0.14        4.66       3.11       0.28
ARG     HE       H        2450        1.15       11.88       7.33       0.64
ARG     HH1     H        301         5.50       10.30       6.85       0.51
ARG     HH21     H        266         4.59        9.70       6.79       0.47
ARG     HH22     H        226         4.59        9.43       6.77       0.50
ARG     C        C        4244        2.20      184.51     176.43       4.30
ARG     CA       C        6432        8.37       70.69      56.84       2.52
ARG     CB       C        5652       22.00       82.18      30.71       2.60
ARG     CG       C        3267       18.22       76.58      27.38       2.59
ARG     CD       C        3360       23.20       91.28      43.21       2.27
ARG     CZ       C        93        156.49      160.70     159.16       1.00
ARG     N        N        7065       67.14      176.86     120.72       4.01
ARG     NE       N        1043        7.28      145.60      93.79      15.46
ARG     NH1      N        61         70.10      112.50      74.22       7.70
ARG     NH2      N        51         66.20      123.30      75.18      10.68

ARG+     H        H        8957        3.64       11.41       8.24       0.61
ARG+     HA       H        7625        1.34       12.57       4.29       0.48
ARG+     HB2      H        6638       -4.78        4.59       1.80       0.30
ARG+     HB3      H        6074       -0.74        3.64       1.78       0.29
ARG+     HG2      H        5746       -1.45        4.20       1.58       0.28
ARG+     HG3      H        5125       -0.51        5.47       1.56       0.30
ARG+     HD2      H        5536       -6.44        4.38       3.12       0.30
ARG+     HD3      H        4849       -0.14        4.66       3.11       0.28
ARG+     HE       H        2450        1.15       11.88       7.33       0.64
ARG+     HH11     H        301         5.50       10.30       6.85       0.51
ARG+     HH12     H        222         5.50       10.30       6.79       0.48
ARG+     HH21     H        266         4.59        9.70       6.79       0.47
ARG+     HH22     H        226         4.59        9.43       6.77       0.50
ARG+     C        C        4244        2.20      184.51     176.43       4.30
ARG+     CA       C        6432        8.37       70.69      56.84       2.52
ARG+     CB       C        5652       22.00       82.18      30.71       2.60
ARG+     CG       C        3267       18.22       76.58      27.38       2.59
ARG+     CD       C        3360       23.20       91.28      43.21       2.27
ARG+     CZ       C        93        156.49      160.70     159.16       1.00
ARG+     N        N        7065       67.14      176.86     120.72       4.01
ARG+     NE       N        1043        7.28      145.60      93.79      15.46
ARG+     NH1      N        61         70.10      112.50      74.22       7.70
ARG+     NH2      N        51         66.20      123.30      75.18      10.68

ASP     H        H        10712       5.43       12.61       8.33       0.60
ASP     HA       H        9046        0.25        8.60       4.61       0.34
ASP     HB2      H        8163       -0.39       37.40       2.77       1.04
ASP     HB3      H        7721       -1.46       37.20       2.71       1.05
ASP     C        C        5476      166.80      182.80     176.48       1.76
ASP     CA       C        7958       39.80       68.47      54.66       2.13
ASP     CB       C        7181       29.51      138.16      40.88       2.57
ASP     CG       C        222       173.49      182.66     179.34       1.44
ASP     N        N        8996      105.33      216.70     120.78       4.25

ASN     H        H        7880        3.61      448.00       8.41       5.00
ASN     HA       H        6655        2.26        6.92       4.68       0.38
ASN     HB2      H        6044       -0.64        4.47       2.81       0.35
ASN     HB3      H        5789       -0.68        4.47       2.76       0.36
ASN     HD21     H        4143        2.06       10.10       7.33       0.54
ASN     HD22     H        4115        3.05       11.43       7.17       0.55
ASN     C        C        3754        2.20      181.99     175.31       3.37
ASN     CA       C        5533        2.20       99.00      53.52       2.25
ASN     CB       C        4994        1.96       99.00      38.77       2.92
ASN     CG       C        482       112.29      181.20     176.69       3.20
ASN     N        N        6255      104.22      137.49     119.08       4.27
ASN     ND2      N        2784       40.60      133.59     112.86       3.42

CYS     H        H        4888        4.73       12.12       8.41       0.69
CYS     HA       H        4558        1.64       43.50       4.81       1.70
CYS     HB2      H        4324      -39.82      134.60       3.27       4.48
CYS     HB3      H        4219      -44.20      125.00       3.23       4.68
CYS     HG       H        35          0.34        7.39       2.43       1.69
CYS     C        C        1439        2.20      182.73     174.76       4.99
CYS     CA       C        2119       41.91       68.54      57.74       3.47
CYS     CB       C        1836       20.10       73.92      33.86       6.64
CYS     N        N        2629      100.48      137.27     119.97       4.70

GLU     H        H        13643       4.31       64.68       8.35       0.90
GLU     HA       H        11518       1.77       31.32       4.25       0.50
GLU     HB2      H        10127       0.12        4.82       2.04       0.24
GLU     HB3      H        9334       -0.79        3.76       2.02       0.24
GLU     HG2      H        8956        0.00        4.69       2.30       0.23
GLU     HG3      H        8123       -0.10        4.69       2.28       0.24
GLU     C        C        7163        8.22      182.70     176.96       3.39
GLU     CA       C        10372      28.80       82.05      57.45       2.24
GLU     CB       C        9299       21.70      114.27      30.08       2.74
GLU     CG       C        5983        6.16       84.58      36.13       2.61
GLU     CD       C        215         0.00      185.27     181.63      12.57
GLU     N        N        11584       0.00      429.00     120.74       5.49

GLN     H        H        7209        4.24       13.17       8.21       0.62
GLN     HA       H        6128        2.24        7.43       4.29       0.45
GLN     HB2      H        5339       -0.70        5.18       2.05       0.28
GLN     HB3      H        4940       -1.14       20.90       2.04       0.40
GLN     HG2      H        4863       -1.76        3.66       2.32       0.30
GLN     HG3      H        4363       -1.08        6.79       2.30       0.32
GLN     HE21     H        3405        2.21       11.11       7.19       0.51
GLN     HE22     H        3389        2.10       10.02       7.05       0.50
GLN     C        C        3606      169.03      184.44     176.38       1.95
GLN     CA       C        5379        4.10       69.63      56.56       2.32
GLN     CB       C        4841       21.00       79.68      29.26       2.44
GLN     CG       C        3081       13.43      125.57      33.81       2.59
GLN     CD       C        404       171.82      183.50     179.63       1.41
GLN     N        N        6044       82.60      216.50     119.84       4.03
GLN     NE2      N        2536       11.96      155.00     111.79       3.40

GLY     H        H        13471     -15.30      128.71       8.33       1.28
GLY     HA2      H        11261      -3.40        8.64       3.96       0.44
GLY     HA3      H        10628      -3.40        7.58       3.89       0.48
GLY     C        C        6270        2.20      183.00     173.97       4.12
GLY     CA       C        9443        2.20       95.10      45.42       2.23
GLY     N        N        10682       8.65      216.00     109.71       4.79

HIS     H        H        3959        4.45       13.34       8.27       0.82
HIS     HA       H        3379        0.68       11.38       4.65       0.77
HIS     HB2      H        3072       -0.05       45.90       3.37       2.23
HIS     HB3      H        2944       -6.20       38.50       3.28       2.03
HIS     HD1      H        334       -15.00       86.50      12.97      14.20
HIS     HD2      H        2379      -25.85       67.80       7.94       7.05
HIS     HE1      H        2121      -26.60       43.80       7.65       4.29
HIS     HE2      H        121       -15.00       76.40      14.02      13.24
HIS     C        C        1852        2.20      180.93     175.17       4.51
HIS     CA       C        2875       23.91      118.60      56.49       3.05
HIS     CB       C        2577       18.80       80.78      30.25       2.94
HIS     CG       C        62         71.30      138.00     130.40       8.34
HIS     CD2      C        767         7.19      156.00     119.20       7.50
HIS     CE1      C        584         8.27      141.10     135.98       8.42
HIS     N        N        3138      105.00      137.80     119.52       4.34
HIS     ND1      N        152        64.90      256.60     189.56      36.14
HIS     NE2      N        148        17.00      246.80     176.81      24.54

ILE     H        H        9285        1.92       11.49       8.28       0.71
ILE     HA       H        7880        1.03        6.30       4.19       0.58
ILE     HB       H        7114       -2.44       38.70       1.80       0.54
ILE     HG12     H        6147      -10.10        5.56       1.26       0.62
ILE     HG13     H        5803      -10.10        9.71       1.22       0.73
ILE     HG2      H        6580       -3.62        6.23       0.78       0.40
ILE     HD1      H        6454       -4.15        8.80       0.67       0.45
ILE     C        C        4775      167.00      182.70     175.94       1.93
ILE     CA       C        7029       39.67       77.93      61.60       2.78
ILE     CB       C        6337       20.94       87.68      38.66       2.75
ILE     CG1      C        3934        8.00      126.90      27.80       3.81
ILE     CG2      C        4329        7.30       65.48      17.67       2.92
ILE     CD1      C        4272        1.02       78.64      13.69       3.60
ILE     N        N        7794       37.30      209.20     121.59       4.86

LEU     H        H        14976       0.09       12.26       8.22       0.67
LEU     HA       H        12444       0.51        8.30       4.32       0.49
LEU     HB2      H        10869      -1.44        8.02       1.64       0.40
LEU     HB3      H        10228      -1.79        8.39       1.55       0.40
LEU     HG       H        9548       -2.08        5.70       1.52       0.37
LEU     HD1      H        10471      -3.42        7.50       0.76       0.38
LEU     HD2      H        10003      -3.42        8.71       0.73       0.40
LEU     C        C        7646      167.49      189.78     177.00       2.02
LEU     CA       C        11162      44.60       85.60      55.63       2.21
LEU     CB       C        10063      27.31       93.18      42.32       2.44
LEU     CG       C        5857       15.57       75.28      26.80       2.46
LEU     CD1      C        6639        0.73       73.88      24.71       2.86
LEU     CD2      C        6204        6.00       73.48      24.22       2.87
LEU     N        N        12520       8.24      521.90     121.95       7.60

LYS     H        H        13884       0.32       12.62       8.19       0.64
LYS     HA       H        11687       0.27        8.60       4.27       0.47
LYS     HB2      H        10210      -0.84       10.94       1.79       0.29
LYS     HB3      H        9331       -0.62        9.43       1.76       0.30
LYS     HG2      H        8624       -1.16        6.70       1.38       0.29
LYS     HG3      H        7700       -1.83        3.99       1.36       0.31
LYS     HD2      H        7362       -1.06      119.62       1.63       1.43
LYS     HD3      H        6295       -2.02        4.70       1.60       0.27
LYS     HE2      H        7185       -0.49        8.37       2.93       0.24
LYS     HE3      H        6080       -0.05        6.83       2.92       0.25
LYS     HZ1       H        585       -10.90        9.90       7.43       1.14
LYS     C        C        6579      121.16      996.25     176.81      10.32
LYS     CA       C        9697       43.10       82.05      56.90       2.29
LYS     CB       C        8668       22.90       82.98      32.82       2.49
LYS     CG       C        5163        0.00       77.38      24.99       2.52
LYS     CD       C        4810       21.30       77.48      28.97       2.41
LYS     CE       C        4606       24.20       89.98      41.92       2.26
LYS     N        N        11081     101.10      217.00     121.13       4.38
LYS     NZ       N        22          7.77      131.04      48.17      36.38

MET     H        H        3609        4.87       10.62       8.26       0.61
MET     HA       H        3178       -0.93        6.35       4.38       0.51
MET     HB2      H        2741       -9.84       33.75       2.05       0.98
MET     HB3      H        2558       -2.64       12.94       2.04       0.77
MET     HG2      H        2440      -33.86       32.70       2.18       3.64
MET     HG3      H        2288      -33.86       31.70       2.11       3.92
MET     HE       H        1654      -24.86        4.00       1.13       4.01
MET     C        C        1873        2.20      181.61     176.17       4.64
MET     CA       C        2875       47.70       72.49      56.23       2.41
MET     CB       C        2578        0.20       83.38      33.07       2.97
MET     CG       C        1536        2.30       81.18      32.06       2.47
MET     CE       C        1059        0.00       68.10      17.45       3.91
MET     N        N        3069       39.90      179.00     120.08       4.24

PHE     H        H        6780        4.06       12.03       8.37       0.73
PHE     HA       H        5686        1.45      122.00       4.63       1.67
PHE     HB2      H        5178        0.43        6.96       2.99       0.40
PHE     HB3      H        4960        0.31       12.72       2.96       0.43
PHE     HD1      H        4511        2.02        8.70       6.99       0.60
PHE     HD2      H        3596        2.02        8.70       6.98       0.64
PHE     HE1      H        4080        0.74       12.90       7.02       0.71
PHE     HE2      H        3335        2.95       12.90       7.02       0.75
PHE     HZ       H        3144       -7.14       43.62       7.01       1.25
PHE     C        C        3413      124.30      181.96     175.56       2.19
PHE     CA       C        4998       22.72       73.43      58.17       2.74
PHE     CB       C        4503       21.40       88.78      40.01       2.82
PHE     CG       C        55         29.57      141.50     135.57      14.85
PHE     CD1      C        1499       19.15      138.12     131.02       5.71
PHE     CD2      C        929        19.15      137.20     130.86       6.72
PHE     CE1      C        1259        7.90      135.60     130.02       6.40
PHE     CE2      C        775         7.90      134.50     129.94       7.60
PHE     CZ       C        955         9.28      138.60     128.51       6.83
PHE     N        N        5628      102.76      229.00     120.72       4.83

PRO     HA       H        5966        1.04        8.51       4.40       0.38
PRO     HB2      H        5394       -0.78        5.25       2.07       0.41
PRO     HB3      H        5163       -3.48        6.10       2.02       0.44
PRO     HG2      H        4692       -2.35        4.92       1.92       0.38
PRO     HG3      H        4279       -1.02        4.92       1.90       0.40
PRO     HD2      H        4947       -6.56        6.69       3.60       0.69
PRO     HD3      H        4689       -6.56        6.05       3.58       0.69
PRO     C        C        3432      150.59      182.30     176.75       1.69
PRO     CA       C        5187       26.45       73.44      63.25       1.89
PRO     CB       C        4596       25.48       81.08      31.94       2.90
PRO     CG       C        2799       19.31       76.28      27.44       3.47
PRO     CD       C        2876        4.99       98.58      50.38       3.59
PRO     N        N        169        31.27      238.30     132.86      19.46

SER     H        H        10939     -15.30       13.13       8.29       0.67
SER     HA       H        9365        1.43        7.37       4.50       0.43
SER     HB2      H        8217        0.61        5.70       3.88       0.30
SER     HB3      H        7503        0.61        5.52       3.85       0.31
SER     HG       H        160         0.00       11.36       5.65       1.54
SER     C        C        5249      165.00      197.10     174.69       1.79
SER     CA       C        7925       45.13       76.07      58.64       2.21
SER     CB       C        6941        0.00      171.73      63.81       2.44
SER     N        N        8709      102.60      196.20     116.35       3.99

THR     H        H        10330       0.20       12.20       8.26       0.66
THR     HA       H        8698       -1.50        6.67       4.47       0.50
THR     HB       H        7751        0.09       68.14       4.19       1.09
THR     HG1      H        343         0.32       11.01       5.24       1.93
THR     HG2      H        7600      -12.10       16.30       1.16       0.41
THR     C        C        4801      165.50      183.80     174.63       1.79
THR     CA       C        7275       51.61       82.16      62.19       2.75
THR     CB       C        6452        7.00      629.21      69.62       7.53
THR     CG2      C        4276       11.70       70.78      21.61       2.80
THR     N        N        8356       11.74      211.50     115.66       5.40

TRP     H        H        2267        5.16       11.09       8.28       0.80
TRP     HA       H        1892        2.28        7.05       4.72       0.57
TRP     HB2      H        1732        0.42        5.35       3.20       0.36
TRP     HB3      H        1663        1.02        4.49       3.16       0.37
TRP     HD1      H        1572        4.90        8.93       7.15       0.35
TRP     HE1      H        1591        5.81       18.00      10.10       0.68
TRP     HE3      H        1458        1.85       10.09       7.26       0.76
TRP     HZ2      H        1529        2.63       10.81       7.22       0.64
TRP     HZ3      H        1429        0.76        8.20       6.78       0.74
TRP     HH2      H        1442        2.84       10.90       6.90       0.71
TRP     C        C        1012      169.63      181.83     176.23       1.92
TRP     CA       C        1523       47.70       65.12      57.66       2.60
TRP     CB       C        1379       23.63       82.08      30.26       3.79
TRP     CG       C        101        25.80      114.60     108.99       9.32
TRP     CD1      C        554        76.02      131.28     125.86       5.03
TRP     CD2      C        77        120.20      131.20     127.56       1.42
TRP     CE2      C        74        118.37      177.71     137.64       6.17
TRP     CE3      C        446        40.14      138.50     119.52       6.96
TRP     CZ2      C        510         6.84      125.70     113.45       7.37
TRP     CZ3      C        459         6.76      138.39     120.48       7.80
TRP     CH2      C        472        74.70      133.10     122.79       6.26
TRP     N        N        1716       25.80      207.70     121.72       5.50
TRP     NE1      N        947         0.53      249.50     129.46       6.51

TYR     H        H        5942        4.39       11.92       8.34       0.75
TYR     HA       H        5040        1.20        6.73       4.63       0.58
TYR     HB2      H        4612        0.30       23.28       2.91       0.50
TYR     HB3      H        4443        0.03       23.28       2.88       0.50
TYR     HD1      H        4234        0.73        9.39       6.90       0.52
TYR     HD2      H        3447        0.92       10.50       6.89       0.57
TYR     HE1      H        4088        0.08       11.80       6.68       0.47
TYR     HE2      H        3346        0.43       11.70       6.67       0.51
TYR     HH       H        123         3.07       31.00       9.08       3.03
TYR     C        C        2575        2.20      182.40     175.41       3.96
TYR     CA       C        3961        2.20       65.80      58.05       2.79
TYR     CB       C        3504       28.95       89.58      39.40       3.08
TYR     CG       C        90        120.94      138.70     129.12       2.53
TYR     CD1      C        1320       19.59      138.70     131.95       7.41
TYR     CD2      C        783        19.59      137.80     131.52       9.26
TYR     CE1      C        1306       61.90      159.57     117.57       4.52
TYR     CE2      C        785        61.90      154.10     117.46       5.18
TYR     CZ       C        84         31.30      162.70     153.34      18.84
TYR     N        N        4519      103.60      606.00     121.13      12.29

VAL     H        H        12028       3.98       11.63       8.28       0.71
VAL     HA       H        10211      -2.83        9.20       4.16       0.64
VAL     HB       H        9246      -18.50       31.75       1.99       0.51
VAL     HG1      H        8944      -27.20       24.20       0.83       0.51
VAL     HG2      H        8617      -27.20       24.20       0.80       0.54
VAL     C        C        5994      168.50      181.72     175.76       1.94
VAL     CA       C        8868       50.13       78.44      62.50       2.95
VAL     CB       C        7934       20.24       83.58      32.71       2.48
VAL     CG1      C        5447       11.60      117.16      21.63       3.16
VAL     CG2      C        5145       11.30       71.18      21.47       3.04
VAL     N        N        10075      16.77      508.99     121.36       9.45
"""



resEquiv = dict (
ASP = ['ASP', 'ASP-'],
CYS = ['CYS', 'CYSS'],
GLU = ['GLU', 'GLU-'],
HIS = ['HIS', 'HIS+', 'HIST'],
LYS = ['LYS', 'LYS+'],
)

for line in AwkLikeS( shifts ):
    if (not line.isComment() and line.NF == 8):
        if (line.dollar[1] in resEquiv):
            resNames = resEquiv[line.dollar[1]]
        else:
            resNames = line.dollar[1:2]
        #end if

        for resName in resNames:
            res = NTdb[resName]

            atm = NTdbGetAtom( resName, line.dollar[2], IUPAC )
            if atm != None:
                atm.shift = NTdict( average=line.float(7), sd=line.float(8) )
            else:
                NTmessage( '>>> line %d: %s', line.NR, line.dollar[0] )

#also get the pseudo shifts
for res in NTdb:
    for atm in res:
        ave = 0.0
        sd = 0.0
        n = 0
        for aN in atm.real:
            a = res[aN]
            if a.shift != None:
                ave += a.shift.average
                sd += a.shift.sd
                n += 1
            #end if
        #end for
        if n > 0:
            atm.shift = NTdict( average = ave/float(n), sd = sd/float(n) )

stream = open('bla.text', 'w')
NTdb.exportDef(stream=stream)
stream.close()
