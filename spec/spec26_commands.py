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
"xz": Benchmark(
		Variant(
"""
cd /speccpu/8xx/801.xz_s/
cd ./test/
""",
"""
../801.xz_s cpu2006docs.tar.xz 4 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1548636 1555348 0 > cpu2006docs.tar-4-0.out 2>> cpu2006docs.tar-4-0.err
../801.xz_s cpu2006docs.tar.xz 4 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1462248 1467400 1 > cpu2006docs.tar-4-1.out 2>> cpu2006docs.tar-4-1.err
../801.xz_s cpu2006docs.tar.xz 4 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1428548 1428556 2 > cpu2006docs.tar-4-2.out 2>> cpu2006docs.tar-4-2.err
../801.xz_s cpu2006docs.tar.xz 4 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1034828 1034836 3e > cpu2006docs.tar-4-3e.out 2>> cpu2006docs.tar-4-3e.err
../801.xz_s cpu2006docs.tar.xz 4 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1061968 1061976 4 > cpu2006docs.tar-4-4.out 2>> cpu2006docs.tar-4-4.err
../801.xz_s cpu2006docs.tar.xz 4 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 1034588 1034596 4e > cpu2006docs.tar-4-4e.out 2>> cpu2006docs.tar-4-4e.err
../801.xz_s cpu2006docs.tar.xz 1 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 650156 650160 0 > cpu2006docs.tar-1-0.out 2>> cpu2006docs.tar-1-0.err
../801.xz_s cpu2006docs.tar.xz 1 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 639996 640004 1 > cpu2006docs.tar-1-1.out 2>> cpu2006docs.tar-1-1.err
../801.xz_s cpu2006docs.tar.xz 1 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 637616 637624 2 > cpu2006docs.tar-1-2.out 2>> cpu2006docs.tar-1-2.err
../801.xz_s cpu2006docs.tar.xz 1 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 628996 629004 3e > cpu2006docs.tar-1-3e.out 2>> cpu2006docs.tar-1-3e.err
../801.xz_s cpu2006docs.tar.xz 1 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 631912 631920 4 > cpu2006docs.tar-1-4.out 2>> cpu2006docs.tar-1-4.err
../801.xz_s cpu2006docs.tar.xz 1 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 629064 629072 4e > cpu2006docs.tar-1-4e.out 2>> cpu2006docs.tar-1-4e.err
"""
		),
		Variant("""
""",
"""
"""
		),
		Variant(
"""
cd /speccpu/8xx/801.xz_s/
cd ./refspeed/
""",
"""
../801.xz_s cld.tar.xz 2700 19cf30ae51eddcbefda78dd06014b4b96281456e078ca7c13e1c0c9e6aaea8dff3efb4ad6b0456697718cede6bd5454852652806a657bb56e07d61128434b474 959312906 1042731420 8 > cld.tar-2700-8.out 2>> cld.tar-2700-8.err
"""
		)
	),

"sph_exa": Benchmark(
		Variant(
"""
cd /speccpu/8xx/803.sph_exa_s/
cd ./test/
""",
"""
../803.sph_exa_s -n 100 -s 0 -w 1 > sph_exa.out 2>> sph_exa.err
"""
		),
		Variant("""
""",
"""
"""
		),
		Variant(
"""
cd /speccpu/8xx/803.sph_exa_s/
cd ./refspeed/
""",
"""
../803.sph_exa_s -n 210 -s 24 -w 7 > sph_exa.out 2>> sph_exa.err
"""
		)
	),

"ntest": Benchmark(
		Variant(
"""
cd /speccpu/8xx/807.ntest_s/
cd ./test/
""",
"""
../807.ntest_s OneGame.ggf 10 6 > ntest.OneGame.10.6.out 2>> ntest.OneGame.10.6.err
"""
		),
		Variant("""
""",
"""
"""
		),
		Variant(
"""
cd /speccpu/8xx/807.ntest_s/
cd ./refspeed/
""",
"""
../807.ntest_s Othello.01e4.ggf 20 21 > ntest.Othello.01e4.20.21.out 2>> ntest.Othello.01e4.20.21.err
"""
		)
	),

