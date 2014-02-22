for y in $(seq 2008 2012)
do
	for m in January February March April May June July August September October November December
	do
		wget "http://mailman.nanog.org/pipermail/nanog/"$y"-"$m".txt"
	done
done
