#!/bin/bash

outputfmt='pop_{1}-seed_{2}.route'
cityfile='compare_pop.cities'

for seed in $(seq 1 1); do
	sed -i 's/^.* # seed/'$seed' # seed/g' $cityfile
 	output1=${outputfmt/'{2}'/$seed}
	pop=500
	for i in $(seq 1 21); do
		echo 'Now running seed='$seed' , pop='$pop
		sed -i 's/^.* # pop/'$pop' # pop/g' $cityfile
		output2=${output1/'{1}'/$pop}
		time mpirun -n 4 ./traveller.exe $cityfile | tee $output2
		pop=$(expr $pop + 100)
	done
done
