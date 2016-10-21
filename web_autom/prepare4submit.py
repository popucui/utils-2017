#coding=utf-8
'''
input params: 
    rawres 来自superSangerR的原始结果 result
    submitres 提交到报告系统的结果，用于单项检测
    tfType 单项检测的类型，如语言

'''
import sys

rawres = sys.argv[1]
submitres = sys.argv[2]
tfType = sys.argv[3]

gftidDct = {'0':[], '1':[]}
assert tfType in gftidDct, 'tfType not supported'
gftidDct['0'] = [
'gft314794',
'gft1054832',
'gft25934',
'gft1738548',
'gft699780',
'gft187527',
'gft4895730',
'gft769785',
'gft15279'
]
outfile = open(submitres, 'w')
with open(rawres) as f:
    for line in f:
        tmp = line.strip().split()
        gftid = tmp[5]
        if gftid in gftidDct[tfType]:
            outfile.write(line)
            

