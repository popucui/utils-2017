#coding=utf-8

import fire,json
import logging
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.CRITICAL)

def get_siteinfo(grow_file, rs2pdp_file, growjson_file):
    '''
    make grow siteinfo json from growinfo and rs2pdpid map
    input: 
        grow_file 
        rs2pdp_file
    output:
        growjson_file
    '''
    rs_dict = {}
    with open(rs2pdp_file) as f:
        rs2pdp_dict = json.load(f)
    with open(grow_file) as f:
        for line in f:
            temp = line.rstrip().split()
            phen2gn = temp[0].split(',')
            logging.debug(phen2gn)
            pheno,rs,genetp,_ = phen2gn
            if pheno not in rs_dict:
                rs_dict[pheno] = {}
            if rs not in rs_dict[pheno]:
                rs_dict[pheno][rs] = {}
            rs_dict[pheno][rs]['pdpid'] = rs2pdp_dict[rs]
            rs_dict[pheno][rs][genetp] = temp[5]
            rs_dict[pheno]['score2result'] = {
                0:'',
                1:'',
                2:''}
            rs_dict[pheno]['total_score'] = 0
            rs_dict[pheno]['result'] = ''
            rs_dict[pheno][rs]['chrm'], rs_dict[pheno][rs]['pos'],rs_dict[pheno][rs]['strand'] = temp[6:9]
    with open(growjson_file, 'w', encoding='utf8') as f:
        json.dump(rs_dict, f, ensure_ascii=False, indent=4)

def get_growres(grow_gtpe, growjson_file, gtest_result):
    '''
    calculate result for each section of GROW gene test
    input:
        grow_gtpe: TF2017012007.drug.genetype.xls
        growjson_file: grow template file,grow_3rd.json
    output:
        gtest_result: output result in json
    '''
    with open(growjson_file) as f:
        rs_dict = json.load(f)
    with open(grow_gtpe) as f:
        for line in f:
            temp = line.rstrip().split('\t')
            dsection, rs, gtype, _ = temp
            if gtype in rs_dict[dsection][rs]:
                rs_dict[dsection]['total_score'] += int(rs_dict[dsection][rs][gtype] )
                rs_dict[dsection][rs]['gtype'] = gtype
            elif gtype[::-1] in rs_dict[dsection][rs]:
                rs_dict[dsection]['total_score'] += int(rs_dict[dsection][rs][gtype[::-1] ] )
                rs_dict[dsection][rs]['gtype'] = gtype[::-1]
            else:
                logging.debug('can not find match for {0}'.format(line) )
                sys.exit()
    for dsection in rs_dict:
        max_score = (len(rs_dict[dsection].keys() ) - 3) * 2
        if rs_dict[dsection]['total_score'] >= max_score * 0.75:
            rs_dict[dsection]['result'] = rs_dict[dsection]['score2result']['2']
        elif rs_dict[dsection]['total_score'] < max_score * 0.25:
            rs_dict[dsection]['result'] = rs_dict[dsection]['score2result']['0']
        else:
            rs_dict[dsection]['result'] = rs_dict[dsection]['score2result']['1']
    with open(gtest_result, 'w', encoding='utf-8') as f:
        json.dump(rs_dict, f, ensure_ascii=False, indent=4, sort_keys=True)
            
            

if __name__ == '__main__':
    fire.Fire()