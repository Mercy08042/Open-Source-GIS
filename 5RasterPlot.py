"""
    1. 读取一个栅格文件，显示其直方图 (单色图像，灰度直方图，彩色图像，多波段多个直方图，还要考虑直方图是否进行归一化处理)
    2. 用 basemap 显示栅格文件

    date: 12/19/2019
    author: Mercy
"""
import numpy as np
import matplotlib.pyplot as plt
from osgeo import gdal
from PIL import Image
from numpy import linspace
from numpy import meshgrid
from mpl_toolkits.basemap import Basemap


def show_raster_histogram(fn):   # 栅格图像显示
    ds = gdal.Open(fn)
    data = ds.ReadAsArray() # 读取栅格图像，存储为二维数组
    array = data.flatten() # 将二维数组转换为一维数组
    plt.hist(array, bins=256, density=1, color='black') # 调用hist显示直方图
    plt.show()

def show_raster_by_basemap(fn):     # Basemap立体颜色效果显示
    map = Basemap(projection='tmerc', lat_0=0, lon_0=3,
                  llcrnrlon=1.819757266426611,
                  llcrnrlat=41.583851612359275,
                  urcrnrlon=1.841589961763497,
                  urcrnrlat=41.598674173123) # 创建map对象
    ds = gdal.Open(fn)
    data = ds.ReadAsArray()
    x = linspace(0, map.urcrnrx, data.shape[1])
    y = linspace(map.urcrnry, 0, data.shape[0])
    xx, yy = meshgrid(x, y)
    map.pcolormesh(xx, yy, data) # 立体效果颜色渲染
    plt.show()

def show_gray_img_histogram(fn):   # 灰度图像显示
    image = Image.open(fn)
    plt.figure("Hist")
    array = np.array(image).flatten()
    plt.hist(array, bins=256, density=1, color='black')
    plt.show()

def show_color_img_histogram(fn):   # 彩色图像显示
    src = Image.open(fn)
    r, g, b = src.split()  # 分离R\G\B
    # 要对图像求直方图，就需要先把图像矩阵进行flatten操作，使之变为一维数组，然后再进行统计
    # 分别提取R\G\B统计值，叠加绘图
    plt.figure("Hist")
    ar = np.array(r).flatten()
    plt.hist(ar, bins=256, density=1, color='red')
    ag = np.array(g).flatten()
    plt.hist(ag, bins=256, density=1, color='green')
    ab = np.array(b).flatten()
    plt.hist(ab, bins=256, density=1, color='blue')

    plt.show()

def main():
    raster_fn = 'cluster_result.tif'    # 栅格图像名称
    gray_img_fn = 'BeautyAndTheBeast.png'    # 灰度图像名称
    color_img_fn = 'Jean Cocteau.png'    # 彩色图像名称
    show_color_img_histogram(color_img_fn)
    show_gray_img_histogram(gray_img_fn)
    show_raster_histogram(raster_fn)
    show_raster_by_basemap(raster_fn)


if __name__ == '__main__':
    main()
