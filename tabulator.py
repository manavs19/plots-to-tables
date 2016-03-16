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
from pdfGen import PdfGen

parser = argparse.ArgumentParser(
  description='Computes data from the plots in the given PDF')

parser.add_argument('--inp', type=str, help='Path of the input pdf')
parser.add_argument('--out', type=str, help='Path of the output pdf')
parser.add_argument('--csv', type=bool, default=False, help='True if data to be written in csv format also')

def main():
  args = parser.parse_args()

  for fn in glob(args.inp):
    img = Converter().convertPDF(args.inp)

    rectangles = PlotRectangles().getRectangles(img)

    x_axis = XAxis(img.copy())
    y_axis = YAxis(img.copy())
    plot_name = PlotName(img.copy())
    pdf_gen = PdfGen(args.out, args.csv)

    #iterating over tables
    for i, rectangle in enumerate(rectangles):
      ret = x_axis.findXScale(rectangle, i)
      xLabelPath, mx = x_axis.findXLabel(rectangle, ret[1], i)
      xScale = ret[0]
      xStart = ret[2]
      xDelta = ret[3]

      ret = y_axis.findYScale(rectangle, i)
      yLabelPath = y_axis.findYLabel(rectangle, ret[1], i)
      yScale = ret[0]
      yStart = ret[2]
      yDelta = ret[3]

      plotNamePath = plot_name.getPlotName(rectangle, i, mx)

      legends = Legends(rectangle, img)
      legendItemImagePaths, colorMap = legends.getLegend(i)

      data = []

      table_headers = [xLabelPath] + legendItemImagePaths
      pdf_gen.add_table(plotNamePath, yLabelPath, table_headers, data)

    pdf_gen.print_file()

if __name__ == '__main__':
  main()