"cactus": Benchmark(
		Variant(
"""
cd /speccpu/8xx/809.cactus_s/
cd ./test/
""",
"""
../809.cactus_s ShiftedGaugeWave.par > cactus.out 2>> cactus.err
"""
		),
		Variant("""
""",
"""
"""
		),
		Variant(
"""
cd /speccpu/8xx/809.cactus_s/
cd ./refspeed/
""",
"""
../809.cactus_s ShiftedGaugeWave.par > cactus.out 2>> cactus.err
"""
		)
	),

"tealeaf": Benchmark(
		Variant(
"""
cd /speccpu/8xx/811.tealeaf_s/
cd ./test/
""",
"""
../811.tealeaf_s > tea.stdout 2>> tea.err
"""
		),
		Variant("""
""",
"""
"""
		),
		Variant(
"""
cd /speccpu/8xx/811.tealeaf_s/
cd ./refspeed/
""",
"""
../811.tealeaf_s > tea.stdout 2>> tea.err
"""
		)
	),

"nab": Benchmark(
		Variant(
"""
cd /speccpu/8xx/816.nab_s/
cd ./test/
""",
"""
../816.nab_s --directory hkrdenq --seed 1930344093 --iterations 1000 > hkrdenq.1000.out 2>> hkrdenq.1000.err
"""
		),
		Variant("""
""",
"""
"""
		),
		Variant(
"""
cd /speccpu/8xx/816.nab_s/
cd ./refspeed/
""",
"""
../816.nab_s --directory 3j1n --seed 20140317 --iterations 220 --epoques 3 > 3j1n.220.3.out 2>> 3j1n.220.3.err
"""
		)
	),

"flac": Benchmark(
		Variant(
"""
cd /speccpu/8xx/817.flac_s/
cd ./test/
""",
"""
../817.flac_s -7V -f amp_podcast_11.wav -o amp_podcast_11.flac --no-preserve-modtime -j 1 > flac.amp_podcast_11.flac.out 2>> flac.amp_podcast_11.flac.err
../817.flac_s -a -f amp_podcast_11.flac -o amp_podcast_11.analysis.txt --no-preserve-modtime --delete-input-file -j 1 > flac.amp_podcast_11.analysis.txt.out 2>> flac.amp_podcast_11.analysis.txt.err
"""
		),
		Variant("""
""",
"""
"""
		),
		Variant(
"""
cd /speccpu/8xx/817.flac_s/
cd ./refspeed/
""",
"""
../817.flac_s -8Vep -f git_etiquette_stereo.wav -o git_etiquette_stereo1.flac --mid-side --replay-gain --keep-foreign-metadata --no-preserve-modtime -j 1 > flac.git_etiquette_stereo1.flac.out 2>> flac.git_etiquette_stereo1.flac.err
"""
		)
	),

"cppcheck": Benchmark(
		Variant(
"""
cd /speccpu/8xx/827.cppcheck_s/
cd ./test/
""",
"""
../827.cppcheck_s > testrunner_s.out 2>> testrunner_s.err
../cppcheck_s --file-list=check_file_list --cppcheck-build-dir=. -j 1 --platform=unix64 > cppcheck_s.raw.out 2>> cppcheck_s.raw.err
"""
		),
		Variant("""
""",
"""
"""
		),
		Variant(
"""
cd /speccpu/8xx/827.cppcheck_s/
cd ./refspeed/
""",
"""
../827.cppcheck_s --file-list=check_file_list -f --suppress=normalCheckLevelMaxBranches --checkers-report=report.txt --cppcheck-build-dir=src --disable=unusedFunction -j 1 --platform=unix64 > cppcheck_s.raw.out 2>> cppcheck_s.raw.err
"""
		)
	),

