#!/bin/bash

outputfmt='mrate_{1}-seed_{2}.route'
cityfile='compare_mrate.cities'

for seed in $(seq 1 10); do
	sed -i 's/^.* # seed/'$seed' # seed/g' $cityfile
 	output1=${outputfmt/'{2}'/$seed}
	mrate=25
	for i in $(seq 1 20); do
		echo 'Now running seed='$seed' , mrate='$mrate
		sed -i 's/^.* # migration ra/'$mrate' # migration ra/g' $cityfile
		output2=${output1/'{1}'/$mrate}
		time mpirun -n 4 ./traveller.exe $cityfile | tee $output2
		mrate=$(expr $mrate + 25)
	done
done
