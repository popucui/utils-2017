#!/usr/bin/env python
#coding=utf-8

VERSION='0.1.0'

import os,sys
import argparse,ConfigParser

parser = argparse.ArgumentParser(description='pipeline for Talent gene V2')

parser.add_argument('-i', help='config file, which store software & database used through whole pipeline')
parser.add_argument('-o', help='output root dir')
parser.add_argument('-fq1', help='left read file')
parser.add_argument('-fq2', help='right read file')
parser.add_argument('-n', help='sample name')
parser.add_argument('-q', help='base quality type. 1: phred64, 2: phred33', default=2, type=int, choices=[1,2])
parser.add_argument('-l', help='sample info file, which hold gender, name, report date etc.')
parser.add_argument('-adpt3', help="3' adapter seq default:TGGAATTCTCGGGTGCCA ", type=str, default='TGGAATTCTCGGGTGCCA')
parser.add_argument('-adpt5', help="5' adapter seq default:AGATCGGAAGAGCGTCGT ", type=str, default='AGATCGGAAGAGCGTCGT')
parser.add_argument('-bwaNT',help='number of thread for bwa alignment', default=2, type=int)
parser.add_argument('-gatkNT',help='number of thread for GATK realign', default=1, type=int)
parser.add_argument('-run', help='whether go through all steps at once, default: n(o)', default='n', type=str)
args = parser.parse_args()

if not os.path.exists(args.i):
    exit('Please check {0}'.format(args.i) )
config = ConfigParser.ConfigParser()
config.readfp(open(args.i))

#make all dirs
if not os.path.exists(args.o):
    os.system('mkdir {0}\ncd {0}'.format(args.o) )  ##now in ROOT dir
rootdir = os.path.realpath(args.o)
projectDirs = ['align', 'QC', 'report', 'shell', 'talant', 'Variant']
[os.system('mkdir {1}/{0}'.format(dir, rootdir) ) for dir in projectDirs if not os.path.exists('{1}/{0}'.format(dir, rootdir) ) ]

bindir = '{0}/bin/'.format(os.path.dirname(args.i) )

#QC
qcsh='''{bin}Filter filter -1 {fq1} -2 {fq2} -Q {baseQual} -o {root}/QC -C {samplename}_clean_1.fq.gz  -D {samplename}_clean_2.fq.gz -G -5 1
gunzip -c {root}/QC/{samplename}_clean_1.fq.gz | {bin}/cutadapt -a {adpt3}  -O 5 -o {root}/QC/{samplename}_clean_cutadapt_1.fq - >{root}/QC/{samplename}.R1.fastq.cutadaptor.log
gunzip -c {root}/QC/{samplename}_clean_2.fq.gz | {bin}/cutadapt -a {adpt5}  -O 5 -o {root}/QC/{samplename}_clean_cutadapt_2.fq - >{root}/QC/{samplename}.R2.fastq.cutadaptor.log
perl {bin}/filt_read_len.pl {root}/QC/{samplename}_clean_cutadapt_1.fq {root}/QC/{samplename}_clean_cutadapt_2.fq {root}/QC/{samplename}_clean_cutadapt_filt 50
'''.format(bin=bindir, fq1=args.fq1, fq2=args.fq2, baseQual=args.q,
    root=rootdir, samplename=args.n, adpt3=args.adpt3, adpt5=args.adpt5)
open('{0}/shell/QC.sh'.format(rootdir),'w' ).write(qcsh)
#print(config.get('software', 'bwa') )
#print(rootdir)


