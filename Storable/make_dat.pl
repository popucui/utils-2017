#!/usr/bin/env perl
use strict;

use Storable qw(store retrieve);
use utf8;
use Getopt::Long;

my %hash_drug;
open OLD_DAT,$ARGV[0];

while (<OLD_DAT>){
    chomp;
    my @tmp = split /\t/;
    my $max_idx = $#tmp;
    $hash_drug{$tmp[0]} = join("\t", @tmp[1..$max_idx]);
}

store(\%hash_drug, $ARGV[1]);