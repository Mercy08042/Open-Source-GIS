"""
    1. 学习Python的读写文件操作，参考 https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files
    2. 把phenology.txt文件按照某一列进行分类，并将每类分别写入不同的文件,
      （例如按作物类型进行分类，会产生'大豆.txt'、‘冬小麦.txt’等一系列文件）
       并且支持选择所要输出的列（例如，输出1至4列、倒数第1列）。

    date: 4/12/2019
    author:Mercy
"""

import codecs


def classify(splitlines, namelist):     # 用于按作物类型分类的函数
    types = [[]for index in range(len(namelist))]
    for item in splitlines:
        for index in range(len(namelist)):
            if item[4] == namelist[index]:
                types[index].append(item)
                break
    return types


def main():
    with codecs.open('S201511262124407981809.txt', 'r', 'utf-8') as fr:
        header = fr.readline()
        print(header)
        lines = fr.readlines()
        splitlines = []
        crop_types = []  # 用于存储作物类型名称
        for line in lines:
            items = line.split()  # items:list 存储一行数据
            splitlines.append(items)
            if items[4] not in crop_types and items[4] != "-9999":  # 将未曾出现过的作物类型添加到croptype列表中,舍弃空值
                crop_types.append(items[4])

    types = classify(splitlines, crop_types)

    # 用户给定输出列的区间或列号，将选中的列写入相应文件中
    print("数据共有20列，请选择您想要导出的列。您有两种输入类型：1. 某一个区间[a,b]；2. 具体的分散的列编号（1-20）。前者请输入0，后者请输入1。")
    flag = input("您选择的输入类型是：")
    columns = input("请输入列区间或编号（空格分隔）：")
    columns_split = columns.split(' ')
    for index in range(len(crop_types)):    # 创建输出文件
        filename = str(crop_types[index]) + ".txt"
        with codecs.open(filename, 'w', 'utf-8') as fw:
            num = 0
            for item in types[index]:
                if flag == '0':     # 用户输入为区间
                    a = int(columns_split[0])
                    b = int(columns_split[len(columns_split) - 1])
                    for i in range(a-1, b):
                        fw.write(str(types[index][num][i]) + ' ')
                elif flag == '1':   # 用户输入为散列
                    for i in columns_split:
                        fw.write(str(types[index][num][int(i) - 1]) + ' ')
                num += 1
                fw.write('\n')


if __name__ == '__main__':
    main()









