#!/usr/bin/env python

##################################################
# Copyright (c) 2023 Genome Research Ltd.

# Author: CASM/Cancer IT <cgphelp@sanger.ac.uk>


# This file is part of hairpin-wrapper.


# hairpin-wrapper is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option) any
# later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
##################################################

# annotate vcf with output of AdditionalBAMStatistics
from __future__ import annotations
import sys
if not sys.version_info >= (3, 10):
    sys.exit('Python 3.10 or greater required!')
import vcfpy
import argparse
from dataclasses import dataclass

FIELD_START = 'Start'
FIELD_UNIQUE = 'Var_reads_unique'
FIELD_MAD_POS = 'MAD_var_pos_reads'
FIELD_SD_POS = 'SD_var_pos_reads'
FIELD_POS_USED_STATS = 'Var_pos_reads_used_stats'
FIELD_POS_PRIME = 'Var_pos_5_prime_15%_reads'
FIELD_MAD_NEG = 'MAD_var_neg_reads'
FIELD_SD_NEG = 'SD_var_neg_reads'
FIELD_NEG_USED_STATS = 'Var_neg_reads_used_stats'
FIELD_NEG_PRIME = 'Var_neg_5_prime_15%_reads'
FIELDS: Set[str] = {FIELD_START, FIELD_UNIQUE, FIELD_MAD_POS, FIELD_SD_POS, FIELD_POS_USED_STATS, FIELD_POS_PRIME, FIELD_MAD_NEG, FIELD_SD_NEG, FIELD_NEG_USED_STATS, FIELD_NEG_PRIME}


def cd_str_conv(x: str) -> Optional[float]:
    return float(x) if x != 'NA' else None


@dataclass(slots=True)
class HStat:
    start: int
    reads_unique: Optional[float]
    mad_pos: Optional[float]
    sd_pos: Optional[float]
    pos_used_stats: Optional[float]
    pos_prime: Optional[float]
    mad_neg: Optional[float]
    sd_neg: Optional[float]
    neg_used_stats: Optional[float]
    neg_prime: Optional[float]
    
    @classmethod
    def from_list(cls, index_map: dict[str, int], a: list[str]) -> HStat:
        return cls(
            start=int(a[index_map[FIELD_START]]),
            reads_unique=cd_str_conv(a[index_map[FIELD_UNIQUE]]),
            mad_pos=cd_str_conv(a[index_map[FIELD_MAD_POS]]),
            sd_pos=cd_str_conv(a[index_map[FIELD_SD_POS]]),
            pos_used_stats=cd_str_conv(a[index_map[FIELD_POS_USED_STATS]]),
            pos_prime=cd_str_conv(a[index_map[FIELD_POS_PRIME]]),
            mad_neg=cd_str_conv(a[index_map[FIELD_MAD_NEG]]),
            sd_neg=cd_str_conv(a[index_map[FIELD_SD_NEG]]),
            neg_used_stats=cd_str_conv(a[index_map[FIELD_NEG_USED_STATS]]),
            neg_prime=cd_str_conv(a[index_map[FIELD_NEG_PRIME]])
        )


def hairpin_tester(t: Hstat) -> bool:
    return (
        t.reads_unique >= 2
        and (
            (t.mad_pos is None and t.sd_neg is not None and t.sd_neg > 2)
            or (t.mad_neg is None and t.sd_pos is not None and t.sd_pos > 2)
            or (t.pos_used_stats > 1 and t.sd_pos is not None and t.sd_pos > 2)
            or (t.neg_used_stats > 1 and t.sd_neg is not None and t.sd_neg > 2)
        )
        and (
            t.pos_used_stats <= 1
            and t.neg_used_stats > 1
            and (
                t.neg_prime / t.neg_used_stats <= 0.9
                or (t.mad_neg > 0 and t.sd_neg >= 4)
            )
            or (
                t.neg_used_stats <= 1
                and t.pos_used_stats > 1
                and (
                    t.pos_prime / t.pos_used_stats <= 0.9
                    or (t.mad_pos > 0 and t.sd_pos >= 4)
                )
            )
            or (
                t.pos_used_stats > 1
                and t.neg_used_stats > 1
                and (
                    t.pos_prime / t.pos_used_stats <= 0.9
                    or (t.pos_used_stats > 2 and t.mad_pos > 2)
                    or (t.neg_used_stats > 1 and t.sd_neg > 10)
                )
                and (
                    t.neg_prime / t.neg_used_stats <= 0.9
                    or (t.neg_used_stats > 2 and t.mad_neg > 2)
                    or (t.pos_used_stats > 1 and t.sd_pos > 10)
                )
            )
        )
    )


def main(vcf_path, annovar_path, output_path):
    
    def hstat_partial(tokens: list[str]) -> HStat:
        return HStat.from_list(index_map=index_map, a=tokens)
        
    try:
        vr = vcfpy.Reader.from_path(vcf_path)
    except Exception as e:
        print(e)
        sys.exit('VCF file could not be read!')
    
    try:
        vr.header.add_filter_line(vcfpy.OrderedDict([('ID', 'HP'), ('Description', 'LCM Hairpin Filter v1.0.8')]))
    except Exception as e:
        print(e)
        sys.exit('Error while modifying VCF header!')
    
    try:
        vw = vcfpy.Writer.from_path(output_path, vr.header)
    except Exception as e:
        print(e)
        sys.exit('Error while getting handle for VCF output!')
        
    try:
        with open(annovar_path) as anv:
            a_head = anv.readline().split('\t')
            index_map = {field_key: field_index for field_index, field_key in enumerate(a_head) if field_key in FIELDS}
            
            for a, v in zip(anv, vr):
                a_stats = hstat_partial(a.split('\t'))
                assert a_stats.start == v.POS
                if not hairpin_tester(a_stats):
                    v.add_filter('HP')
                vw.write_record(v)
    except (TypeError, ValueError) as e:
        print(e)
        sys.exit('ANNOVAR misformatted!')
    except AssertionError as e:
        print(e)
        sys.exit('VCF and ANNOVAR mismatch at postion VCF: {}, ANNOVAR: {}'.format(v.POS, a_stats.start))  # not done yet
    finally:
        vr.close()
        vw.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("annovar", help="input annovar")
    parser.add_argument("vcf", help="input vcf")
    parser.add_argument("output", help="output path")
    args = parser.parse_args()
    
    main(vcf_path=args.vcf, annovar_path=args.annovar, output_path=args.output)
