"""
    1. 以dem_fengle.tif文件为例，编程实现栅格数据的重采样（如将栅格分辨率变为原来的2倍，或用户输入参数）
    2. cluster_result.tif中有很多破碎的栅格斑块，编程去除这些破碎斑块
      （例如，如果一个栅格单元周围的值与其自身的值都不相同，则把该单元的值变为周围单元的值）

    date: 12/12/2019
    author: Mercy
"""
from osgeo import gdal, gdalconst
import matplotlib.pyplot as plt
import numpy as np


def raster_reading(fn):
    """
    读取栅格图像
    :param fn: 栅格图像名称
    :return:
    """
    ds = gdal.Open(fn)  # 得到Dataset，一个Dataset可能包含多个波段
    band = ds.GetRasterBand(1)  # 得到第一个波段
    data = band.ReadAsArray()
    print(data)
    print(type(data))
    plt.show()
    '''
    geotrans = ds.GetGeoTransform()     # 仿射变换参数
    proj_info = ds.GetProjection()  # 得到投影信息
    ds.RasterCount  # 波段数
    n_rows, n_cols = band.YSize, band.XSize  # 行列数
    nodata_value = band.GetNoDataValue()  # 空值
    '''


def resample(in_fn, ref_fn, out_fn):
    """
    栅格数据重采样 最邻近法
    :param in_fn: 原始图像名称给
    :param ref_fn: 参考图像
    :param out_fn: 结果图像名称
    :return: null
    """

    # 获取原始影像信息
    in_ds = gdal.Open(in_fn, gdal.GA_ReadOnly)
    in_proj = in_ds.GetProjection()

    # 获取参考影像信息
    ref_ds = gdal.Open(ref_fn, gdal.GA_ReadOnly)
    ref_proj = ref_ds.GetProjection()
    ref_refn = ref_ds.GetGeoTransform()
    ref_band = ref_ds.GetRasterBand(1)
    x = ref_ds.RasterXSize
    y = ref_ds.RasterYSize
    nbands = ref_ds.RasterCount

    # 创建重采样输出文件
    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(out_fn, x, y, nbands, ref_band.DataType)
    out_ds.SetGeoTransform(ref_refn)
    out_ds.SetProjection(ref_proj)
    gdal.ReprojectImage(ref_ds, out_ds, in_proj, ref_proj, gdalconst.GRA_Bilinear)


def myresample(in_fn, out_fn, m):
    in_ds = gdal.Open(in_fn)  # 打开原始栅格图像
    out_rows = int(in_ds.RasterYSize / m)  # 设置重采样后的图像行列数
    out_columns = int(in_ds.RasterXSize / m)
    num_bands = in_ds.RasterCount  # 设置重采样后的图像波段

    gtiff_driver = gdal.GetDriverByName('GTiff')  # 创建重采样后图像
    out_ds = gtiff_driver.Create(out_fn, out_columns, out_rows, num_bands)
    out_ds.SetProjection(in_ds.GetProjection())  #
    geotransform = list(in_ds.GetGeoTransform())  # 获取仿射变化参数
    geotransform[1] *= m  # 设置 w-e 像素分辨率
    geotransform[5] *= m  # 设置 n-s 像素分辨率设置输出文件投影
    out_ds.SetGeoTransform(geotransform)

    data = in_ds.ReadRaster(buf_xsize=out_columns, buf_ysize=out_rows)  # 重采样处理

    out_ds.WriteRaster(0, 0, out_columns, out_rows, data)  # 输出结果图像
    out_ds.FlushCache()
    for i in range(num_bands):
        out_ds.GetRasterBand(i + 1).ComputeStatistics(False)
    out_ds.BuildOverviews('average', [2, 4, 8, 16])
    del out_ds


def remove_plaque(in_fn, out_fn):
    """
    函数功能：去除破碎斑块
    定义窗口大小： 3 * 3
    判断条件：栅格值（0-255）对比中心栅格单元的栅格值与周围栅格单元的栅格值
    注意：首行/列、尾行/列的处理
    :param in_filename:
    :param out_filename:
    :return:
    """
    in_ds = gdal.Open(in_fn)
    in_rows = int(in_ds.RasterYSize)
    in_colums = int(in_ds.RasterXSize)
    num_bands = in_ds.RasterCount

    data = in_ds.GetRasterBand(1).ReadAsArray(0, 0, in_colums, in_rows)

    for i in range(1, in_rows - 1):  # 滑动窗口消除斑块 skip first & last
        for j in range(1, in_colums - 1):
            if (data[i, j] != data[i - 1, j - 1]) & (data[i, j] != data[i - 1, j]) & \
                    (data[i, j] != data[i - 1, j + 1]) & (data[i, j] != data[i, j - 1]) & \
                    (data[i, j] != data[i, j + 1]) & (data[i, j] != data[i + 1, j - 1]) & \
                    (data[i, j] != data[i + 1, j + 1]):
                data[i, j] = (data[i - 1, j - 1] + data[i - 1, j] + data[i - 1, j + 1] + data[i, j - 1] + data[i, j + 1] + data[i + 1, j - 1] + data[i + 1, j + 1]) / 8

    # 创建并输出结果图像
    gtiff_driver = gdal.GetDriverByName('GTiff')
    out_ds = gtiff_driver.Create(out_fn, in_colums, in_rows, num_bands)
    out_ds.SetGeoTransform(in_ds.GetGeoTransform())
    out_ds.SetProjection(in_ds.GetProjection())
    out_ds.GetRasterBand(1).WriteArray(data)

    out_ds.FlushCache()
    del out_ds


def main():
    res_in_fn = 'dem_fengle.tif'
    rem_in_fn = 'cluster_result.tif'
    res_out_fn1 = 'resample_dem_fengle1.tif'
    res_out_fn2 = 'resample_dem_fengle2.tif'
    rem_out_fn = 'remove_cluster_result.tif'

    myresample(res_in_fn,res_out_fn1,2)
    remove_plaque(rem_in_fn, rem_out_fn)


if __name__ == '__main__':
    main()
