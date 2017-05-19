#!/usr/bin/env perl
use strict;

use Storable qw(store retrieve);
use utf8;
use Getopt::Long;




my $hash_tmp = retrieve ("$ARGV[0]");

foreach my $i (sort keys %$hash_tmp){
    print $i,"\t",$hash_tmp->{$i},"\n";
}
