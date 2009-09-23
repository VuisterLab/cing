from matplotlib import colors
from matplotlib.cm import LUTSIZE
from matplotlib.cm import datad

# JFD no idea what the difference between the below columns are:
#                           ->|  |<-
_gray_inv_data =  {
               'red':   ((0., 1, 1), (1., 0, 0)),
               'green': ((0., 1, 1), (1., 0, 0)),
               'blue':  ((0., 1, 1), (1., 0, 0))}

_red_inv_data =  {
               'red':   ((0., 1, 1), (1., 1, 1)),
               'green': ((0., 1, 1), (1., 0, 0)),
               'blue':  ((0., 1, 1), (1., 0, 0))}
_green_inv_data =  {
               'red':   ((0., 1, 1), (1., 0, 0)),
               'green': ((0., 1, 1), (1., 1, 1)),
               'blue':  ((0., 1, 1), (1., 0, 0))}
_blue_inv_data =  {
               'red':   ((0., 1, 1), (1., 0, 0)),
               'green': ((0., 1, 1), (1., 0, 0)),
               'blue':  ((0., 1, 1), (1., 1, 1))}
_yellow_inv_data =  {
               'red':   ((0., 1, 1), (1., 1, 1)),
               'green': ((0., 1, 1), (1., 1, 1)),
               'blue':  ((0., 1, 1), (1., 0, 0))}

gray_inv   = colors.LinearSegmentedColormap('gray_inv',  _gray_inv_data, LUTSIZE)
red_inv    = colors.LinearSegmentedColormap('red_inv',   _red_inv_data, LUTSIZE)
green_inv  = colors.LinearSegmentedColormap('green_inv', _green_inv_data, LUTSIZE)
blue_inv   = colors.LinearSegmentedColormap('blue_inv',  _blue_inv_data, LUTSIZE)
yellow_inv = colors.LinearSegmentedColormap('yellow_inv',_yellow_inv_data, LUTSIZE)

datad[ 'gray_inv' ]   = _gray_inv_data
datad[ 'red_inv' ]    = _red_inv_data
datad[ 'green_inv' ]  = _green_inv_data
datad[ 'blue_inv' ]   = _blue_inv_data
datad[ 'yellow_inv' ] = _yellow_inv_data


