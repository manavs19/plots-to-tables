#!/usr/bin/env python

'''
Tabulator main
'''

from glob import glob
import argparse
import cv2

from convert import Converter
from plot_rectangles import PlotRectangles
from xAxis import XAxis
from yAxis import YAxis
from plotname import PlotName
from legends import Legends

parser = argparse.ArgumentParser(
  description='Computes data from the plots in the given PDF')

parser.add_argument('--pdf_path', type=str, help='Path of the input pdf')

def main():
  args = parser.parse_args()

  for fn in glob(args.pdf_path):
    img = Converter().convertPDF(args.pdf_path)

    rectangles = PlotRectangles().getRectangles(img)

    x_axis = XAxis(img.copy())
    y_axis = YAxis(img.copy())
    plot_name = PlotName(img.copy())

    for i, rectangle in enumerate(rectangles):
      ret = x_axis.findXScale(rectangle, i)
      xLabel, mx = x_axis.findXLabel(rectangle, ret[1], i)
      xScale = ret[0]
      xStart = ret[2]
      xDelta = ret[3]

      ret = y_axis.findYScale(rectangle, i)
      yLabel = y_axis.findYLabel(rectangle, ret[1], i)
      yScale = ret[0]
      yStart = ret[2]
      yDelta = ret[3]

      plotName = plot_name.getPlotName(rectangle, i, mx)

      legends = Legends(rectangle, img)
      legendItems, colorMap = legends.getLegend(i)

if __name__ == '__main__':
  main()