"abc": Benchmark(
		Variant(
"""
cd /speccpu/8xx/829.abc_s/
cd ./test/
""",
"""
../829.abc_s -F truthtable.in > truthtable.out 2>> truthtable.err
../829.abc_s -F riscv.in > riscv.out 2>> riscv.err
"""
		),
		Variant("""
""",
"""
"""
		),
		Variant(
"""
cd /speccpu/8xx/829.abc_s/
cd ./refspeed/
""",
"""
../829.abc_s -F ethernet-fraig.in > ethernet-fraig.out 2>> ethernet-fraig.err
"""
		)
	),

"vpr": Benchmark(
		Variant(
"""
cd /speccpu/8xx/834.vpr_s/
cd ./test/
""",
"""
../834.vpr_s stratixiv_arch.timing.xml murax_stratixiv_arch_timing.blif --place_algorithm bounding_box --RL_agent_placement off --max_criticality 0.0 --init_t 512 --alpha_t 0.75 --exit_t 1 --router_initial_timing all_critical --routing_failure_predictor off --route_chan_width 300 --max_router_iterations 20 --router_lookahead classic --initial_pres_fac 1.0 --pres_fac_mult 2.0 --astar_fac 1.5 --router_profiler_astar_fac 1.5 --seed 3 --sdc_file murax_stratixiv_arch_timing.sdc --pack_verbosity 0 --netlist_verbosity 0 --base_cost_type demand_only --inner_num 4 --read_initial_place_file ref_murax_stratixiv_arch_timing.init.place --place > murax_stratixiv_arch_timing.blif.out 2>> murax_stratixiv_arch_timing.blif.err
../834.vpr_s stratixiv_arch.timing.xml murax_stratixiv_arch_timing.blif --place_algorithm bounding_box --place_static_notiming_move_prob 50 25 25 --max_criticality 0.0 --router_initial_timing all_critical --routing_failure_predictor off --route_chan_width 300 --max_router_iterations 20 --router_lookahead classic --initial_pres_fac 1.0 --pres_fac_mult 2.0 --astar_fac 1.5 --router_profiler_astar_fac 1.5 --seed 3 --sdc_file murax_stratixiv_arch_timing.sdc --pack_verbosity 0 --netlist_verbosity 0 --place_file ref_murax_stratixiv_arch_timing.place --base_cost_type demand_only --analysis --route > murax_stratixiv_arch_timing.blif.out 2>> murax_stratixiv_arch_timing.blif.err
"""
		),
		Variant("""
""",
"""
"""
		),
		Variant(
"""
cd /speccpu/8xx/834.vpr_s/
cd ./refspeed/
""",
"""
../834.vpr_s stratixiv_arch.timing.xml wb_conmax_stratixiv_arch_timing.blif --place_algorithm bounding_box --place_static_notiming_move_prob 50 25 25 --max_criticality 0.0 --router_initial_timing all_critical --routing_failure_predictor off --route_chan_width 300 --max_router_iterations 30 --router_lookahead classic --initial_pres_fac 0.0009765625 --pres_fac_mult 2.0 --astar_fac 1.5 --router_profiler_astar_fac 1.5 --seed 3 --sdc_file wb_conmax_stratixiv_arch_timing.sdc --pack_verbosity 0 --netlist_verbosity 0 --base_cost_type demand_only --place_file ref_wb_conmax_stratixiv_arch_timing.place --analysis --route > wb_conmax_stratixiv_arch_timing.blif.out 2>> wb_conmax_stratixiv_arch_timing.blif.err
"""
		)
	),

"gem5": Benchmark(
		Variant(
"""
cd /speccpu/8xx/835.gem5_s/
cd ./test/
""",
"""
../835.gem5_s --stats-file=synthetic_traffic.py_LinearGenerator_100.stats.txt synthetic_traffic.py LinearGenerator 100 > synthetic_traffic.py_LinearGenerator_100.out 2>> synthetic_traffic.py_LinearGenerator_100.err
"""
		),
		Variant("""
""",
"""
"""
		),
		Variant(
"""
cd /speccpu/8xx/835.gem5_s/
cd ./refspeed/
""",
"""
../835.gem5_s --stats-file=bwaves-train-simpt-3-o3cpu.py.stats.txt bwaves-train-simpt-3-o3cpu.py > bwaves-train-simpt-3-o3cpu.py.out 2>> bwaves-train-simpt-3-o3cpu.py.err
"""
		)
	),

