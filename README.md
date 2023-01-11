# hairpin_annotation

Project for centrally supported version of Mathijs Sanders' hairpin flagging algorithms, known as "Mathijs' scripts"

### Background

CLI for statistical detection and flagging of variants caused by hairpin/cruciform artifacts in LCM sequencing, made at the request of scientists. Previously, scientists were performing this task with diffuse versions of a small pipeline built by Mathijs and added to by others over many years. This repository brings together the components of that pipeline, strips out the extraneous functionality, and packages them into a single command for ease of use. The components are inherited and remain in their original form - this is `runScriptImitateANNOVAR.sh` and `additionalBamStatistics.jar`. The parent repositories can be found [here](https://github.com/MathijsSanders/SangerLCMFiltering) and [here](https://github.com/MathijsSanders/AdditionalBAMStatistics) respectively. There is an associated paper [here](https://www.nature.com/articles/s41596-020-00437-6#Sec31); information on the calculated statistics can be found in the 'SNV filtering' section. The legacy code is reasonably efficient, but entirely unmaintainable. Ideally, we would entirely refactor the project, but a 'V2' has been promised by Mathijs so until that arrives refactoring is on hold (07/2022).

The various components that have been removed or pared down either produced statistics that the scientists do not utilise, or were program functionality which would be better placed elsewhere, such as (unnecessary with regard to function) prefiltering of input VCFs according to CPLM. Do one(ish) thing and do it well.

### Requirements

**Java** >= 8  
**Python** >= 3.10  
**samtools** == 1.14  
**pysam** == 0.19.1  
**vcfpy** == 0.13.4  

### Installation

clone repository and cd into bin/ and run the following:
```
module load python/3.10.1
python -m venv pyenv
source pyenv/bin/activate
pip install -r requirements.txt
deactivate
```

### Usage

```
hairpin 
-v input VCF path \
-b BAM path \
-o output VCF path \
[-g] specify genome build (hg37, hg38(default)) \
[-r] display available reference genomes \
[-h] display help manpage \
```

example bsub with suggested resource:
```
bsub -R "select[mem>8000] rusage[mem=8000] span[hosts=1]" -M8000 \
-o out.%J.log \
-e err.%J.log \
-n 20 \
hairpin \
-v VCF_PATH \
-b BAM_PATH \
-o VCF_OUTPUT_PATH \
-g "38"
```

### LICENSE

Copyright (c) 2023 Genome Research Ltd.

Author: CASM/Cancer IT <cgphelp@sanger.ac.uk>


This file is part of hairpin-wrapper.


hairpin-wrapper is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your option) any
later version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
details.
You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.