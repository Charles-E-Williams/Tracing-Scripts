
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
	
"gcc": Benchmark(
		Variant(
"""
cd /speccpu/4xx/403.gcc/
""",
"""
./403.gcc data/test/input/cccp.i -o cccp.s
"""
		),
		Variant(
"""
cd /speccpu/4xx/403.gcc/
""",
"""
./403.gcc data/train/input/integrate.i -o integrate.s
"""
		),
		Variant(
"""
cd /speccpu/4xx/403.gcc/
""",
"""
./403.gcc data/ref/input/166.i -o 166.s
"""
		)
	),


"mcf": Benchmark(
		Variant(
"""
cd /speccpu/4xx/429.mcf/
""",
"""
./429.mcf data/test/input/inp.in
"""
		),
        
		Variant(
"""
cd /speccpu/4xx/429.mcf/
""",
"""
./429.mcf data/train/input/inp.in
"""
		),
		Variant(
"""
cd /speccpu/4xx/429.mcf/
""",
"""
./429.mcf data/ref/input/inp.in
"""
		)
	),


"perlbench": Benchmark( #hangs?
		Variant(
"""
cd /speccpu/4xx/400.perlbench/
cd ./data/all/input/
""",
"""
../../../400.perlbench -I. -I./lib ../../test/input/test.pl
"""
		),
		Variant(
"""
cd /speccpu/4xx/400.perlbench/
cd ./data/train/input/
""",
"""
../../../400.perlbench -I../../all/input/lib ../../all/input/diffmail.pl 2 550 15 24 23 100
"""
		),
		Variant(
"""
cd /speccpu/4xx/400.perlbench/
cd ./data/all/input/
""",
"""
../../../400.perlbench -I./lib ../../ref/input/checkspam.pl 2500 5 25 11 150 1 1 1 1
"""
		)
	),

	"libquantum": Benchmark(
		Variant(
"""
cd /speccpu/4xx/462.libquantum/
""",
"""
./462.libquantum 33 5
"""
		),
		Variant(
"""
cd /speccpu/4xx/462.libquantum/
""",
"""
./462.libquantum 143 25
"""
		),
		Variant(
"""
cd /speccpu/4xx/462.libquantum/
""",
"""
./462.libquantum 1397 8
"""
		)
	),

	"xalancbmk": Benchmark(
		Variant(
"""
cd /speccpu/4xx/483.xalancbmk/
""",
"""
./483.xalancbmk -v data/test/input/test.xml data/test/input/xalanc.xsl
"""
		),
		Variant(
"""
cd /speccpu/4xx/483.xalancbmk/
""",
"""
./483.xalancbmk -v data/train/input/allbooks.xml data/train/input/xalanc.xsl
"""
		),
		Variant(
"""
cd /speccpu/4xx/483.xalancbmk/
""",
"""
./483.xalancbmk -v data/ref/input/t5.xml data/ref/input/xalanc.xsl
"""
		)
	),

	"omnetpp": Benchmark(
		Variant(
"""
cd /speccpu/4xx/471.omnetpp/
""",
"""
./471.omnetpp -f data/test/input/omnetpp.ini
"""
		),
		Variant(
"""
cd /speccpu/4xx/471.omnetpp/
""",
"""
./471.omnetpp -f data/train/input/omnetpp.ini
"""
		),
		Variant(
"""
cd /speccpu/4xx/471.omnetpp/
""",
"""
./471.omnetpp -f data/ref/input/omnetpp.ini
"""
		)
	),

	"bzip2": Benchmark(
		Variant(
"""
cd /speccpu/4xx/401.bzip2/
""",
"""
./401.bzip2 data/all/input/input.program 5
"""
		),
		Variant(
"""
cd /speccpu/4xx/401.bzip2/
""",
"""
./401.bzip2 data/all/input/input.program 10
./401.bzip2 data/train/input/byoudoin.jpg 5
./401.bzip2 data/all/input/input.combined 80
"""
		),
		Variant(
"""
cd /speccpu/4xx/401.bzip2/
""",
"""
./401.bzip2 data/all/input/input.program 280
"""
		)
	),

	"hmmer": Benchmark(
		Variant(
"""
cd /speccpu/4xx/456.hmmer/
""",
"""
./456.hmmer --fixed 0 --mean 325 --num 45000 --sd 200 --seed 0 data/test/input/bombesin.hmm
"""
		),
		Variant(
"""
cd /speccpu/4xx/456.hmmer/
""",
# source: https://rootfriend.tistory.com/entry/Spec-INT-2006-command-line-arguments
"""
./456.hmmer --fixed 0 --mean 425 --num 85000 --sd 300 --seed 0 data/train/input/leng100.hmm
"""
		),
		Variant(
"""
cd /speccpu/4xx/456.hmmer/
""",
# source: https://github.com/ccelio/Speckle/blob/master/commands/456.hmmer.ref.cmd
"""
./456.hmmer --fixed 0 --mean 500 --num 500000 --sd 350 --seed 0 data/ref/input/retro.hmm
"""
		)
	),

	"astar": Benchmark(
		Variant(
"""
cd /speccpu/4xx/473.astar/
cd ./data/test/input/
""",
"""
../../../473.astar lake.cfg
"""
		),
		Variant(
"""
cd /speccpu/4xx/473.astar/
cd ./data/train/input/
""",
"""
../../../473.astar BigLakes1024.cfg
../../../473.astar rivers1.cfg
"""
		),
		Variant(
"""
cd /speccpu/4xx/473.astar/
cd ./data/ref/input/
""",
# source: https://github.com/ccelio/Speckle/blob/master/commands/473.astar.ref.cmd
"""
../../../473.astar rivers.cfg
"""
		)
	),

	"sjeng": Benchmark(
		Variant(
"""
cd /speccpu/4xx/458.sjeng/
""",
"""
./458.sjeng data/test/input/test.txt
"""
		),
		Variant(
"""
cd /speccpu/4xx/458.sjeng/
""",
"""
./458.sjeng data/train/input/train.txt
"""
		),
		Variant(
"""
cd /speccpu/4xx/458.sjeng/
""",
"""
./458.sjeng data/ref/input/ref.txt
"""
		)
	),

	"h264ref": Benchmark(
		Variant(
"""
cd /speccpu/4xx/464.h264ref/
cd ./data/test/input/
""",
"""
../../../464.h264ref -d foreman_test_encoder_baseline.cfg
"""
		),
		Variant(
"""
cd /speccpu/4xx/464.h264ref/
cd ./data/train/input/
""",
"""
../../../464.h264ref -d foreman_train_encoder_baseline.cfg
"""
		),
		Variant(
"""
cd /speccpu/4xx/464.h264ref/
cd ./data/ref/input/
""",
# source: https://github.com/ccelio/Speckle/blob/master/commands/464.h264ref.ref.cmd
"""
../../../464.h264ref -d foreman_ref_encoder_baseline.cfg
"""
		)
	),

	"gobmk": Benchmark(
		Variant(
"""
cd /speccpu/4xx/445.gobmk/
cd ./data/all/input
""",
"""
../../../445.gobmk --quiet --mode gtp < ../../test/input/capture.tst
"""
		),
		Variant(
"""
cd /speccpu/4xx/445.gobmk/
cd ./data/all/input
""",
"""
../../../445.gobmk --quiet --mode gtp < ../../train/input/arb.tst
../../../445.gobmk --quiet --mode gtp < ../../train/input/arend.tst
../../../445.gobmk --quiet --mode gtp < ../../train/input/arion.tst
../../../445.gobmk --quiet --mode gtp < ../../train/input/atari_atari.tst
../../../445.gobmk --quiet --mode gtp < ../../train/input/blunder.tst
../../../445.gobmk --quiet --mode gtp < ../../train/input/bluzco.tst
../../../445.gobmk --quiet --mode gtp < ../../train/input/nicklas2.tst
../../../445.gobmk --quiet --mode gtp < ../../train/input/nicklas4.tst
"""
		),
		Variant(
"""
cd /speccpu/4xx/445.gobmk/
cd ./data/all/input
""",
"""
../../../445.gobmk --quiet --mode gtp < ../../ref/input/trevord.tst
"""
		)
	),


	"milc": Benchmark(
		Variant(
"""
cd /speccpu/4xx/433.milc
""",
"""
./433.milc < data/test/input/su3imp.in
"""
		),
		Variant(
"""
cd /speccpu/4xx/433.milc
""",
"""
./433.milc < data/train/input/su3imp.in
"""
		),
		Variant(
"""
cd /speccpu/4xx/433.milc
""",
"""
./433.milc < data/ref/input/su3imp.in
"""
		)
	),

	"namd": Benchmark(
		Variant(
"""
cd /speccpu/4xx/444.namd
""",
"""
./444.namd --input data/all/input/namd.input --iterations 1 --output namd.out
"""
		),
		Variant(
"""
cd /speccpu/4xx/444.namd
""",
"""
./444.namd --input data/all/input/namd.input --iterations 1 --output namd.out
"""
		),
		Variant(
"""
cd /speccpu/4xx/444.namd
""",
"""
./444.namd --input data/all/input/namd.input --iterations 38 --output namd.out
"""
		)
	),

	"dealII": Benchmark(
		Variant(
"""
cd /speccpu/4xx/447.dealII
""",
"""
./447.dealII 8
"""
		),
		Variant(
"""
cd /speccpu/4xx/447.dealII
""",
"""
./447.dealII 10
"""
		),
		Variant(
"""
cd /speccpu/4xx/447.dealII
""",
"""
./447.dealII 23
"""
		)
	),

	"soplex": Benchmark(
		Variant(
"""
cd /speccpu/4xx/450.soplex
""",
"""
./450.soplex -m10000 data/test/input/test.mps
"""
		),
		Variant(
"""
cd /speccpu/4xx/450.soplex
""",
"""
./450.soplex -s1 -e -m5000 data/train/input/pds-20.mps
"""
		),
		Variant(
"""
cd /speccpu/4xx/450.soplex
""",
"""
./450.soplex -s1 -e -m45000 data/ref/input/pds-50.mps
"""
		)
	),

	"povray": Benchmark(
		Variant(
"""
cd /speccpu/4xx/453.povray
cd ./data/test/input/
""",
"""
../../../453.povray SPEC-benchmark-test.ini
"""
		),
		Variant(
"""
cd /speccpu/4xx/453.povray
cd ./data/train/input/
""",
"""
../../../453.povray SPEC-benchmark-train.ini
"""
		),
		Variant(
"""
cd /speccpu/4xx/453.povray
cd ./data/ref/input/
""",
"""
../../../453.povray SPEC-benchmark-ref.ini
"""
		)
	),


	"lbm": Benchmark(
		Variant(
"""
cd /speccpu/4xx/470.lbm
""",
"""
./470.lbm 20 reference.dat 0 1 data/test/input/100_100_130_cf_a.of
"""
		),
		Variant(
"""
cd /speccpu/4xx/470.lbm
""",
"""
./470.lbm 300 reference.dat 0 1 data/train/input/100_100_130_cf_b.of
"""
		),
		Variant(
"""
cd /speccpu/4xx/470.lbm
""",
"""
./470.lbm 3000 reference.dat 0 0 data/ref/input/100_100_130_ldc.of
"""
		)
	),


	"sphinx3": Benchmark(
		Variant(
"""
cd /speccpu/4xx/482.sphinx3
cd ./data/test/input/
""",
"""
../../../482.sphinx3 ctlfile . args.an4
"""
		),
		Variant(
"""
cd /speccpu/4xx/482.sphinx3
cd ./data/train/input/
""",
"""
../../../482.sphinx3 ctlfile . args.an4
"""
		),
		Variant(
"""
cd /speccpu/4xx/482.sphinx3
cd ./data/ref/input/
""",
"""
../../../482.sphinx3 ctlfile . args.an4
"""
		)
	)

}