"diamond": Benchmark(
		Variant(
"""
cd /speccpu/8xx/838.diamond_s/
cd ./test/
""",
"""
../838.diamond_s blastp -q astral-scopedom-seqres-gd-sel-gs-bib-40-2.07.fa.gz -d astral-scopedom-seqres-gd-sel-gs-bib-40-2.07.fa.gz --fast --outfmt 6 qseqid sseqid slen mismatch gapopen qstart qend sstart send nident bitscore -o astral40.tsv -p 1 > astral-scopedom-seqres-gd-sel-gs-bib-40-2.07.fa.gz.out 2>> astral-scopedom-seqres-gd-sel-gs-bib-40-2.07.fa.gz.err
"""
		),
		Variant("""
""",
"""
"""
		),
		Variant(
"""
cd /speccpu/8xx/838.diamond_s/
cd ./refspeed/
""",
"""
../838.diamond_s blastp -q cRAP.fasta.gz -d swissprot.fasta --ultra-sensitive --index-chunks 4 --block-size 2.8 --masking seg --evalue 0.0005 --outfmt 6 qseqid sseqid slen mismatch gapopen qstart qend sstart send -o cRAP.tsv -p 1 > cRAP.fasta.gz.out 2>> cRAP.fasta.gz.err
"""
		)
	),

"minizinc": Benchmark(
		Variant(
"""
cd /speccpu/8xx/846.minizinc_s/
cd ./test/
""",
"""
../846.minizinc_s --stdlib-dir share/minizinc -r 214365 --output-mode json --solver share/minizinc/solvers/chuffed.msc -s -f radiation.mzn > radiation.mzn.out 2>> radiation.mzn.err
../846.minizinc_s --stdlib-dir share/minizinc -r 214365 --output-mode json --solver gecode_presolver -s tennis_problem.mzn > tennis_problem.mzn.out 2>> tennis_problem.mzn.err
"""
		),
		Variant("""
""",
"""
"""
		),
		Variant(
"""
cd /speccpu/8xx/846.minizinc_s/
cd ./refspeed/
""",
"""
../846.minizinc_s --stdlib-dir share/minizinc -r 214365 --output-mode json --solver gecode_presolver --solver-statistics roster-sickness.mzn small-4.dzn -p 1 > small-4.dzn.out 2>> small-4.dzn.err
"""
		)
	),

"ns3": Benchmark(
		Variant(
"""
cd /speccpu/8xx/853.ns3_s/
cd ./test/
""",
"""
../853.ns3_s tcp-pacing --isPacingEnabled=true --tracing=false --RngSeed=1 --RngRun=1 > tcp-pacing_0.out 2>> tcp-pacing_0.err
../853.ns3_s wifi-mixed-network --simulationTime=2 --RngSeed=1 --RngRun=1 > wifi-mixed-network_1.out 2>> wifi-mixed-network_1.err
"""
		),
		Variant("""
""",
"""
"""
		),
		Variant(
"""
cd /speccpu/8xx/853.ns3_s/
cd ./refspeed/
""",
"""
../853.ns3_s wifi-mixed-network --isUdp=1 --payloadSize=4096 --simulationTime=50 --RngSeed=1 --RngRun=1 > wifi-mixed-network_3.out 2>> wifi-mixed-network_3.err
"""
		)
	),

