"""
    1. 把AGME_AB2_CHN_TEN_STATION.txt文件转换为shp文件（点文件）；
    2. 读取第一步中生成的shp文件，进行缓冲区分析，并将结果写为shp文件（面文件）；
    3. 将上述两步的点、线文件转换为geojson，调用folium进行在线地图显示。

    date: 5/12/2019
    author: Mercy
"""

import codecs
import os
from osgeo import gdal
from osgeo import ogr
import geojson
from geojson import Feature, Point, FeatureCollection
import folium


def txt_reading(txt_filename):  # 读txt文件
    with codecs.open(txt_filename, 'r') as txtf:
        firstline = txtf.readline()
        header = firstline.split()
        lines = txtf.readlines()
        splitlines = [header]   # 添加属性名称列表
        for line in lines:
            items = line.split()
            del items[0]    # 根据我对数据的理解，第一列数据是无效的
            splitlines.append(items)
    return splitlines


def create_shp(splitlines, shp_filename):     # 创建shp文件，并将数据写入
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YSE")  # 支持中文路径
    gdal.SetConfigOption("SHAPE_ENCODING", "GBK")  # 属性表字段支持中文

    driver = ogr.GetDriverByName("ESRI Shapefile")  # step1: Register a driver
    if os.access(shp_filename, os.F_OK):  # 若文件已存在，则删除
        driver.DeleteDataSource(shp_filename)
    ds = driver.CreateDataSource(shp_filename)  # step2: Create shapefile (可写）
    layer = ds.CreateLayer(shp_filename[:-4], geom_type=ogr.wkbPoint)  # step3: Create layer

    # 添加属性定义（属性名称需要从txt中获得）
    num = 0
    attr_name = splitlines[0]
    for item in attr_name:
        if num < 3:     # 添加前四列属性字符类型数据
            field = ogr.FieldDefn(attr_name[num], ogr.OFTString)    # 提供的数据中的属性字段 类型均为string
        else:
            field = ogr.FieldDefn(attr_name[num], ogr.OFTReal)   # 定义经纬度字段 类型为 Floating point number
        layer.CreateField(field)
        num += 1

    # 循环读取 splitlines 添加 属性 与 几何 信息
    for line in splitlines[1:]:
        flag = 0
        xy = []     # 存储经纬度坐标
        feature = ogr.Feature(layer.GetLayerDefn())
        for item in line:   # 添加属性信息
            if flag < 3:
                feature.SetField(attr_name[flag], item)
            else:
                feature.SetField(attr_name[flag], float(item))
                xy.append(item)
            flag += 1
        pt = ogr.Geometry(ogr.wkbPoint)     # 添加几何信息
        pt.AddPoint(float(xy[0]), float(xy[1]))
        feature.SetGeometry(pt)
        layer.CreateFeature(feature)  # add feature to layer

    ds.Destroy()    # del ds(内存数据库)
    return layer


def shp_reading(shp_filename):  # #读取shp文件
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YSE")  # 支持中文路径
    gdal.SetConfigOption("SHAPE_ENCODING", "GBK")  # 属性表字段支持中文
    ogr.RegisterAll()   # 注册所有驱动
    ds = ogr.Open(shp_filename, False)  # 打开Shape文件（False - read only, True - read/write）
    if not ds:
        raise IOError("Could not open '%s'" % shp_filename)
    print("open %s successfully" % shp_filename)
    layer = ds.GetLayer(0)
    if not layer:
        raise IOError("Could not open layer")
    return layer


def buffer_analysis(shp_filename, buffer_filename):    # 缓冲区分析
    ds = ogr.Open(shp_filename, 1)
    in_lyr = ds.GetLayer()
    out_lyr = ds.CreateLayer(buffer_filename[:6], in_lyr.GetSpatialRef(), ogr.wkbPolygon)   # 创建缓冲区分析结果文件
    out_lyr.CreateFields(in_lyr.schema)     # 为结果图层创建属性
    out_defn = out_lyr.GetLayerDefn()
    out_feat = ogr.Feature(out_defn)
    bufferDist = 1  # 圆形缓冲区半径设置

    for in_feat in in_lyr:  # 对每一个要素进行缓冲区分析
        geom = in_feat.geometry().Buffer(bufferDist)
        out_feat.SetGeometry(geom)  # 设置几何
        for i in range(in_feat.GetFieldCount()):
            value = in_feat.GetField(i)
            out_feat.SetField(i, value) # 设置属性值
        out_lyr.CreateFeature(out_feat)
    del ds


def shp2geojson(shp_filename, json_filename):    # shp 2 json    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YSE")    # 支持中文路径
    shp_ds = ogr.Open(shp_filename, 1)
    shp_layer = shp_ds.GetLayer()

    # baseName = os.path.basename(json_filename)
    driver = ogr.GetDriverByName("GeoJSON")     # step1 创建驱动
    if os.access(json_filename, os.F_OK):
        driver.DeleteDataSource(json_filename)
    ds = driver.CreateDataSource(json_filename)  # step2 创建临时数据集
    '''
    if ds.GetLayer(json_filename):
        ds.DeleteLayer(baseName)
    # spatialref = shp_layer.GetSpatialRef()   spatialref = None (本身未定义投影）
    '''
    layer = ds.CreateLayer(json_filename)    # step3 创建图层
    layer.CreateFields(shp_layer.schema)    # mistake 一次性添加所有属性定义 GetLayerDefn() 如果单独用函数读shp文件，这里会出错，怀疑是self参数混淆的问题
    out_feature = ogr.Feature(layer.GetLayerDefn())
    for feature in shp_layer:    # 添加要素几何和属性信息
        out_feature.SetGeometry(feature.geometry())
        for i in range(feature.GetFieldCount()):
            out_feature.SetField(i, feature.GetField(i))
        layer.CreateFeature(out_feature)

    ds.Destroy()    # OR del ds
    return layer


def visulize_folium(json_filename):
    with open(json_filename, 'r', encoding='UTF-8') as f:   # 报错信息：'gbk' codec can't decode byte 0xb7 in position 113: illegal multibyte sequence
        data = geojson.load(f)      # 解决方案：encoding='UTF-8'
    feature_collection = FeatureCollection(data['features'])    # 获取要素集合
    m = folium.Map([30, 30], zoom_start=4)  # 创建地图
    folium.GeoJson(feature_collection).add_to(m)    # 将数据添加到地图
    m.save(json_filename[:-5] + '.html')     # 保存在线地图为html


def main():
    txt_filename = 'AGME_AB2_CHN_TEN_STATION.txt'
    shp_filename = 'point.shp'
    buffer_filename = 'buffer.shp'
    json_point = 'point.json'
    json_buffer = 'buffer.json'
    splitlines = txt_reading(txt_filename)
    create_shp(splitlines, shp_filename)
    buffer_analysis(shp_filename,buffer_filename)
    shp2geojson(shp_filename, json_point)
    shp2geojson(buffer_filename, json_buffer)
    visulize_folium(json_point)
    visulize_folium(json_buffer)


if __name__ == '__main__':
    main()