#alignment
alignsh='''{bwa}  mem  -t {bwaNT} {ref} {root}/QC/{samplename}_clean_cutadapt_filt_1.fq {root}/QC/{samplename}_clean_cutadapt_filt_2.fq | {samtools} view  -b  -F 0x100 -T  {ref} - > {root}/align/{samplename}.bam
{samtools} view  -h  {root}/align/{samplename}.bam | awk '{{if($1~/@/){{print}}else{{if(!($6~/H/ && $5>25 )){{print $0}}}}}}' |{samtools} view -b  -T  {ref} - -o {root}/align/{samplename}.bf.bam
java -Xmx3g -XX:MaxPermSize=512m -XX:-UseGCOverheadLimit -jar {picard} FixMateInformation I={root}/align/{samplename}.bf.bam  O={root}/align/{samplename}.bftmp.bam TMP_DIR={root}/align/tmp SO=coordinate VALIDATION_STRINGENCY=SILENT
mv -f {root}/align/{samplename}.bftmp.bam {root}/align/{samplename}.bf.bam
java -Xmx3g -XX:MaxPermSize=512m -XX:-UseGCOverheadLimit -jar {picard}  AddOrReplaceReadGroups I={root}/align/{samplename}.bf.bam  O={root}/align/{samplename}.add.bam ID={samplename} LB={samplename} SM={samplename}  PL=illumina PU={samplename} CN=gene TMP_DIR={root}/align/tmp  SO=coordinate VALIDATION_STRINGENCY=SILENT
{samtools} calmd -b  {root}/align/{samplename}.add.bam {ref} >{root}/align/{samplename}.sort.tmp.bam
{samtools} index {root}/align/{samplename}.sort.tmp.bam
java -Xmx4g  -jar {gatk}  -T RealignerTargetCreator -R  {ref} -nt {gatkNT} -I {root}/align/{samplename}.sort.tmp.bam -o {root}/align/{samplename}.sort.intervals -known {known1} -known {known2}
java -Xmx4g  -jar {gatk}  -T IndelRealigner -R {ref}   -I {root}/align/{samplename}.sort.tmp.bam -o {root}/align/{samplename}.sort.bam -targetIntervals  {root}/align/{samplename}.sort.intervals   -maxInMemory 300000  -known  {known1} -known {known2}
awk '{{if(NR>1){{print $1"\\t"$2-1"\\t"$3}}}}' {insert_bed} >{root}/align/insert2_bed
{samtools} depth -d 10000000 -b {root}/align/insert2_bed {root}/align/{samplename}.sort.bam  >{root}/align/{samplename}.primer.depth.xls
perl {bin}/reads_Depth_Coverage/depth.pl {insert_bed} {root}/align/{samplename}.primer.depth.xls {root}/align {samplename}.primer
'''.format( bwa=config.get('software', 'bwa'), ref=config.get('database', 'ref'),
    root=rootdir, samplename=args.n, samtools=config.get('software', 'samtools'),
    picard=config.get('software', 'picard'), gatk=config.get('software', 'GATK'),
    bwaNT=args.bwaNT, gatkNT=args.gatkNT, known1=config.get('database', 'know1'),
    known2=config.get('database', 'know2'), insert_bed=config.get('database', 'insert_bed'), bin=bindir
    )
open('{0}/shell/align.sh'.format(rootdir),'w' ).write(alignsh)

#call variant
variantsh='''awk 'NR>1'   {insert_bed} > {root}/Variant/insert.bed
java -Xmx4g -jar  -jar {gatk}  -T  UnifiedGenotyper -dcov 1000000 -nt {gatkNT} -minIndelFrac 0.15 -glm BOTH -l INFO -R  {ref} -I {root}/align/{samplename}.sort.bam -o {root}/Variant/{samplename}.vcf -L {root}/Variant/insert.bed
java -Xmx4g -jar  -jar {gatk}  -T VariantFiltration -R {ref} -o {root}/Variant/{samplename}.filt.vcf --variant {root}/Variant/{samplename}.vcf --filterExpression "MQ0 >= 4 && ((MQ0 / (1.0 * DP)) > 0.1) " --filterName "HARD_TO_VALIDATE"  --filterExpression "DP < 10 || QD < 2" --filterName "LOW_READ_SUPPORT" 
awk '{{if(NR>1){{print $1"\\t"$2-1"\\t"$3}}}}' {insert_bed} >{root}/Variant/insert2_bed
{samtools}  mpileup  -A -d 10000000 -q 10 -f {ref} -l {root}/Variant/insert2_bed {root}/align/{samplename}.sort.bam  > {root}/Variant/{samplename}.pileup
{bin}/pileup_analyse {root}/Variant/{samplename}.pileup {root}/Variant/{samplename}.pileup.out
'''.format(insert_bed=config.get('database', 'insert_bed'), root=rootdir, 
    gatkNT=args.gatkNT, gatk=config.get('software', 'GATK'), bin=bindir,
    ref=config.get('database', 'ref'), samplename=args.n, samtools=config.get('software', 'samtools')
    )
