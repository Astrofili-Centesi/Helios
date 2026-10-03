#!/bin/bash 
# Meglio installare una ramdisk sudo mount -t tmpfs -o size=100M tmpfs /home/thomas/Scrivania/ramdisk/

# carica il file di configurazione
source /home/helios/helios/helios.cfg

if [ $keyon -eq 1 ]
then
	# legge la data
	dt="$(date -u -Is)"

	#controllo amplificatore
	pacmd set-source-port 1 analog-input-linein
	pacmd set-source-volume 1 ${volacq}
	
   # acquisizione segnale 
   rec -r192k -c 2 $ramdisk_path/input.wav trim 1 $lenacq
   sox $ramdisk_path/input.wav $ramdisk_path/l.wav remix 1
   sox $ramdisk_path/input.wav $ramdisk_path/r.wav remix 2
   sox -m -v 1 $ramdisk_path/l.wav -v -1 $ramdisk_path/r.wav $ramdisk_path/input.wav
   
   #RMS del segnale
   
   printf "$dt" >> ${work_path}/db_rms.csv
   sox $ramdisk_path/input.wav -n stats 2> $ramdisk_path/app.txt
   dvrms="$(sed -n 6p ${ramdisk_path}/app.txt | cut -c 15-20)"
   printf ",$dvrms\n" >> ${work_path}/db_rms.csv
   
	# filtraggio e misura rms dei canali e registrazione su db
	printf "$dt" >> ${work_path}/db.csv
	for (( i=0; i<${#freq[@]}; i++))
	do
	   sox $ramdisk_path/input.wav $ramdisk_path/input1.wav bandpass ${freq[$i]} ${lb[$i]}
	   sox -v ${gain[$i]} $ramdisk_path/input1.wav -n bandpass ${freq[$i]} ${lb[$i]} stats 2> $ramdisk_path/app.txt
	  	   
	   # lettura canale orrizontale in dB
	   dva="$(sed -n 5p ${ramdisk_path}/app.txt | cut -c 15-20)"
	  	
	   # lettura canale verticale in dB
	   # dvb="$(sed -n 6p ${ramdisk_path}/app.txt | cut -c 35-40)"
	   
	   
	   # calcola il valore lineare di dva e dvb
	   # sa=$(echo "e($dva/8.6858896)" | bc -l)
	   # sb=$(echo "e($dvb/8.6858896)" | bc -l)
	   
	   
	   # calcolo magnitudine
	   # dvmag=$(echo "(l(sqrt($sa^2+$sb^2))/l(10)*20)" | bc -l | awk '{printf("%.2f",$1)}')
	   
	   # calcolo fase
	   # dvfas=$(echo "(a($sa/$sb)*57.3)" | bc -l | awk '{printf("%.2f",$1)}') 
	   
	   # prova canali
	   # dvmag=$dva
	   # dvfas=$dvb  
	   
	   printf ",$dva" >> ${work_path}/db.csv
	   # printf ",$dvfas" >> ${work_path}/db.csv
	   
	done
	printf "\n" >> ${work_path}/db.csv
	
	sox $ramdisk_path/input.wav -n spectrogram -o $ramdisk_path/spectrogram.png -Y2000 -m -h -t "Astrofili Centesi - Helios VLF" -c "$(date)"
		
	#esegue il git ai 00 e ai 30 di ogni ora
	if [ $(date +%M) -eq 00 ] || [ $(date +%M) -eq 30 ]
	then 
	   #creazione spettrogramma ricordarsi 
       sox $ramdisk_path/input.wav -n spectrogram -o $ramdisk_path/spectrogram.png -Y2000 -m -h -t "Astrofili Centesi - Helios VLF" -c "$(date)"
	   #git
	   cd $work_path/Helios
	   git reset --hard HEAD
	   git clean -fxd
	   git pull --rebase
	   
	   cp ../db.csv .
	   cp ../freq.csv .
	   cp ../db_rms.csv .
	   cp $ramdisk_path/spectrogram.png .
	   
	   git add db.csv
	   git add freq.csv
	   git add db_rms.csv
	   
	   #git add spectrogram.png
	   git commit -m "Update $(date -Is)"
	   git push
	   cd ..
	fi
fi





