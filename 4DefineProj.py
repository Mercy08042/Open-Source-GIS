"""
    编写程序把chap2中生成的点和面shp文件转换到 Lambert 投影坐标系（标准纬线：φ1=25°00′，φ2=47°00′）

    date: 12/19/2019
    author: Mercy
"""

from osgeo import ogr, osr
import os
os.environ['SHAPE_ENCODING'] = 'GBK'  # 属性信息编码规范


def projection(src_file, dst_file, geom_type):
    src_ds = ogr.Open(src_file)
    src_layer = src_ds.GetLayer(0)
    src_srs = src_layer.GetSpatialRef()  # 输入数据投影
    if src_srs is None:
        inosr = osr.SpatialReference()
        inosr.ImportFromEPSG(4269)
    else:
        inosr = src_srs

    # 输出数据投影定义，参考资料：http://spatialreference.org
    srs_def = """+proj=lcc +lat_1=25 +lat_2=47 +lat_0=33.3 +lon_0=105 +x_0=0 +y_0=0
            +a=6378249.2 +b=6356514.999904194 +units=m +no_defs  """
    dst_srs = osr.SpatialReference()
    dst_srs.ImportFromProj4(srs_def)

    # 创建转换对象
    ctx = osr.CoordinateTransformation(inosr, dst_srs)

    # 创建输出文件
    driver = ogr.GetDriverByName('ESRI Shapefile')
    if os.access(dst_file, os.F_OK):  # 若文件已存在，则删除
        driver.DeleteDataSource(dst_file)
    dst_ds = driver.CreateDataSource(dst_file)

    if geom_type == 'Polygon':  # 创建面图层
        dst_layer = dst_ds.CreateLayer(dst_file, dst_srs, ogr.wkbPolygon)
    elif geom_type == 'Point':  # 创建点图层
        dst_layer = dst_ds.CreateLayer(dst_file, dst_srs, ogr.wkbPoint)
    dst_layer.CreateFields(src_layer.schema)
    dst_defn = dst_layer.GetLayerDefn()
    dst_feature = ogr.Feature(dst_defn)

    # 对要素进行投影变换并添加属性信息
    for src_feature in src_layer:
        geometry = src_feature.GetGeometryRef()
        geometry.Transform(ctx)
        dst_feature.SetGeometry(geometry)  # 要素几何变换
        for i in range(src_feature.GetFieldCount()):  # src_feature.GetFieldCount() = 5
            value = src_feature.GetField(i)  # os.environ['SHAPE_ENCODING'] = 'GBK'
            dst_feature.SetField(i, value)  # 添加要素属性
        dst_layer.CreateFeature(dst_feature)

    del src_ds
    del dst_ds

def main():
    src_file1 = 'point.shp'
    dst_file1 = 'point_proj'  # 创建一个文件夹
    src_file2 = 'buffer.shp'
    dst_file2 = 'buffer_proj'
    projection(src_file1, dst_file1, 'Point')
    projection(src_file2, dst_file2, 'Polygon')


if __name__ == '__main__':
    main()