open('{0}/shell/Variant.sh'.format(rootdir),'w' ).write(variantsh)

#talent annote
talantsh='''{bin}/talant_gene_annnot/talant_mark -i {root}/Variant/{samplename}.filt.vcf -d {bin}/talant_gene_annnot/Logicla_Mathematical.Dat  -o {root}/talant  -p {samplename}.Logicla_Mathematical
{bin}/talant_gene_annnot/talant_mark -i {root}/Variant/{samplename}.filt.vcf -d  {bin}/talant_gene_annnot/Bodily_Kinesthetic.Dat -o {root}/talant  -p {samplename}.Bodily_Kinesthetic
{bin}/talant_gene_annnot/talant_mark -i {root}/Variant/{samplename}.filt.vcf -d  {bin}/talant_gene_annnot/Growing_health.Dat -o {root}/talant  -p {samplename}.Growing_health
{bin}/talant_gene_annnot/talant_mark -i {root}/Variant/{samplename}.filt.vcf -d  {bin}/talant_gene_annnot/Interpersonal.Dat -o {root}/talant  -p {samplename}.Interpersonal
{bin}/talant_gene_annnot/talant_mark -i {root}/Variant/{samplename}.filt.vcf -d  {bin}/talant_gene_annnot/Introspection.Dat -o {root}/talant  -p {samplename}.Introspection
{bin}/talant_gene_annnot/talant_mark -i {root}/Variant/{samplename}.filt.vcf -d  {bin}/talant_gene_annnot/Linguistic.Dat -o {root}/talant  -p {samplename}.Linguistic
{bin}/talant_gene_annnot/talant_mark -i {root}/Variant/{samplename}.filt.vcf -d  {bin}/talant_gene_annnot/music.Dat  -o {root}/talant  -p {samplename}.music
{bin}/talant_gene_annnot/talant_mark -i {root}/Variant/{samplename}.filt.vcf -d  {bin}/talant_gene_annnot/nutrition.Dat -o {root}/talant  -p {samplename}.nutrition
{bin}/talant_gene_annnot/talant_mark -i {root}/Variant/{samplename}.filt.vcf -d  {bin}/talant_gene_annnot/Spatial.Dat -o {root}/talant  -p {samplename}.Spatial
{bin}/talant_gene_annnot/grow_genetype -i {root}/Variant/{samplename}.filt.vcf -d {bin}/talant_gene_annnot/grow.genetype.Dat  -o {root}/talant  -p {samplename}.grow
perl {bin}/draw/draw_value.pl  -i {root}/talant/{samplename}.Logicla_Mathematical.value.xls  -o {root}/talant -p {samplename}.Logicla_Mathematical
perl {bin}/draw/draw_value.pl  -i {root}/talant/{samplename}.Bodily_Kinesthetic.value.xls  -o {root}/talant -p {samplename}.Bodily_Kinesthetic
perl {bin}/draw/draw_value.pl  -i {root}/talant/{samplename}.Growing_health.value.xls  -o {root}/talant -p {samplename}.Growing_health
perl {bin}/draw/draw_value.pl  -i {root}/talant/{samplename}.Interpersonal.value.xls -o {root}/talant -p {samplename}.Interpersonal
perl {bin}/draw/draw_value.pl  -i {root}/talant/{samplename}.Introspection.value.xls  -o {root}/talant -p {samplename}.Introspection
perl {bin}/draw/draw_value.pl  -i {root}/talant/{samplename}.Linguistic.value.xls -o {root}/talant -p {samplename}.Linguistic
perl {bin}/draw/draw_value.pl  -i {root}/talant/{samplename}.music.value.xls -o {root}/talant -p {samplename}.music
perl {bin}/draw/draw_value.pl  -i {root}/talant/{samplename}.nutrition.value.xls -o {root}/talant -p {samplename}.nutrition
perl {bin}/draw/draw_value.pl  -i {root}/talant/{samplename}.Spatial.value.xls -o {root}/talant -p {samplename}.Spatial
{bin}/talant_gene_annnot/drug_annot -i {root}/Variant/{samplename}.filt.vcf -d {bin}/talant_gene_annnot/Drug.Dat -o {root}/talant -p {samplename}.drug
perl {bin}/draw/draw_radar.pl {root}/talant {root}/talant {samplename}
convert -density 300 {root}/talant/{samplename}.radar.pdf {root}/talant/{samplename}.radar.png
'''.format(bin=bindir, root=rootdir, samplename=args.n, )
open('{0}/shell/talant.sh'.format(rootdir),'w' ).write(talantsh)

