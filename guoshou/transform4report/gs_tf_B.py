#!/home/reboot/software/envs/p3k/bin/python
#coding=utf-8


import fire

def makeResultSample(gtype_B, timeStamp):
    '''
    generate sampleData and resultData for taocan B
    input:
        gtype_B: gene type result of B taocan
        timeStamp: time stamp for upload
    output:
        gtype_B + 'sampleData'
        gtype_B + 'resultData'
    '''
    sampleDataLst = ['snp位点\t基因\t批次\t所属样本\t基因型\t检测结果\n']
    resultDataLst = ['样本编号\t所属项目(动态项目名称必须正确)\t检测结果\t实验批次\n']
    rs2gene = {'rs1042522':'TP53', 'rs9939609':'FTO', 'rs2736100':'TERT'}
    gene2pheno = {
    'rs1042522' : {'GG': '患肿瘤的风险较高', 'GC': '存在一定患肿瘤风险', 'CG': '存在一定患肿瘤风险', 'CC': '患肿瘤的风险正常'},
    'rs9939609': {'TT': '肥胖风险较低', 'AT': '肥胖风险较高', 'TA':'肥胖风险较高', 'AA': '肥胖风险较高'},
    'rs2736100': {'GT': '衰老速度正常', 'TG': '衰老速度正常', 'TT': '衰老速度增加', 'GG': '衰老速度较缓慢'},
    'rs9275319': {'AG':'略高于普通风险', 'GA':'略高于普通风险', 'AA':'略高于普通风险', 'GG':'普通风险'},  #肝癌
    'rs36600': {'CC': '普通风险', 'CT':'略高于普通风险', 'TC':'略高于普通风险', 'TT':'略高于普通风险'}, #肺癌
    'rs817826': {'TT':'普通风险', 'TC':'略高于普通风险', 'CT':'略高于普通风险', 'CC':'略高于普通风险'}, #前列腺癌
    'rs1800440': {'AA':'普通风险', 'AC':'略高于普通风险', 'CA':'略高于普通风险', 'CC':'略高于普通风险'}, #略高于普通风险
    'rs1799949': {'CC':'普通风险', 'CT':'略高于普通风险', 'TC':'略高于普通风险', 'TT':'略高于普通风险'}, #卵巢癌
    'rs1799950': {'AA':'普通风险', 'AG':'略高于普通风险', 'GA':'略高于普通风险', 'GG':'略高于普通风险'}, #乳腺癌 BC2
    'rs1801499': {'TT':'普通风险', 'CT':'略高于普通风险', 'TC':'略高于普通风险', 'CC':'略高于普通风险'}, #乳腺癌 BC3 
    }
    submt_stamp = timeStamp
    with open(gtype_B, mode='r') as f:
        for line in f:
            if line.startswith('序号'):
                continue
            temp = line.rstrip().split()
            barcode, tctype, gender, cancer_gtype, _1, fat_gtype, _2, aged_gtype, _3 = temp[3:]
            sampleDataLine = 'rs1042522\tTP53\t{Stamp}\t{bcode}\t{c_gtype}\t{cphtype}\nrs9939609\tFTO\t{Stamp}\t{bcode}\t{fat_gtype}\t{fphtype}\nrs2736100\tTERT\t{Stamp}\t{bcode}\t{aged_gtype}\t{aphtype}\n'.format(
            Stamp = submt_stamp, bcode=barcode, c_gtype=cancer_gtype, cphtype=gene2pheno['rs1042522'][cancer_gtype],
            fat_gtype=fat_gtype, fphtype=gene2pheno['rs9939609'][fat_gtype], aged_gtype=aged_gtype, aphtype=gene2pheno['rs2736100'][aged_gtype] )
            
            sampleDataLst.append(sampleDataLine)
            
            resultDataLine = '{bcode}\t抗肿瘤基因检测\t\t{Stamp}\n{bcode}\t肥胖基因检测\t\t{Stamp}\n{bcode}\t衰老基因检测\t\t{Stamp}\n'.format(Stamp=submt_stamp, bcode=barcode)
            
            resultDataLst.append(resultDataLine)
    with open('{gtype_B}_sampleData.txt'.format(gtype_B=gtype_B.rstrip('.txt')), 'w') as f:
        f.writelines(sampleDataLst)
    with open('{gtype_B}_resultData.txt'.format(gtype_B=gtype_B.rstrip('.txt')), 'w') as f:
        f.writelines(resultDataLst)
 
if __name__ == '__main__':
    fire.Fire()
 
