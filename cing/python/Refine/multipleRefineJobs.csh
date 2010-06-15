#!/bin/tcsh

set stage = r1
set x = 1brv
set ranges = '171-189'

@ jobCountMax = 2
@ modelCountMax = 20
@ modelsPerJob = $modelCountMax / $jobCountMax
@ jobCount = 0 # default is zero
while ( $jobCount < $jobCountMax )
	@ modelCountStart = $jobCount * $modelsPerJob
	@ modelCountEnd = $modelCountStart + $modelsPerJob - 1
	refine --project $x --name $stage --refine --models $modelCountStart"-"$modelCountEnd >& job$count.log &
	@ jobCount = $jobCount + 1
end