#report
reportsh='''cp -r {bin}/report/picture {root}/report
cp {root}/talant/{samplename}*png {root}/report/picture
perl {bin}/data_stat.pl {root}/align/{samplename}.primer_reads_Depth_Coverage.stat {root}/align/{samplename}.primer_aveage_depth.stat {samplename} >{root}/report/target_data_stat.txt
cp {root}/Variant/{samplename}.filt.vcf {root}/report/{samplename}.vcf
{bin}/report/talant_report  -o {root}/report -p {samplename} -g  {root}/talant/{samplename}.grow.genetype.xls -d {root}/talant/{samplename}.drug.genetype.xls -l {sampleinfo}
cp {root}/align/{samplename}.primer_bed_Depth_Coverage.stat.xls  {root}/report
cp {root}/Variant/{samplename}.filt.vcf {root}/report/{samplename}.vcf
sh {bin}/report/html2pdf.sh {root}/report/{samplename}.report.html {root}/report/{samplename}.report.pdf
'''.format(bin=bindir, root=rootdir, samplename=args.n, sampleinfo=args.l)
open('{0}/shell/report.sh'.format(rootdir),'w' ).write(reportsh)

#Clean up
cleansh='''rm {root}/QC/{samplename}_clean_cutadapt_filt_1.fq {root}/QC/{samplename}_clean_cutadapt_filt_2.fq {root}/QC/{samplename}_clean_1.fq.gz {root}/QC/{samplename}_clean_2.fq.gz {root}/QC/{samplename}_clean_cutadapt_1.fq {root}/QC/{samplename}_clean_cutadapt_2.fq
rm {root}/align/*bam
rm {root}/Variant/{samplename}.pileup
'''.format(root=rootdir, samplename=args.n)
open('{0}/shell/Clean.sh'.format(rootdir),'w' ).write(cleansh)

#run ALL step
allstepsh='''echo -e Start Filter FQ at  `date +%y-%m-%d.%H:%M:%S` "\\n"
sh {root}/shell/QC.sh >{root}/shell/QC.sh.log 2>&1
echo -e Finish Filter FQ at `date +%y-%m-%d.%H:%M:%S` "\\n"

echo -e Start Align  at  `date +%y-%m-%d.%H:%M:%S` "\\n"
sh {root}/shell/align.sh >{root}/shell/align.sh.log 2>&1
echo -e Finish Align  at  `date +%y-%m-%d.%H:%M:%S` "\\n"
echo -e Start Call Variant  at  `date +%y-%m-%d.%H:%M:%S` "\\n"
sh {root}/shell/Variant.sh >{root}/shell/Variant.sh.log 2>&1
echo -e Finish Call Variant  at  `date +%y-%m-%d.%H:%M:%S` "\\n"

echo -e Star talant at  `date +%y-%m-%d.%H:%M:%S` "\\n"
sh  {root}/shell/talant.sh >{root}/shell/talant.sh.log 2>&1 
echo -e Finish talant at  `date +%y-%m-%d.%H:%M:%S` "\\n"

echo -e Star report at  `date +%y-%m-%d.%H:%M:%S` "\\n"
sh  {root}/shell/report.sh >{root}/shell/report.sh.log 2>&1 
echo -e Finish  report at  `date +%y-%m-%d.%H:%M:%S` "\\n"

# echo -e Star Clean data  at  `date +%y-%m-%d.%H:%M:%S` "\\n"
# sh {root}/shell/Clean.sh >{root}/shell/Clean.sh.log 2>&1 
# echo -e Finish Clean data  at  `date +%y-%m-%d.%H:%M:%S` "\\n"
'''.format(root=rootdir)
open('{0}/shell/All_step.sh'.format(rootdir),'w' ).write(allstepsh)

if args.run.lower() == 'y':
    os.system('sh {0}/shell/All_step.sh &'.format(rootdir) )