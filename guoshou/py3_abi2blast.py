#!/usr/bin env python
#coding=utf-8


import sys,os
import json
from abifpy import Trace
import argparse
import logging
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.CRITICAL)

parser = argparse.ArgumentParser(description='detect hetero sites directly from ab1 file')
parser.add_argument('--skipnum', type=int, default = 40, help='#Num of base to skip at both sides')
parser.add_argument('--tracemin', type=int, default = 100, help='min trace value required for a valid base calling')
parser.add_argument('--similtymin', type=float, default = 0.2, help='min ratio of two trace value for a potential hetero site')
parser.add_argument('--rawseq', help='raw sequencing result, which contains all .ab1 and .seq result of ONE individual, dir name should be TF number')
parser.add_argument('--debug',help='whether print additioanl info or not',default='n',choices=['y','n','Y','N'])
args = parser.parse_args()

SKIP_BASE_NUM = args.skipnum
TRACE_THRESHOLD = args.tracemin
SIMILTY_THRESHOLD = args.similtymin

DATABASE = './database'
refSeq = os.path.join(DATABASE, 'tumor_ref.fa')
#gene2locus = os.path.join(DATABASE, 'genelocus.json')
assert os.path.exists(refSeq)
#assert os.path.exists(gene2locus)

baseOrderDict = {
    0:'G',
    1:'A',
    2:'T',
    3:'C'
}
assert os.path.exists(args.rawseq)
name = os.path.basename(os.path.realpath(args.rawseq)) 
traceFiles = sorted([f for f in os.listdir(args.rawseq) if f.endswith('.ab1') ] )
traceFiles = [os.path.join(args.rawseq,f) for f in traceFiles]
seqFiles = []
for tracef in traceFiles:
    seqFileName = os.path.basename(tracef).replace('.ab1', '.seq')
    gstrace = Trace(tracef)
    gstrace.export(out_file = os.path.join(args.rawseq,seqFileName), fmt='fasta')
    seqFiles.append(seqFileName)
seqFiles = sorted( seqFiles )
seqFiles = [os.path.join(args.rawseq,f) for f in seqFiles]

logging.debug(seqFiles)
logging.debug(traceFiles)

def calSimilty(numList):
    import numpy as np
    return np.std(numList, dtype=np.float64) / np.mean(numList)

def getSecondLarge(tval):
    #if len(set(tval) ) < len(tval):
    #    print 'trace values not unique :{0}'.format(tval)
    #assert len(set(tval) ) == len(tval), 'trace values not unique, should call hetero base manually!:{0}'.format(tval)
    val = sorted(tval)[2] #trace value should be a 4 elements list, get the second largest
    return tval.index(val)



gene2Locus = {
    'BRCA1': {'rs1799950':'123520', 'rs1799949':'124535' },
    'BRCA2': {'rs1801499':'21723'},
    'CYP1B1': {'rs1800440':'10106'},
    'MTMR3': {'rs36600':'58433'},
    'RAD23BKLF4': {'rs817826':'10026'},
    'FTO': {'rs9939609 ':'87653'},
    'TERT': {'rs2736100':'13647'},
    'TP53': {'rs1042522':'16397'},
    'HLADQ': {'rs9275319':'3001'}
}

def main(trace,seq,gene2locus):
    '''
    tracefile, seq, make sure trace and seq correspend to each other correctly
    return heterosite{}
    '''
    heteroSite = {}
    gft2base = {}
    st = Trace(trace)
    startBase = SKIP_BASE_NUM
    endBase = len(st.seq) - SKIP_BASE_NUM
    st.basepos = st.get_data('PLOC1')
    st.basecalls = st.seq
    st.tracesamps = {
        'G':(),
        'A':(),
        'T':(),
        'C':()
    }
    st.tracesamps['G'],st.tracesamps['A'],st.tracesamps['T'],st.tracesamps['C'] = st.get_data('DATA9'), st.get_data('DATA10'), st.get_data('DATA11'), st.get_data('DATA12')
    #detect hetero base
    i = 0
    for basePos in st.basepos[startBase:endBase]:
        #base posGATC
        i += 1
        tracePos = [
        st.tracesamps['G'][basePos],
        st.tracesamps['A'][basePos],
        st.tracesamps['T'][basePos],
        st.tracesamps['C'][basePos] ]
        if max(tracePos) < TRACE_THRESHOLD:
            continue
        stdMn = calSimilty(sorted(tracePos, reverse=True)[:2] ) #calculate the first two largest trace value's similarity by formula: std / mean
        if stdMn > SIMILTY_THRESHOLD:
            continue
        altBase = baseOrderDict[getSecondLarge(tracePos) ]
        heteroPos = startBase + i
        if heteroPos not in heteroSite:
            heteroSite[heteroPos] = [st.basecalls[startBase+i-1], altBase ]
        else:
            pass 
        if args.debug.lower() == 'y':
            print ('{orgbasePos}\t{pos}\t{base}\t{G}\t{A}\t{T}\t{C}\t{stdMn}\t{altBase}'.format(base = st.basecalls[startBase+i-1], G = st.tracesamps['G'][basePos],
                A = st.tracesamps['A'][basePos],
                T = st.tracesamps['T'][basePos],
                C = st.tracesamps['C'][basePos],
                stdMn = stdMn,
                pos = startBase+i,
                orgbasePos = basePos,altBase = altBase))
    
    #run blastn
    cmd = 'blastn -query "{0}" -db {1}   -evalue 0.01 -outfmt  "6 qseqid sseqid qstart qend sstart send qseq sseq btop"   -num_threads 8 -task megablast -max_target_seqs 1'.format(seq, refSeq)
    logging.debug(cmd)
    blastRes = os.popen(cmd).read()
    #extract base content
    qseqid,sseqid,qstart,qend,sstart,send,qseq,sseq,btop = blastRes.rstrip().split('\t') 
    assert sseqid  in gene2locus, '{0} not valid gene id'.format(sseqid)
    for gftid,cord in gene2locus[sseqid ].items():
        if (int(sstart) <= int(cord) <= int(send) ):
            #hit within range
            pos = int(qstart) + int(cord) - int(sstart)
            if pos in heteroSite: #encounter a hetero site
                gft2base[gftid] = ''.join(heteroSite[pos])
            else:
                gft2base[gftid] = '{0}{0}'.format(qseq[int(cord) - int(sstart) - 1 ])
        else:
            #hit W/O range
            pass
    return gft2base

# locus2base = {}
# locus2base['results'] = []
for idx, trace in enumerate(traceFiles):
    gft2base = main(trace, seqFiles[idx], gene2Locus)
    print('{0}\t{1}'.format(os.path.basename(trace), gft2base ) )