"graph500": Benchmark(
		Variant(
"""
cd /speccpu/8xx/854.graph500_s/
cd ./test/
""",
"""
../854.graph500_s -s 18 -e 16 -o bfs_test.bin -f 1 > bfs_test.bin.out 2>> bfs_test.bin.err
../854.graph500_s -m 62 -p 100 -q apsp_NYroad_62.bin -g 1 > apsp_NYroad_62.bin.out 2>> apsp_NYroad_62.bin.err
"""
		),
		Variant("""
""",
"""
"""
		),
		Variant(
"""
cd /speccpu/8xx/854.graph500_s/
cd ./refspeed/
""",
"""
../854.graph500_s -s 26 -e 16 -o bfs_refspeed.bin -f 1 > bfs_refspeed.bin.out 2>> bfs_refspeed.bin.err
"""
		)
	),

"namd": Benchmark(
		Variant(
"""
cd /speccpu/8xx/857.namd_s/
cd ./test/
""",
"""
../857.namd_s --input stmv.input --iterations 1 --output stmv.test.output > namd.out 2>> namd.err
"""
		),
		Variant("""
""",
"""
"""
		),
		Variant(
"""
cd /speccpu/8xx/857.namd_s/
cd ./refspeed/
""",
"""
../857.namd_s --input stmv.input --output stmv.ref.output --iterations 399 > namd.out 2>> namd.err
"""
		)
	),

"nest": Benchmark(
		Variant(
"""
cd /speccpu/8xx/867.nest_s/
cd ./test/
""",
"""
../867.nest_s --userargs=threads=1 --verbosity=FATAL cuba_stdp_spec.sli > cuba_stdp_spec.sli.out 2>> cuba_stdp_spec.sli.err
"""
		),
		Variant("""
""",
"""
"""
		),
		Variant(
"""
cd /speccpu/8xx/867.nest_s/
cd ./refspeed/
""",
"""
../867.nest_s --userargs=threads=1 --verbosity=FATAL microcircuit_spec.sli > microcircuit_spec.sli.out 2>> microcircuit_spec.sli.err
"""
		)
	),

"marian": Benchmark(
		Variant(
"""
cd /speccpu/8xx/872.marian_s/
cd ./test/
""",
"""
../872.marian_s --cpu-threads 1 -m model.alphas.npz -v vocab.spm vocab.spm --beam-size 1 --mini-batch 32 --maxi-batch 100 --maxi-batch-sort src -w 64 --skip-cost --gemm-type intgemm8 --intgemm-options precomputed-alpha standard-only --quiet --quiet-translation -i TildeMODEL-test.en --log TildeMODEL-test.log --log-level off -o TildeMODEL-test.out > run_TildeMODEL-test.out.out 2>> run_TildeMODEL-test.out.err
"""
		),
		Variant("""
""",
"""
"""
		),
		Variant(
"""
cd /speccpu/8xx/872.marian_s/
cd ./refspeed/
""",
"""
../872.marian_s --cpu-threads 1 -m model.alphas.npz -v vocab.spm vocab.spm --beam-size 8 --mini-batch 32 --maxi-batch 100 --maxi-batch-sort trg -w 64 --skip-cost --gemm-type intgemm8 --intgemm-options precomputed-alpha standard-only --quiet --quiet-translation -i EuroPat-spec-long.en --log EuroPat-spec.log --log-level off -o EuroPat-spec.out > run_EuroPat-spec.out.out 2>> run_EuroPat-spec.out.err
"""
		)
	),

"neutron": Benchmark(
		Variant(
"""
cd /speccpu/8xx/881.neutron_s/
cd ./test/
""",
"""
../881.neutron_s xsbench -s small -g 1000 -p 50000 > xsbench.small.out 2>> xsbench.small.err
../881.neutron_s rsbench -m event -l 100000 -p 2000 -P 2000 -d > rsbench.event.out 2>> rsbench.event.err
"""
		),
		Variant("""
""",
"""
"""
		),
		Variant(
"""
cd /speccpu/8xx/881.neutron_s/
cd ./refspeed/
""",
"""
../881.neutron_s rsbench -m history -s large -p 1500000 -P 300000 -W 35000 -l 60 -d > rsbench.history.out 2>> rsbench.history.err
"""
		)
	),
}
