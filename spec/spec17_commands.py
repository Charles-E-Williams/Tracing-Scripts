class Benchmark:
	def __init__(self, test, train, ref):
		self.test = test
		self.train = train
		self.ref = ref

class Variant:
	def __init__(self, setup, execution):
		self.setup = setup.strip().split("\n")
		self.execution = execution.strip().split("\n")

benchmarks = \
{
"perlbench": Benchmark(
		Variant(
"""
cd /speccpu/6xx/600.perlbench_s/
cd ./data/all/input/
""",
"""
../../../600.perlbench_s -I. -I./lib ../../test/input/makerand.pl
"""
		),
		Variant(
"""
cd /speccpu/6xx/600.perlbench_s/
cd ./data/train/input/
""",
"""
../../../600.perlbench_s -I../../all/input/lib ../../all/input/diffmail.pl 2 550 15 24 23 100
../../../600.perlbench_s -I../../all/input/lib perfect.pl b 3
../../../600.perlbench_s -I. -I../../all/input/lib scrabbl.pl < scrabbl.in
../../../600.perlbench_s -I../../all/input/lib ../../all/input/splitmail.pl 535 13 25 24 1091
../../../600.perlbench_s -I. -I../../all/input/lib suns.pl
"""
		),
		Variant(
"""
cd /speccpu/6xx/600.perlbench_s/
cd ./data/all/input/
""",
"""
../../../600.perlbench_s -I./lib ../../refrate/input/checkspam.pl 2500 5 25 11 150 1 1 1 1
"""
		)  
    ),

"gcc": Benchmark(
		Variant(
"""
cd /speccpu/6xx/602.gcc_s/
""",
"""
./602.gcc_s data/test/input/t1.c -finline-limit=50000 -o t1.opts-O3_-finline-limit_50000.s1
"""
		),
		Variant(
"""
cd /speccpu/6xx/602.gcc_s/
""",
"""
./602.gcc_s data/train/input/200.c -O3 -finline-limit=50000 -o 200.opts-O3_-finline-limit_50000.s
./602.gcc_s data/train/input/scilab.c -O3 -finline-limit=50000 -o scilab.opts-O3_-finline-limit_50000.s
./602.gcc_s data/train/input/train01.c -O3 -finline-limit=50000 -o train01.opts-O3_-finline-limit_50000.s
"""
		),
		Variant(
"""
cd /speccpu/6xx/602.gcc_s/
""",
"""
./602.gcc_s data/refspeed/input/gcc-pp.c -O5 -fipa-pta -o gcc-pp.opts-O5_-fipa-pta.s
"""
		)  
    ),    
    
    
"mcf": Benchmark(
		Variant(
"""
cd /speccpu/6xx/605.mcf_s/
""",
"""
./605.mcf_s data/test/input/inp.in
"""
		),
        
		Variant(
"""
cd /speccpu/6xx/605.mcf_s/
""",
"""
./605.mcf_s data/train/input/inp.in
"""
		),
		Variant(
"""
cd /speccpu/6xx/605.mcf_s/
""",
"""
./605.mcf_s data/refspeed/input/inp.in
"""
		)
	),


"lbm": Benchmark(
		Variant(
"""
cd /speccpu/6xx/619.lbm_s/
""",
"""
./619.lbm_s 20 reference.dat 0 1 data/test/input/200_200_260_ldc.of
"""
		),
        
		Variant(
"""
cd /speccpu/6xx/619.lbm_s/
""",
"""
./619.lbm_s 300 reference.dat 0 1 data/train/input/200_200_260_ldc.of
"""
		),
		Variant(
"""
cd /speccpu/6xx/619.lbm_s/
""",
"""
./619.lbm_s 2000 reference.dat 0 0 data/refspeed/input/200_200_260_ldc.of
"""
		)
	),


"omnetpp": Benchmark(#hangs? 
		Variant(
"""
cd /speccpu/6xx/620.omnetpp_s/
cd ./data/test/input
""",
"""
../../../620.omnetpp_s -c General -r 0
"""
		),
        
		Variant(
"""
cd /speccpu/6xx/620.omnetpp_s/
cd ./data/train/input
""",
"""
../../../620.omnetpp_s -c General -r 0
"""
		),
		Variant(
"""
cd /speccpu/6xx/620.omnetpp_s/
cd ./data/refrate/input
""",
"""
../../../620.omnetpp_s -c General -r 0
"""
		)
	),

"xalancbmk": Benchmark(
		Variant(
"""
cd /speccpu/6xx/623.xalancbmk_s/
""",
"""
./623.xalancbmk_s -v  data/test/input/test.xml  data/test/input/xalanc.xsl
"""
		),
        
		Variant(
"""
cd /speccpu/6xx/623.xalancbmk_s/
""",
"""
./623.xalancbmk_s -v data/train/input/allbooks.xml  data/train/input/xalanc.xsl
"""
		),
		Variant(
"""
cd /speccpu/6xx/623.xalancbmk_s/
""",
"""
./623.xalancbmk_s -v data/refrate/input/t5.xml  data/refrate/input/xalanc.xsl
"""
		)
	),



"x264": Benchmark(
		Variant(
"""
cd /speccpu/6xx/625.x264_s/
""",
"""
./625.x264_s --dumpyuv 50 --frames 156 -o BuckBunny_New.264 data/test/input/BuckBunny.yuv 1280x720
"""
		),
        
		Variant(
"""
cd /speccpu/6xx/625.x264_s/
""",
"""
./625.x264_s --dumpyuv 50 --frames 142 -o BuckBunny_New.264 data/train/input/BuckBunny.yuv 1280x720
"""
		),
		Variant(
"""
cd /speccpu/6xx/625.x264_s/
""",
"""
./625.x264_s --seek 500 --dumpyuv 200 --frames 1250 -o BuckBunny_New.264 data/refrate/input/BuckBunny.yuv 1280x720
"""
		)
	),

"deepsjeng": Benchmark(
		Variant(
"""
cd /speccpu/6xx/631.deepsjeng_s/
""",
"""
./631.deepsjeng_s data/test/input/test.txt
"""
		),
        
		Variant(
"""
cd /speccpu/6xx/631.deepsjeng_s/
""",
"""
./631.deepsjeng_s data/train/input/train.txt
"""
		),
		Variant(
"""
cd /speccpu/6xx/631.deepsjeng_s/
""",
"""
./631.deepsjeng_s data/refspeed/input/ref.txt
"""
		)
	),


"imagick": Benchmark(
		Variant(
"""
cd /speccpu/6xx/638.imagick_s/
""",
"""
./638.imagick_s -limit disk 0 data/test/input/test_input.tga -shear 25 -resize 640x480 -negate -alpha Off test_output.tga
"""
		),
        
		Variant(
"""
cd /speccpu/6xx/638.imagick_s/
""",
"""
./638.imagick_s -limit disk 0 data/train/input/train_input.tga -resize 320x240 -shear 31 -edge 140 -negate -flop -resize 900x900 -edge 10 train_output.tga
"""
		),
		Variant(
"""
cd /speccpu/6xx/638.imagick_s/
""",
"""
./638.imagick_s -limit disk 0 data/refspeed/input/refspeed_input.tga -resize 817% -rotate -2.76 -shave 540x375 -alpha remove -auto-level -contrast-stretch 1x1% -colorspace Lab -channel R -equalize +channel -colorspace sRGB -define histogram:unique-colors=false -adaptive-blur 0x5 -despeckle -auto-gamma -adaptive-sharpen 55 -enhance -brightness-contrast 10x10 -resize 30% refspeed_output.tga
"""
		)
	),

"leela": Benchmark(
		Variant(
"""
cd /speccpu/6xx/641.leela_s/
""",
"""
./641.leela_s data/test/input/test.sgf
"""
		),
        
		Variant(
"""
cd /speccpu/6xx/641.leela_s/
""",
"""
./641.leela_s data/train/input/train.sgf
"""
		),
		Variant(
"""
cd /speccpu/6xx/641.leela_s/
""",
"""
./641.leela_s data/refrate/input/ref.sgf
"""
		)
	),

"nab": Benchmark(
		Variant(
"""
cd /speccpu/6xx/644.nab_s/
cd ./data/test/input/
""",
"""
../../../644.nab_s hkrdenq 1930344093 1000
"""
		),
        
		Variant(
"""
cd /speccpu/6xx/644.nab_s/
cd ./data/train/input/
""",
"""
../../../644.nab_s aminos 391519156 1000
../../../644.nab_s gcn4dna 1850041461 300
"""
		),
		Variant(
"""
cd /speccpu/6xx/644.nab_s/
cd ./data/refspeed/input/
""",
"""
../../../644.nab_s 3j1n 20140317 220
"""
		)
	),

"xz": Benchmark(
		Variant(
"""
cd /speccpu/6xx/657.xz_s/
""",
"""
./657.xz_s data/all/input/cpu2006docs.tar.xz 4 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1548636 1555348 0
"""
		),
        
		Variant(
"""
cd /speccpu/6xx/657.xz_s/
""",
"""
./657.xz_s data/all/input/input.combined.xz 40 a841f68f38572a49d86226b7ff5baeb31bd19dc637a922a972b2e6d1257a890f6a544ecab967c313e370478c74f760eb229d4eef8a8d2836d233d3e9dd1430bf 6356684 -1 8
"""
		),
		Variant(
"""
cd /speccpu/6xx/657.xz_s/
""",
"""
./657.xz_s data/all/input/cpu2006docs.tar.xz 6643 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1036078272 1111795472 4 
"""
		)
	)
}