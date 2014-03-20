#!/bin/bash

outputfmt='ntasks_{1}-seed_{2}.route'

nmult=2
nmax=3
stepdiv=1
popdiv=1
for seed in $(seq 1 10); do
	sed -i 's/^.* # seed/'$seed' # seed/g' compare_ntasks.cities
	output1=${outputfmt/'{2}'/$seed}
	pop=1000
	steps=100000
	ntasks=1
	for i in $(seq 1 $nmax); do
		sed -i 's/^.* # pop/'$pop' # pop/g' compare_ntasks.cities
		sed -i 's/^.* # steps/'$steps' # steps/g' compare_ntasks.cities
		echo 'Now running seed='$seed' , ntasks='$ntasks' , pop='$pop' , steps='$steps
		output2=${output1/'{1}'/$ntasks}
		#mpirun -n $ntasks ./traveller.exe compare_ntasks.cities | tee $output2
		ntasks=$(expr $ntasks \* $nmult)
		steps=$(expr $steps / $stepdiv)
		pop=$(expr $pop / $popdiv)
	done
done
